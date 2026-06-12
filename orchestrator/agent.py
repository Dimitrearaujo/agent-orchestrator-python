"""
agent.py — Classe base Agent para o orquestrador multi-agente.
"""

from typing import Optional


class Agent:
    """
    Classe base que representa um agente especializado.
    Em produção, o método run() pode chamar a API do Claude ou qualquer LLM.
    Neste projeto, retorna respostas mock para permitir testes sem API keys.
    """

    def __init__(self, name: str, role: str, system_prompt: str, confidence: float = 0.9):
        """
        Args:
            name: Nome do agente (ex: "vendas", "suporte", "financeiro")
            role: Descrição curta do papel do agente
            system_prompt: Instruções de sistema que definem o comportamento do agente
            confidence: Nível de confiança padrão das respostas (0.0 a 1.0)
        """
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        self.name = name.strip()
        self.role = role
        self.system_prompt = system_prompt
        self.confidence = confidence

    def run(self, user_input: str, context: Optional[list] = None) -> dict:
        """
        Processa o input do usuário e retorna uma resposta.

        Args:
            user_input: Mensagem do usuário
            context: Histórico de mensagens anteriores (para handoff)

        Returns:
            dict com 'response' (str) e 'confidence' (float)
        """
        context_info = ""
        if context:
            context_info = f" [contexto: {len(context)} mensagens anteriores]"

        # Mock response — substitua por chamada real à API do Claude:
        # from anthropic import Anthropic
        # client = Anthropic()
        # messages = context or []
        # messages.append({"role": "user", "content": user_input})
        # response = client.messages.create(
        #     model="claude-opus-4-5",
        #     max_tokens=1024,
        #     system=self.system_prompt,
        #     messages=messages,
        # )
        # return {"response": response.content[0].text, "confidence": self.confidence}

        mock_response = (
            f"[{self.name.upper()}] Entendido. Você disse: '{user_input}'"
            f"{context_info}. Processando como agente de {self.role}."
        )
        return {"response": mock_response, "confidence": self.confidence}

    def __repr__(self) -> str:
        return f"Agent(name={self.name!r}, role={self.role!r}, confidence={self.confidence})"
