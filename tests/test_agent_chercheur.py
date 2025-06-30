import unittest
from unittest.mock import patch

from nina_project.agents.agent_chercheur import AgentChercheur


class TestAgentChercheurWeb(unittest.TestCase):
    @patch("nina_project.agents.agent_chercheur.requests.get")
    def test_collect_from_web(self, mock_get):
        # Prépare une fausse page DuckDuckGo minimaliste
        html = """
        <html><body>
          <a class='result__a'>Résultat 1</a>
          <a class='result__a'>Résultat 2</a>
          <a class='result__a'>Résultat 3</a>
        </body></html>
        """
        mock_resp = mock_get.return_value
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status.return_value = None

        agent = AgentChercheur()
        results = agent.collect_from_web("chatgpt")
        self.assertEqual(results[:3], ["Résultat 1", "Résultat 2", "Résultat 3"])


if __name__ == "__main__":
    unittest.main() 