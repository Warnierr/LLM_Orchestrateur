import unittest
from nina_project.agents.agent_planificateur import AgentObjectif

class TestAgentObjectif(unittest.TestCase):
    def test_planification(self):
        agent = AgentObjectif("Optimiser la productivité")
        agent.planifier()
        # Ajoutez des assertions pertinentes ici

if __name__ == "__main__":
    unittest.main() 