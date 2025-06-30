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
import uuid
from typing import List, Optional
import os

from tools.sql_db import Fact

# -----------------------------------------------------------------------------
# Import sécurisé de Qdrant ; si la lib n'est pas dispo (ex. CI minimal),
# on fournit un mock simplifié pour permettre aux tests de tourner sans erreur.
# -----------------------------------------------------------------------------
try:
    from qdrant_client import QdrantClient, models as rest
except ImportError:
    class _MockPoint:
        def __init__(self, id, payload): self.id, self.payload = id, payload
    class _MockCollection:
        def __init__(self): self.storage = {}
        def upsert(self, points):
            for p in points: self.storage[p.id] = p
        def search(self, query_vector, limit): return list(self.storage.values())[:limit]
    class QdrantClient:
        def __init__(self, *args, **kwargs): self.collections = {}
        def get_collections(self): return type("o", (), {"collections": [type("c", (), {"name": n}) for n in self.collections]})()
        def recreate_collection(self, collection_name, vectors_config): self.collections[collection_name] = _MockCollection()
        def upsert(self, collection_name, points): self.collections[collection_name].upsert(points)
        def search(self, collection_name, query_vector, limit): return self.collections[collection_name].search(query_vector, limit)
    class rest:
        VectorParams = type("VectorParams", (), {"__init__": lambda s, size, distance: None})
        Distance = type("Distance", (), {"COSINE": "Cosine"})
        PointStruct = type("PointStruct", (), {"__init__": lambda s, id, vector, payload: setattr(s, "id", id) or setattr(s, "vector", vector) or setattr(s, "payload", payload)})


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
        ints = [int.from_bytes(digest[i : i + 4], "little") for i in range(0, len(digest), 4)]
        return [val / 2**32 for val in ints]


class VectorDB:
    def __init__(self, collection: str = "nina_vectors", dim: int = SimpleEmbedder.dim):
        self.collection = collection
        self.dim = dim
        # Stockage local des documents pour fallback substring search
        self._docs: List[str] = []
        self._metadatas: List[Optional[dict]] = []
        # Connexion à Qdrant persistant si configuré
        qdrant_url = os.getenv("QDRANT_URL")
        self.client = QdrantClient(url=qdrant_url) if qdrant_url else QdrantClient(":memory:")
        # Crée la collection si elle n'existe pas
        # Récupère la liste des collections Qdrant de façon sécurisée
        collections = getattr(self.client.get_collections(), "collections", [])
        existing_names = [c.name for c in collections]
        if self.collection not in existing_names:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=rest.VectorParams(size=dim, distance=rest.Distance.COSINE),
            )

    def add_fact(self, fact: Fact):
        """Vectorise et ajoute un fait à Qdrant."""
        if not fact or not isinstance(fact.content, str):
            return

        metadata = {
            "fact_id": fact.id,
            "source": fact.source,
            "timestamp": fact.timestamp.isoformat() if fact.timestamp else None,
        }
        vector = SimpleEmbedder.embed(fact.content)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"fact_{fact.id}"))
        point = rest.PointStruct(
            id=point_id, vector=vector, payload={"text": fact.content, "meta": metadata}
        )
        self.client.upsert(collection_name=self.collection, points=[point])

    # ------------------------------------------------------------------
    # API documents
    # ------------------------------------------------------------------
    def add_documents(self, docs: List[str], metadata_list: Optional[List[Optional[dict]]] = None):
        """Indexe une liste de documents.

        Args:
            docs: textes à indexer
            metadata_list: liste de dicts de même longueur que docs (ou None) contenant
                des méta‐données (ex. timestamp, url, source). Elles seront stockées
                dans le payload sous la clé "meta".
        """
        if not docs:
            return
        
        metadata_list = metadata_list or ([None] * len(docs))
        self._docs.extend(docs)
        self._metadatas.extend(metadata_list)
        
        points = []
        for text, meta in zip(docs, metadata_list):
            vector = SimpleEmbedder.embed(text)
            payload = {"text": text, "meta": meta} if meta else {"text": text}
            points.append(rest.PointStruct(id=uuid.uuid4().hex, vector=vector, payload=payload))
        
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def similarity_search(self, query: str, top_k: int = 3) -> List[dict]:
        """Retourne `top_k` documents (texte + meta) les plus proches."""
        query_vector = SimpleEmbedder.embed(query)
        hits = self.client.search(collection_name=self.collection, query_vector=query_vector, limit=top_k)
        return [{"text": h.payload.get("text", ""), "meta": h.payload.get("meta", {})} for h in hits]