"""AgentNews – récupère les dernières actualités IA.

Stratégie :
1. Si la variable d'env NEWSAPI_KEY est définie → appeler NewsAPI.org.
2. Sinon → fallback scraping DuckDuckGo news.

Retour : liste de dicts {title, url, published, source}
"""
from __future__ import annotations

import os
import requests
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup


class AgentNews:
    def __init__(self):
        self.news_key = os.getenv("NEWSAPI_KEY")
        self.session = requests.Session()

    # ------------------------------------------------------------------
    def fetch_ai_news(self, max_items: int = 5) -> List[Dict]:
        if self.news_key:
            return self._fetch_newsapi(max_items)
        return self._scrape_duckduckgo(max_items)

    # ------------------------------------------------------------------
    def _fetch_newsapi(self, max_items: int) -> List[Dict]:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "artificial intelligence",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": max_items,
            "apiKey": self.news_key,
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            articles = []
            for art in data.get("articles", [])[:max_items]:
                articles.append({
                    "title": art["title"],
                    "url": art["url"],
                    "published": art["publishedAt"],
                    "source": art["source"]["name"],
                })
            return articles
        except Exception as exc:
            print(f"[AgentNews] Erreur NewsAPI: {exc}")
            return []

    def _scrape_duckduckgo(self, max_items: int) -> List[Dict]:
        params = {"q": "intelligence artificielle actualités", "kl": "fr-fr"}
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NinaBot/0.1)"}
        try:
            resp = self.session.get("https://duckduckgo.com/html/", params=params, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[AgentNews] Erreur DuckDuckGo: {exc}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for a in soup.select("a.result__a")[:max_items]:
            title = a.get_text(strip=True)
            url = a["href"]
            results.append({
                "title": title,
                "url": url,
                "published": datetime.utcnow().isoformat(),
                "source": "DuckDuckGo",
            })
        return results 