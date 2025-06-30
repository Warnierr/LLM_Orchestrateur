# agent_chercheur.py

import requests
from bs4 import BeautifulSoup
from typing import List

class AgentChercheur:
    def __init__(self):
        pass

    def collect_data(self, source_type, query):
        if source_type == 'web':
            return self.collect_from_web(query)
        elif source_type == 'api':
            return self.collect_from_api(query)
        elif source_type == 'document':
            return self.collect_from_document(query)
        else:
            raise ValueError("Type de source non supporté")

    def collect_from_web(self, query: str) -> List[str]:
        """Collecte via DuckDuckGo Instant Answer API (JSON) avec fallback HTML."""
        print(f"Collecte DuckDuckGo Instant Answer pour : {query}")
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NinaBot/0.1)"}
        # 1) Instant Answer API
        try:
            params = {"q": query, "format": "json", "no_html": "1", "lang": "fr"}
            resp = requests.get("https://api.duckduckgo.com/", params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Vérifier que c'est un dict JSON
            if not isinstance(data, dict):
                raise ValueError("Non JSON response")
            results = []
            # Abstract
            abstract = data.get("AbstractText")
            if abstract:
                results.append(abstract)
            # Related topics
            for topic in data.get("RelatedTopics", [])[:5]:
                text = topic.get("Text") or topic.get("Name")
                if text:
                    results.append(text)
            if results:
                return results[:5]
        except Exception as exc:
            print(f"[AgentChercheur] Erreur Instant Answer: {exc}")
        # 2) Fallback scraping HTML
        print(f"[AgentChercheur] Fallback scraping HTML pour : {query}")
        try:
            params = {"q": query, "kl": "fr-fr"}
            resp = requests.get("https://duckduckgo.com/html/", params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            results = [a.get_text(strip=True) for a in soup.select("a.result__a")[:5]]
            return results
        except Exception as exc:
            print(f"[AgentChercheur] Erreur scraping DuckDuckGo HTML: {exc}")
            return []

    def collect_from_api(self, query):
        # Implémenter la logique de collecte de données via API
        print(f"Collecte de données API pour la requête : {query}")
        try:
            params = {"q": query, "format": "json", "no_html": "1", "lang": "fr"}
            headers = {"User-Agent": "Mozilla/5.0 (compatible; NinaBot/0.1)"}
            resp = requests.get("https://api.duckduckgo.com/", params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Vérifier que la réponse est bien un dict JSON
            if not isinstance(data, dict):
                raise ValueError("Non JSON response")
            results = []
            abstract = data.get("AbstractText")
            for result in data.get("Results", []):
                results.append(result.get("Text"))
            return results
        except Exception as exc:
            print(f"[AgentChercheur] Erreur lors de la requête API : {exc}")
            return []

    def collect_from_document(self, query):
        # Implémenter la logique de collecte de données à partir de documents
        print(f"Collecte de données document pour la requête : {query}")
        return [] 