"""
router.py — Roteador por keywords/intent para selecionar o agente correto.
"""

from typing import Optional
from .agent import Agent


class Router:
    """
    Analisa o input do usuário e decide qual agente deve responder.
    Usa mapeamento de keywords por agente; o agente default é acionado
    quando nenhuma keyword é encontrada.
    """

    def __init__(self, agents: list[Agent], default_agent: Optional[Agent] = None):
        """
        Args:
            agents: Lista de agentes disponíveis
            default_agent: Agente usado quando nenhuma keyword corresponde.
                           Se None, usa o primeiro agente da lista.
        """
        if not agents:
            raise ValueError("Router requires at least one agent")

        self.agents: dict[str, Agent] = {a.name: a for a in agents}
        self.default_agent = default_agent or agents[0]
        self._keyword_map: dict[str, list[str]] = {}

    def register_keywords(self, agent_name: str, keywords: list[str]) -> None:
        """
        Registra keywords associadas a um agente.

        Args:
            agent_name: Nome do agente (deve existir na lista)
            keywords: Lista de palavras-chave em minúsculo
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Available: {list(self.agents.keys())}")
        self._keyword_map[agent_name] = [kw.lower() for kw in keywords]

    def route(self, user_input: str) -> Agent:
        """
        Analisa o input e retorna o agente mais adequado.

        Args:
            user_input: Texto enviado pelo usuário

        Returns:
            Agent selecionado
        """
        normalized = user_input.lower()

        # Conta matches por agente e seleciona o com mais correspondências
        scores: dict[str, int] = {}
        for agent_name, keywords in self._keyword_map.items():
            score = sum(1 for kw in keywords if kw in normalized)
            if score > 0:
                scores[agent_name] = score

        if not scores:
            return self.default_agent

        best_agent_name = max(scores, key=lambda k: scores[k])
        return self.agents[best_agent_name]

    def list_agents(self) -> list[str]:
        """Retorna nomes de todos os agentes registrados."""
        return list(self.agents.keys())

    def __repr__(self) -> str:
        return f"Router(agents={self.list_agents()}, default={self.default_agent.name!r})"
