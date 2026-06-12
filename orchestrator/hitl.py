"""
hitl.py — Human-in-the-Loop: avalia se uma resposta precisa de revisão humana.
"""


class HITLChecker:
    """
    Verifica se a resposta de um agente deve ser revisada por um humano
    com base no nível de confiança e em regras configuráveis.
    """

    def __init__(self, confidence_threshold: float = 0.75, sensitive_keywords: list[str] = None):
        """
        Args:
            confidence_threshold: Confiança mínima para aprovação automática (0.0 a 1.0)
            sensitive_keywords: Palavras que forçam revisão humana independente da confiança
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")

        self.confidence_threshold = confidence_threshold
        self.sensitive_keywords = [kw.lower() for kw in (sensitive_keywords or [])]

    def check(self, response: str, confidence: float, user_input: str = "") -> dict:
        """
        Avalia se a resposta precisa de revisão humana.

        Args:
            response: Texto da resposta gerada pelo agente
            confidence: Nível de confiança da resposta (0.0 a 1.0)
            user_input: Input original do usuário (para verificar keywords sensíveis)

        Returns:
            dict com:
                - hitl_required (bool): True se precisa de revisão humana
                - reason (str): Motivo da flag (ou "auto-approved")
                - confidence (float): Confiança recebida
                - threshold (float): Threshold configurado
        """
        # Verifica keywords sensíveis
        combined_text = (user_input + " " + response).lower()
        for kw in self.sensitive_keywords:
            if kw in combined_text:
                return {
                    "hitl_required": True,
                    "reason": f"Keyword sensível detectada: '{kw}'",
                    "confidence": confidence,
                    "threshold": self.confidence_threshold,
                }

        # Verifica threshold de confiança
        if confidence < self.confidence_threshold:
            return {
                "hitl_required": True,
                "reason": f"Confiança {confidence:.2f} abaixo do threshold {self.confidence_threshold:.2f}",
                "confidence": confidence,
                "threshold": self.confidence_threshold,
            }

        return {
            "hitl_required": False,
            "reason": "auto-approved",
            "confidence": confidence,
            "threshold": self.confidence_threshold,
        }

    def update_threshold(self, new_threshold: float) -> None:
        """Atualiza o threshold de confiança em tempo de execução."""
        if not 0.0 <= new_threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.confidence_threshold = new_threshold

    def __repr__(self) -> str:
        return (
            f"HITLChecker(threshold={self.confidence_threshold}, "
            f"sensitive_keywords={self.sensitive_keywords})"
        )
