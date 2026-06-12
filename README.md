# agent-orchestrator-python

[![CI](https://github.com/dimitrearaujo/agent-orchestrator-python/actions/workflows/ci.yml/badge.svg)](https://github.com/dimitrearaujo/agent-orchestrator-python/actions/workflows/ci.yml)

Orquestrador multi-agente em Python puro com memória de sessão, roteamento por intent, handoff com contexto preservado e Human-in-the-Loop.

---

## Fluxo de Orquestração

```
                        ┌─────────────────────────────────────────────┐
                        │              PIPELINE (pipeline.py)          │
                        │                                              │
  Input do usuário      │   ┌──────────┐     ┌─────────────────────┐  │
  ────────────────►     │   │  ROUTER  │────►│  AGENTE selecionado │  │
                        │   │(router.py│     │    (agent.py)        │  │
                        │   └──────────┘     └────────┬────────────┘  │
                        │                             │ resposta       │
                        │   ┌──────────┐              │                │
                        │   │ MEMÓRIA  │◄─────────────┘                │
                        │   │(memory.py│  salva input + resposta       │
                        │   └──────────┘                               │
                        │        │ confiança baixa?                    │
                        │        ▼                                      │
                        │   ┌──────────┐                               │
                        │   │ HANDOFF  │  transfere com contexto       │
                        │   │(handoff  │  para agente fallback         │
                        │   │  .py)    │                               │
                        │   └──────────┘                               │
                        │        │                                      │
                        │        ▼                                      │
                        │   ┌──────────┐                               │
                        │   │  HITL    │  flag se precisa de           │
                        │   │(hitl.py) │  revisão humana               │
                        │   └──────────┘                               │
                        │        │                                      │
                        └────────┼─────────────────────────────────────┘
                                 │
                                 ▼
                        Output estruturado:
                        {agent_used, response, hitl_required, session_id, ...}
```

---

## Estrutura do Projeto

```
agent-orchestrator-python/
├── .env.example              # Variáveis de ambiente necessárias
├── .gitignore
├── .github/workflows/ci.yml  # CI com syntax check + testes inline
├── README.md
├── requirements.txt
├── main.py                   # Demo com 3 agentes: vendas, suporte, financeiro
└── orchestrator/
    ├── __init__.py
    ├── agent.py              # Classe base Agent
    ├── memory.py             # Memória de sessão in-memory
    ├── router.py             # Roteador por keywords/intent
    ├── handoff.py            # Transferência entre agentes
    ├── hitl.py               # Human-in-the-Loop
    └── pipeline.py           # Orquestrador do fluxo completo
```

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/dimitrearaujo/agent-orchestrator-python.git
cd agent-orchestrator-python

# Crie o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com sua ANTHROPIC_API_KEY
```

---

## Uso Rápido

```bash
# Rode a demo com 3 agentes
python main.py
```

### Uso programático

```python
from orchestrator import Agent, SessionMemory, Router, HandoffManager, HITLChecker, Pipeline

# 1. Defina os agentes
vendas = Agent("vendas", "vendedor", "Você é especialista em vendas.", confidence=0.92)
suporte = Agent("suporte", "suporte técnico", "Você resolve problemas técnicos.", confidence=0.85)

# 2. Configure o roteador
router = Router([vendas, suporte], default_agent=suporte)
router.register_keywords("vendas", ["preço", "plano", "contratar"])
router.register_keywords("suporte", ["erro", "bug", "problema"])

# 3. Monte o pipeline
memory = SessionMemory()
handoff = HandoffManager(memory)
hitl = HITLChecker(confidence_threshold=0.75)
pipeline = Pipeline(router, memory, handoff, hitl)

# 4. Execute
result = pipeline.run("Qual o preço do plano?")
print(result["agent_used"])    # "vendas"
print(result["hitl_required"]) # False
print(result["response"])      # Resposta do agente vendas
```

---

## Como Adicionar Novos Agentes

1. Crie uma instância de `Agent` com nome, role e system_prompt únicos:

```python
from orchestrator import Agent

agente_juridico = Agent(
    name="juridico",
    role="consultor jurídico especializado em contratos",
    system_prompt="Você é advogado especializado em contratos de SaaS...",
    confidence=0.80,
)
```

2. Adicione ao `Router` e registre as keywords:

```python
router = Router([agente_juridico, ...], default_agent=agente_suporte)
router.register_keywords("juridico", ["contrato", "cláusula", "rescisão", "multa"])
```

3. Pronto. O pipeline já roteia automaticamente para o novo agente.

---

## Como Integrar com a Claude API (Modo Real)

Substitua o método mock em `orchestrator/agent.py` pela chamada real:

```python
# orchestrator/agent.py
from anthropic import Anthropic

client = Anthropic()  # usa ANTHROPIC_API_KEY do ambiente

def run(self, user_input: str, context=None) -> dict:
    messages = list(context or [])
    # Remove mensagens 'system' do histórico (não são aceitas em messages)
    messages = [m for m in messages if m["role"] in ("user", "assistant")]
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=self.system_prompt,
        messages=messages,
    )
    return {
        "response": response.content[0].text,
        "confidence": self.confidence,
    }
```

Para confiança dinâmica, você pode usar o campo `stop_reason` ou implementar um classificador de confiança baseado no conteúdo da resposta.

---

## Python Puro vs LangChain/LangFlow

| Critério | Python Puro (este projeto) | LangChain / LangFlow |
|---|---|---|
| Dependências | 2 (`anthropic`, `python-dotenv`) | 50+ pacotes |
| Tempo de boot | < 0.1s | 2–5s |
| Debuggability | Stack trace direto | Abstrações opacas |
| Flexibilidade | Total controle do fluxo | Limitado às abstrações |
| Curva de aprendizado | Python padrão | API proprietária |
| Handoff customizado | Implementado em ~30 linhas | Workaround complexo |
| Vendor lock-in | Zero | Alto (LangSmith, etc.) |
| Produção | Direto no servidor | Overhead adicional |

**Quando usar este projeto:** você precisa de controle total, código auditável, performance máxima e zero dependências desnecessárias.

**Quando usar LangChain:** você quer integrar 20+ ferramentas prontas rapidamente e o overhead não é problema.

---

## Configuração via `.env`

| Variável | Padrão | Descrição |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Chave da API do Claude (obrigatório para modo real) |
| `HITL_CONFIDENCE_THRESHOLD` | `0.75` | Confiança mínima para aprovação automática |
| `HANDOFF_THRESHOLD` | `0.50` | Confiança mínima para evitar handoff automático |
| `DEFAULT_AGENT` | `suporte` | Agente padrão quando nenhuma keyword corresponde |

---

## Desenvolvido por

**CD Tech** — Automação e agentes IA para pequenos negócios  
[dimitrearaujo@gmail.com](mailto:dimitrearaujo@gmail.com) | Fortaleza, CE
