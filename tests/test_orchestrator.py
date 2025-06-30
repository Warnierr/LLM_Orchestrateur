import unittest

from nina_project.app.orchestrator import Orchestrator


class TestOrchestrator(unittest.TestCase):
    def test_orchestration_pipeline(self):
        orchestrator = Orchestrator()
        resultat = orchestrator.orchestrate("test recherche IA")
        # Le rapport généré doit être une chaîne non vide contenant des sections clés.
        self.assertIsInstance(resultat, str)
        self.assertIn("Rapport d'Analyse", resultat)
        self.assertIn("nombre_elements", resultat)
        # Nina peut retourner des passages_similaires (mémoire) ou des news (données fraîches)
        self.assertTrue(
            "passages_similaires" in resultat or "news" in resultat,
            "La réponse doit contenir 'passages_similaires' ou 'news'",
        )


if __name__ == "__main__":
    unittest.main() 