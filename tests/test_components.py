import unittest
from nina_project.agents.agent_analyste import AgentAnalyste, AgentApprentissage  # type: ignore
from nina_project.tools.vector_db import VectorDB  # type: ignore
from nina_project.agents.agent_nina import AgentNina, TaskType  # type: ignore

class DummyLLM:
    def chat(self, messages):
        return "DUMMY_RESPONSE"

class TestAnalyste(unittest.TestCase):
    def test_extract_insights(self):
        agent = AgentAnalyste()
        data = ["a", "b", "c"]
        insights = agent.analyze_data(data)
        self.assertEqual(insights, {"nombre_elements": 3})

class TestApprentissage(unittest.TestCase):
    def test_apprendre_and_recommander(self):
        agent = AgentApprentissage()
        # Au départ, pas de recommandations
        self.assertEqual(agent.recommander(), [])
        # Apprentissage de données
        agent.apprendre(["x", "y", "x"])
        rec1 = agent.recommander(top_k=1)
        self.assertEqual(rec1, ["x"])
        rec2 = agent.recommander(top_k=2)
        self.assertIn("y", rec2)
        self.assertIn("x", rec2)

class TestVectorDB(unittest.TestCase):
    def setUp(self):
        # Utiliser une collection dédiée pour le test
        self.db = VectorDB(collection="test_components")

    def test_add_and_search(self):
        docs = ["hello world", "foo bar", "hello foo"]
        metas = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.db.add_documents(docs, metas)
        results = self.db.similarity_search("hello", top_k=2)
        self.assertEqual(len(results), 2)
        texts = [r["text"] for r in results]
        # Au moins un résultat contient 'hello'
        self.assertTrue(any("hello" in t for t in texts))

class TestAgentNinaExtra(unittest.TestCase):
    def setUp(self):
        self.agent = AgentNina()

    def test_analyze_request_conversation(self):
        # Message simple sans mot-clé de recherche pour classification 'conversation'
        plan = self.agent.analyze_request("Salut Nina")
        self.assertEqual(plan.task_type, TaskType.CONVERSATION)

    def test_think_and_respond_report(self):
        # Désactiver le LLM local pour forcer le pipeline de rapport
        self.agent.local_llm = None
        response = self.agent.think_and_respond("test recherche IA")
        self.assertIsInstance(response, str)
        self.assertIn("Rapport d'Analyse", response)
        self.assertIn("nombre_elements", response)

    def test_think_and_respond_conversation_with_local(self):
        # Stubber le LLM local pour conversation
        self.agent.local_llm = DummyLLM()
        response = self.agent.think_and_respond("Bonjour Nina")
        self.assertEqual(response, "DUMMY_RESPONSE")

if __name__ == '__main__':
    unittest.main() 