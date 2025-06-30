import unittest

from nina_project.tools.vector_db import VectorDB


class TestVectorDB(unittest.TestCase):
    def test_add_and_search(self):
        db = VectorDB(collection="test_vectors")
        docs = ["Python est un langage", "La Terre est ronde", "ChatGPT est un LLM"]
        db.add_documents(docs)
        res = db.similarity_search("langage", top_k=2)
        # On vérifie que la recherche renvoie des dicts avec clés 'text' et 'meta'.
        self.assertTrue(len(res) > 0)
        for item in res:
            self.assertIsInstance(item, dict)
            self.assertIn('text', item)
            self.assertIn('meta', item)


if __name__ == "__main__":
    unittest.main() 