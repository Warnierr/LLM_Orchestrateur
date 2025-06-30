import unittest
from nina_project.agents.agent_nina import AgentNina, TaskType  # type: ignore

class TestAgentNina(unittest.TestCase):
    def setUp(self):
        self.agent = AgentNina()

    def test_analyze_request_recherche(self):
        plan = self.agent.analyze_request("Donne-moi des informations sur ChatGPT")
        self.assertEqual(plan.task_type, TaskType.RECHERCHE)
        self.assertIn("chercheur", plan.agents_needed)
        self.assertTrue(plan.estimated_time > 0)
        self.assertIsInstance(plan.reasoning, str)

    def test_think_and_respond_returns_report(self):
        response = self.agent.think_and_respond("test recherche IA")
        self.assertIsInstance(response, str)
        self.assertIn("Rapport d'Analyse", response)
        self.assertIn("nombre_elements", response)
        self.assertTrue("passages_similaires" in response or "news" in response)

if __name__ == "__main__":
    unittest.main() 