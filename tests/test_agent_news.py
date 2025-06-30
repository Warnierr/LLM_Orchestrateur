import unittest
from unittest.mock import patch, MagicMock
from nina_project.agents.agent_news import AgentNews

class TestAgentNews(unittest.TestCase):
    @patch('nina_project.agents.agent_news.requests.Session.get')
    def test_fetch_with_newsapi(self, mock_get):
        # Simuler NEWSAPI_KEY
        with patch.dict('os.environ', {'NEWSAPI_KEY': 'fakekey'}):
            # Préparer la réponse JSON
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {
                'articles': [
                    {
                        'title': 'Titre Test',
                        'url': 'http://example.com',
                        'publishedAt': '2025-01-01T00:00:00Z',
                        'source': {'name': 'ExempleSource'}
                    }
                ]
            }
            mock_get.return_value = mock_resp

            agent = AgentNews()
            items = agent.fetch_ai_news(max_items=1)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]['title'], 'Titre Test')
            self.assertEqual(items[0]['url'], 'http://example.com')
            self.assertEqual(items[0]['source'], 'ExempleSource')

    @patch('nina_project.agents.agent_news.requests.Session.get')
    def test_fetch_with_scraping(self, mock_get):
        # Sans NEWSAPI_KEY => scrap
        with patch.dict('os.environ', {}, clear=True):
            html = """
            <html><body>
              <a class='result__a' href='http://a'>Article A</a>
              <a class='result__a' href='http://b'>Article B</a>
            </body></html>
            """
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.text = html
            mock_get.return_value = mock_resp

            agent = AgentNews()
            items = agent.fetch_ai_news(max_items=2)
            self.assertEqual(len(items), 2)
            self.assertTrue(all('title' in it and 'url' in it for it in items))

if __name__ == '__main__':
    unittest.main() 