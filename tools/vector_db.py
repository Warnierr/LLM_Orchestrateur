"""vector_db.py – Interface minimale autour de Qdrant pour Nina.

Objectifs :
1. Stocker les textes (chunks) sous forme de vecteurs.
2. Retrouver les passages les plus similaires à une requête.

Pour simplifier l'embarqué/offline, nous utilisons le moteur in-memory de Qdrant
(`QdrantClient(" :memory: ")`) et un *embedding* maison déterministe afin
d'éviter le téléchargement de modèles lourds.
"""
from __future__ import annotations

import hashlib
import itertools
import uuid
from typing import List
import os

# -----------------------------------------------------------------------------
# Import sécurisé de Qdrant ; si la lib n'est pas dispo (ex. CI minimal),
# on fournit un mock simplifié pour permettre aux tests de tourner sans erreur.
# -----------------------------------------------------------------------------
try:
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.http import models as rest  # type: ignore

    _QDRANT_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover – fallback
    _QDRANT_AVAILABLE = False

    class _MockPoint:  # minimal structure
        def __init__(self, payload):
            self.payload = payload

    class _MockCollection:
        def __init__(self):
            self.storage = []

        def upsert(self, points):
            self.storage.extend(points)

        def search(self, query_vector, limit):
            # Retourne simplement les premiers éléments
            return self.storage[:limit]

    class QdrantClient:  # type: ignore
        def __init__(self, *_, **__):
            self.collections = {}

        def get_collections(self):
            return type("obj", (), {"collections": [type("c", (), {"name": n}) for n in self.collections]})()

        def recreate_collection(self, collection_name, vectors_config):
            self.collections[collection_name] = _MockCollection()

        def upsert(self, collection_name, points):
            self.collections[collection_name].upsert(points)

        def search(self, collection_name, query_vector, limit):
            return self.collections[collection_name].search(query_vector, limit)

    class rest:  # type: ignore
        class VectorParams:
            def __init__(self, size, distance):
                self.size = size
                self.distance = distance

        class Distance:
            COSINE = "Cosine"

        class PointStruct:
            def __init__(self, id, vector, payload):
                self.payload = payload


class SimpleEmbedder:
    """Génère un vecteur de dimension 8 à partir d'un texte.

    Méthode : SHA-256 → 32 octets, regroupés par 4 pour former 8 entiers, puis
    normalisés dans \[0,1]. Ce n'est pas sémantique mais suffisant pour un POC
    hors-ligne et des tests unitaires.
    """

    dim = 8

    @classmethod
    def embed(cls, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()[: cls.dim * 4]
        # Convert 4-byte chunks to int
        ints = [int.from_bytes(digest[i : i + 4], "little", signed=False) for i in range(0, len(digest), 4)]
        # Normalise
        return [val / 2**32 for val in ints]


class VectorDB:
    def __init__(self, collection: str = "nina_vectors", dim: int = SimpleEmbedder.dim):
        self.collection = collection
        self.dim = dim
        # Stockage local des documents pour fallback substring search
        self._docs: List[str] = []
        self._metadatas: List[dict | None] = []
        # Connexion à Qdrant persistant si configuré
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        if qdrant_url:
            # Connexion à une instance Qdrant distante ou locale
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            # Instance Qdrant en mémoire (mode POC)
            self.client = QdrantClient(":memory:")
        # Crée la collection si elle n'existe pas
        # Récupère la liste des collections Qdrant de façon sécurisée
        collections_list = getattr(self.client.get_collections(), "collections", [])
        existing_names = [getattr(c, "name", None) for c in collections_list]
        if self.collection not in existing_names:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=rest.VectorParams(size=dim, distance=rest.Distance.COSINE),
            )

    # ------------------------------------------------------------------
    # API documents
    # ------------------------------------------------------------------
    def add_documents(self, docs: List[str], metadata_list: List[dict | None] | None = None):
        """Indexe une liste de documents.

        Args:
            docs: textes à indexer
            metadata_list: liste de dicts de même longueur que docs (ou None) contenant
                des méta‐données (ex. timestamp, url, source). Elles seront stockées
                dans le payload sous la clé "meta".
        """
        if not docs:
            return
        # Listes de métadonnées (None autorisé)
        metadata_list = metadata_list or [None] * len(docs)
        vectors = [SimpleEmbedder.embed(t) for t in docs]
        points = []
        # Enregistrer en local pour fallback
        self._docs.extend(docs)
        self._metadatas.extend(metadata_list)
        for v, t, meta in zip(vectors, docs, metadata_list):
            payload = {"text": t}
            if meta:
                payload["meta"] = meta
            points.append(rest.PointStruct(id=uuid.uuid4().hex, vector=v, payload=payload))
        self.client.upsert(collection_name=self.collection, points=points)

    def similarity_search(self, query: str, top_k: int = 3) -> List[dict]:
        """Retourne `top_k` documents (texte + meta) les plus proches."""
        # Fallback substring search si QDRANT_URL non défini (tests)
        if not os.getenv("QDRANT_URL"):
            matches = []
            for doc, meta in zip(self._docs, self._metadatas):
                if query.lower() in doc.lower():
                    matches.append({"text": doc, "meta": meta or {}})
                    if len(matches) >= top_k:
                        break
            return matches
        # Recherche vectorielle via Qdrant
        query_vector = SimpleEmbedder.embed(query)
        hits = self.client.search(collection_name=self.collection, query_vector=query_vector, limit=top_k)
        results = []
        for h in hits:
            results.append({
                "text": h.payload.get("text", ""),
                "meta": h.payload.get("meta", {}),
            })
        # Si aucun des résultats ne contient la chaîne de requête, on retombe sur une recherche par substring
        if not any(query.lower() in r["text"].lower() for r in results):
            matches = []
            for doc, meta in zip(self._docs, self._metadatas):
                if query.lower() in doc.lower():
                    matches.append({"text": doc, "meta": meta or {}})
                    if len(matches) >= top_k:
                        break
            return matches
        return results

    def store_vectors(self, vectors, collection_name):
        # Implémenter la logique de stockage de vecteurs
        print(f"Stockage des vecteurs dans la collection {collection_name}...")
        self.client.upload_collection(collection_name=collection_name, vectors=vectors)

    def search_vectors(self, query_vector, collection_name, top_k=5):
        # Implémenter la logique de recherche de vecteurs
        print(f"Recherche des vecteurs similaires dans la collection {collection_name}...")
        return self.client.search(collection_name=collection_name, query_vector=query_vector, top=top_k) 