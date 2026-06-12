"""
main.py — Demo com 3 agentes: vendas, suporte e financeiro.

Execução:
    py main.py

Para integrar com Claude API real, configure ANTHROPIC_API_KEY no .env
e substitua o método run() mock em orchestrator/agent.py pela chamada real.
"""

import os
from dotenv import load_dotenv

from orchestrator import (
    Agent,
    SessionMemory,
    Router,
    HandoffManager,
    HITLChecker,
    Pipeline,
)

load_dotenv()


def build_pipeline() -> Pipeline:
    """Constrói e retorna o pipeline configurado com 3 agentes."""

    # --- Agentes ---
    agente_vendas = Agent(
        name="vendas",
        role="vendedor especialista em soluções de IA para pequenos negócios",
        system_prompt=(
            "Você é Lucas, consultor de vendas da CD Tech. "
            "Apresente soluções de automação e agentes IA com entusiasmo. "
            "Foque em benefícios práticos para clínicas, academias e studios."
        ),
        confidence=0.92,
    )

    agente_suporte = Agent(
        name="suporte",
        role="suporte técnico para clientes da CD Tech",
        system_prompt=(
            "Você é o suporte técnico da CD Tech. "
            "Ajude a resolver problemas técnicos com calma e clareza. "
            "Se não souber a resposta, escalone para um especialista humano."
        ),
        confidence=0.85,
    )

    agente_financeiro = Agent(
        name="financeiro",
        role="consultor financeiro para orçamentos e pagamentos",
        system_prompt=(
            "Você cuida do setor financeiro da CD Tech. "
            "Trate de preços, planos, pagamentos e notas fiscais. "
            "Seja transparente e profissional."
        ),
        confidence=0.88,
    )

    # --- Roteador ---
    router = Router(
        agents=[agente_vendas, agente_suporte, agente_financeiro],
        default_agent=agente_suporte,
    )
    router.register_keywords("vendas", [
        "preço", "plano", "contratar", "comprar", "demonstração", "demo",
        "quero", "interesse", "automação", "agente ia", "quanto custa",
    ])
    router.register_keywords("suporte", [
        "erro", "bug", "problema", "não funciona", "falha", "travou",
        "ajuda técnica", "suporte", "configuração",
    ])
    router.register_keywords("financeiro", [
        "boleto", "pagamento", "nota fiscal", "nf", "reembolso", "cobrança",
        "fatura", "assinatura", "cancelar", "upgrade",
    ])

    # --- Memória, Handoff e HITL ---
    memory = SessionMemory()
    handoff_manager = HandoffManager(memory)
    hitl_checker = HITLChecker(
        confidence_threshold=0.75,
        sensitive_keywords=["reembolso", "cancelar contrato", "processo judicial"],
    )

    # --- Pipeline ---
    pipeline = Pipeline(
        router=router,
        memory=memory,
        handoff_manager=handoff_manager,
        hitl_checker=hitl_checker,
        handoff_threshold=0.5,
    )

    return pipeline


def main():
    pipeline = build_pipeline()
    session_id = None

    print("\n" + "=" * 60)
    print("  CD Tech — Orquestrador Multi-Agente (Demo)")
    print("  Digite 'sair' para encerrar | 'nova sessão' para reiniciar")
    print("=" * 60 + "\n")

    # Demonstração automática com inputs pré-definidos
    demo_inputs = [
        "Quero saber o preço dos planos de automação",
        "Tenho um erro na integração com WhatsApp",
        "Preciso de uma nota fiscal do meu pagamento",
        "Quero cancelar contrato",  # Deve acionar HITL (keyword sensível)
    ]

    for user_input in demo_inputs:
        print(f"Usuario: {user_input}")
        result = pipeline.run(user_input, session_id=session_id)
        session_id = result["session_id"]

        print(f"Agente : [{result['agent_used'].upper()}] {result['response']}")
        print(f"Conf.  : {result['confidence']:.0%}  |  HITL: {result['hitl_required']} ({result['hitl_reason']})")
        if result["handoff_occurred"]:
            print("  >>> Handoff realizado para este agente")
        print()

    print("=" * 60)
    print(f"Session ID: {session_id}")
    print(f"Total de handoffs: {len(result['handoff_log'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
