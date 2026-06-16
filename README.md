# ProjetoSD_RAG_MCP
 Desenvolvimento de um sistema inteligente distribuído utilizando RAG (Retrieval-Augmented Generation) e MCP (Model Context Protocol) para resolver um problema do mundo real.

# 🧠 Sistema Inteligente de Priorização de Tarefas

## 📌 Descrição

Este projeto consiste no desenvolvimento de um sistema inteligente distribuído capaz de auxiliar usuários na priorização de tarefas diárias, considerando compromissos previamente agendados.

O sistema utiliza conceitos de:

* Sistemas Distribuídos
* Inteligência Artificial
* RAG (Retrieval-Augmented Generation)
* MCP (Model Context Protocol)

---

## 🎯 Objetivo

Ajudar o usuário a decidir **o que fazer primeiro**, utilizando:

* regras de priorização (base de conhecimento)
* tarefas do usuário
* eventos da agenda

---

## 🚀 Diferenciais Técnicos (Requisitos Atendidos)

1.  **Arquitetura de Microserviços:** Sistema totalmente desacoplado com 5 serviços independentes comunicando-se via HTTP/REST.
2.  **Padrão SAGA (Orquestração):** Coordenação de transações distribuídas com lógica de compensação (rollback) para garantir a consistência do fluxo.
3.  **RAG (Retrieval-Augmented Generation):** Uso de banco vetorial (ChromaDB) para injetar regras de negócio e metodologias de produtividade no contexto da IA.
4.  **Integração MCP (Model Context Protocol):** Conexão real com as APIs do Google (Tasks e Calendar) para captura de contexto dinâmico.
5.  **Gateway Routing:** Ponto de entrada único que protege a topologia interna e gerencia o tráfego.

---

## 🧱 Arquitetura do Sistema

| Componente | Função | Porta |
| :--- | :--- | :--- |
| **Frontend** | Interface de usuário (React/Vite) | Local |
| **API Gateway** | Ponto de entrada e roteamento | `8000` |
| **Orchestrator** | Coordenador da Saga e Lógica de Negócio | `8004` |
| **RAG Service** | Recuperação semântica (ChromaDB) | `8001` |
| **MCP Service** | Conector Google SDK (Tasks/Calendar) | `8002` |
| **LLM Service** | Interface com o motor de IA (Ollama/Llama3) | `8003` |

---

## 🔄 Fluxo de Dados (Padrão SAGA)

O sistema utiliza o padrão **SAGA Baseado em Orquestração**. O `Orchestrator` gerencia o ciclo de vida da transação:

1.  **Início:** O Gateway recebe a pergunta e valida a intenção (Porteiro).
2.  **Execução:** A `SagaCoordinator` dispara chamadas sequenciais ao RAG, MCP e LLM.
3.  **Transaction Log:** Cada passo é registrado com um `saga_id` único.
4.  **Compensação:** Em caso de falha em qualquer microserviço, a Saga executa o fluxo de compensação para manter o sistema em estado consistente.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.11+
*   **Framework Web:** FastAPI / Uvicorn
*   **Banco Vetorial:** ChromaDB
*   **IA/LLM:** Ollama (Llama 3)
*   **Integrações:** Google Discovery API (OAuth2)
*   **Frontend:** React + Tailwind CSS

---

## ⚙️ Como Executar

### 1. Preparação do Ambiente
Instale as dependências coletivas:
```bash
pip install fastapi uvicorn httpx chromadb requests google-api-python-client google-auth-oauthlib
```

### 2. Configuração do Google MCP
*   Coloque seu arquivo `credentials.json` na pasta `mcp_service/`.
*   O sistema criará o `token.json` automaticamente no primeiro acesso.

### 3. Inicialização Automatizada
Para iniciar todos os microserviços simultaneamente:
*   **Windows:** Execute `start_all.bat`
*   **Linux/Mac:** Execute `bash start_all.sh`

### 4. Acesso ao Sistema
Abra o `frontend/index.html` no navegador e interaja com o assistente.

---

## 👨‍💻 Autores
*   Adrielly Ferreira da Silva
*   Marco Antonio Roquini Espudario
*   Maria Clara Souza Rosa
*   Milena de Lourdes Barbosa

---
*Trabalho desenvolvido para a disciplina de Sistemas Distribuídos - 2026.*

---

## Implementacao local da SAGA

Na versao local, a SAGA fica implementada em `projeto_distribuido/orchestrator/saga.py`.
O Orchestrator gera ou recebe um `saga_id`, propaga esse identificador no header
`X-Saga-Id` e registra o ciclo da requisicao no SQLite local
`projeto_distribuido/orchestrator/saga_log.db`.

Tabelas criadas automaticamente:

* `sagas` - estado geral da transacao distribuida.
* `saga_steps` - log das etapas `CLASSIFY_INTENT`, `FETCH_RAG`, `FETCH_TASKS`,
  `FETCH_CALENDAR`, `SAVE_PRIORITY_PLAN`, `GENERATE_RESPONSE`,
  `CREATE_GOOGLE_TASK`, `CREATE_CALENDAR_EVENT` e `COMPENSATE`.
* `priority_plans` - plano de priorizacao salvo localmente.
* `saga_resources` - recursos criados pela SAGA e status de compensacao.

O plano local e criado como `PENDING` antes da geracao final. Se uma etapa posterior
falhar, a compensacao marca esse plano como `CANCELLED`. Quando a requisicao pede
criacao opcional de tarefa ou evento no Google, os recursos sao registrados e podem
ser removidos pelos endpoints de compensacao do MCP.

Para consultar o log de uma execucao:

```bash
curl http://127.0.0.1:8004/sagas/SEU_SAGA_ID
```
