import unittest
from nina_project.agents.agent_analyste import AgentApprentissage

class TestAgentApprentissage(unittest.TestCase):
    def test_apprentissage(self):
        agent = AgentApprentissage()
        agent.apprendre(["donnée1", "donnée2"])
        recommandations = agent.recommander()
        self.assertIsNotNone(recommandations)

if __name__ == "__main__":
    unittest.main() 