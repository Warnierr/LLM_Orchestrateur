import pytest

from nina_project.agents.agent_llm_local import AgentLLMLocal


def test_agent_llm_local_initialization():
    # Test que l'agent peut être initialisé (utilise Ollama maintenant)
    agent = AgentLLMLocal()
    assert agent is not None
    # Vérifier que l'agent a bien les méthodes attendues
    assert hasattr(agent, 'generate')
    assert hasattr(agent, 'chat')

if __name__ == "__main__":
    pytest.main() 