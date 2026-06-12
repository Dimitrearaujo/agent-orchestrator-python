"""
handoff.py — Transferência de contexto entre agentes (handoff).
"""

from .agent import Agent
from .memory import SessionMemory


class HandoffManager:
    """
    Gerencia transferências entre agentes preservando o contexto da sessão.
    Quando um agente não consegue responder adequadamente, o HandoffManager
    transfere a conversa para outro agente com o histórico completo.
    """

    def __init__(self, memory: SessionMemory):
        self.memory = memory
        self._handoff_log: list[dict] = []

    def transfer(
        self,
        from_agent: Agent,
        to_agent: Agent,
        session_id: str,
        reason: str = "",
    ) -> dict:
        """
        Executa a transferência de contexto de um agente para outro.

        Args:
            from_agent: Agente que está transferindo
            to_agent: Agente que vai receber a conversa
            session_id: ID da sessão com o histórico
            reason: Motivo do handoff (para auditoria)

        Returns:
            dict com 'from_agent', 'to_agent', 'context_size' e 'reason'
        """
        context = self.memory.get(session_id)

        record = {
            "from_agent": from_agent.name,
            "to_agent": to_agent.name,
            "session_id": session_id,
            "context_size": len(context),
            "reason": reason or "Transferência automática",
        }
        self._handoff_log.append(record)

        # Adiciona nota de handoff na memória para o próximo agente saber
        handoff_note = (
            f"[HANDOFF] Transferido de '{from_agent.name}' para '{to_agent.name}'. "
            f"Motivo: {reason or 'não especificado'}. "
            f"Contexto: {len(context)} mensagens anteriores disponíveis."
        )
        self.memory.add(session_id, "system", handoff_note)

        return record

    def get_log(self) -> list[dict]:
        """Retorna o histórico completo de handoffs realizados."""
        return list(self._handoff_log)

    def clear_log(self) -> None:
        """Limpa o log de handoffs."""
        self._handoff_log = []

    def __repr__(self) -> str:
        return f"HandoffManager(handoffs_performed={len(self._handoff_log)})"
