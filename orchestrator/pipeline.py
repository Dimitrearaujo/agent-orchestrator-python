"""
pipeline.py — Orquestrador do fluxo completo multi-agente.
"""

import uuid
from typing import Optional

from .agent import Agent
from .memory import SessionMemory
from .router import Router
from .handoff import HandoffManager
from .hitl import HITLChecker


class Pipeline:
    """
    Orquestra o fluxo completo:
      input → router → agente → memória → handoff (se necessário) → HITL → output
    """

    def __init__(
        self,
        router: Router,
        memory: SessionMemory,
        handoff_manager: HandoffManager,
        hitl_checker: HITLChecker,
        handoff_threshold: float = 0.5,
    ):
        """
        Args:
            router: Roteador de agentes
            memory: Memória de sessão
            handoff_manager: Gerenciador de handoffs
            hitl_checker: Verificador Human-in-the-Loop
            handoff_threshold: Confiança mínima para evitar handoff automático
        """
        self.router = router
        self.memory = memory
        self.handoff_manager = handoff_manager
        self.hitl_checker = hitl_checker
        self.handoff_threshold = handoff_threshold

    def run(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        force_agent: Optional[str] = None,
    ) -> dict:
        """
        Executa o pipeline completo para um input do usuário.

        Args:
            user_input: Mensagem do usuário
            session_id: ID da sessão (cria nova se None)
            force_agent: Nome do agente a forçar (ignora o router)

        Returns:
            dict com:
                - session_id (str)
                - agent_used (str)
                - response (str)
                - confidence (float)
                - hitl_required (bool)
                - hitl_reason (str)
                - handoff_occurred (bool)
                - handoff_log (list)
        """
        # 1. Garante sessão
        if not session_id:
            session_id = str(uuid.uuid4())
        self.memory.create_session(session_id)

        # 2. Adiciona input à memória
        self.memory.add(session_id, "user", user_input)

        # 3. Roteamento
        if force_agent and force_agent in self.router.agents:
            selected_agent: Agent = self.router.agents[force_agent]
        else:
            selected_agent = self.router.route(user_input)

        # 4. Executa agente com contexto da sessão
        context = self.memory.get(session_id)
        result = selected_agent.run(user_input, context=context)
        response: str = result["response"]
        confidence: float = result["confidence"]

        # 5. Handoff automático se confiança for muito baixa
        handoff_occurred = False
        if confidence < self.handoff_threshold:
            # Tenta agente default como fallback
            fallback = self.router.default_agent
            if fallback.name != selected_agent.name:
                self.handoff_manager.transfer(
                    from_agent=selected_agent,
                    to_agent=fallback,
                    session_id=session_id,
                    reason=f"Confiança {confidence:.2f} abaixo do handoff_threshold {self.handoff_threshold:.2f}",
                )
                context = self.memory.get(session_id)
                result = fallback.run(user_input, context=context)
                response = result["response"]
                confidence = result["confidence"]
                selected_agent = fallback
                handoff_occurred = True

        # 6. Adiciona resposta à memória
        self.memory.add(session_id, "assistant", response)

        # 7. Verificação HITL
        hitl_result = self.hitl_checker.check(
            response=response,
            confidence=confidence,
            user_input=user_input,
        )

        return {
            "session_id": session_id,
            "agent_used": selected_agent.name,
            "response": response,
            "confidence": confidence,
            "hitl_required": hitl_result["hitl_required"],
            "hitl_reason": hitl_result["reason"],
            "handoff_occurred": handoff_occurred,
            "handoff_log": self.handoff_manager.get_log(),
        }

    def __repr__(self) -> str:
        return (
            f"Pipeline(agents={self.router.list_agents()}, "
            f"handoff_threshold={self.handoff_threshold})"
        )
