from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

class AgentWikipedia:
    """Agent pour interroger Wikipedia via LangChain."""
    def __init__(self, lang: str = "fr", top_k: int = 3):
        # Initialise le wrapper Wikipedia
        self.wrapper = WikipediaAPIWrapper(lang=lang, top_k_results=top_k)  # type: ignore

    def search(self, query: str) -> str:
        """Recherche et renvoie un résumé consolidé des meilleurs résultats."""
        try:
            return self.wrapper.run(query)
        except Exception as e:
            # Fallback simplifié
            return f"Erreur Wikipedia: {e}" 