"""
memory.py — Memória de conversa por sessão (in-memory).
"""

import uuid
from typing import Optional


class SessionMemory:
    """
    Armazena o histórico de mensagens de cada sessão em um dicionário em memória.
    Cada sessão é identificada por um session_id único.
    """

    def __init__(self):
        self._sessions: dict[str, list[dict]] = {}

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Cria uma nova sessão e retorna o session_id."""
        sid = session_id or str(uuid.uuid4())
        if sid not in self._sessions:
            self._sessions[sid] = []
        return sid

    def add(self, session_id: str, role: str, content: str) -> None:
        """
        Adiciona uma mensagem ao histórico da sessão.

        Args:
            session_id: ID da sessão
            role: "user" | "assistant" | "system"
            content: Conteúdo da mensagem
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})

    def get(self, session_id: str) -> list[dict]:
        """Retorna o histórico completo de uma sessão."""
        return self._sessions.get(session_id, [])

    def clear(self, session_id: str) -> None:
        """Limpa o histórico de uma sessão específica."""
        if session_id in self._sessions:
            self._sessions[session_id] = []

    def delete_session(self, session_id: str) -> None:
        """Remove completamente uma sessão da memória."""
        self._sessions.pop(session_id, None)

    def session_exists(self, session_id: str) -> bool:
        """Verifica se uma sessão existe."""
        return session_id in self._sessions

    def list_sessions(self) -> list[str]:
        """Retorna lista de todos os session_ids ativos."""
        return list(self._sessions.keys())

    def __repr__(self) -> str:
        return f"SessionMemory(sessions={len(self._sessions)})"
