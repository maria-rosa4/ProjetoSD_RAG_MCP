# Projeto: Assistente de Organização e Priorização Distribuído (Versão Local)

Este projeto implementa um assistente inteligente distribuído utilizando uma arquitetura de microserviços com **API Gateway**, **Orquestrador**, **RAG**, **MCP** e **LLM**. Esta versão foi configurada para execução manual direta no seu computador, sem a necessidade de Docker.

## 1. Arquitetura do Sistema

O sistema é dividido em componentes que se comunicam via rede (HTTP), cada um rodando em sua própria porta:

| Componente | Função | Porta |
| :--- | :--- | :--- |
| **Frontend** | Interface HTML para o usuário final | Abre via arquivo local |
| **API Gateway** | Ponto de entrada único e roteador principal | `8000` |
| **Orquestrador** | Coordena o fluxo de chamadas entre os serviços | `8004` |
| **RAG Service** | Recupera regras de priorização da base ChromaDB | `8001` |
| **MCP Service** | Busca dados reais do Google Tasks e Calendar | `8002` |
| **LLM Service** | Envia o prompt final para o Ollama (IA) | `8003` |

## 2. Pré-requisitos

1.  **Python 3.10+** instalado.
2.  **Ollama** instalado e rodando com o modelo `llama3` (`ollama run llama3`).
3.  **Credenciais do Google**: Arquivo `credentials.json` dentro da pasta `mcp_service/`.

## 3. Instalação

Abra o terminal na pasta raiz do projeto e instale as dependências:

```bash
pip install fastapi uvicorn httpx chromadb requests google-api-python-client google-auth-oauthlib
```

## 4. Como Executar

Você pode iniciar cada serviço manualmente em um terminal diferente ou usar os scripts automatizados:

### Opção A: Usando Scripts (Recomendado)

*   **No Windows:** Clique duas vezes no arquivo `start_all.bat`. Ele abrirá 5 janelas de comando, uma para cada serviço.
*   **No Linux/Mac:** Execute `bash start_all.sh`.

### Opção B: Manualmente (5 Terminais)

Abra 5 terminais e execute um comando em cada um:

1.  **Terminal 1 (RAG):** `cd rag_service && uvicorn main:app --port 8001`
2.  **Terminal 2 (MCP):** `cd mcp_service && uvicorn main:app --port 8002`
3.  **Terminal 3 (LLM):** `cd llm_service && uvicorn main:app --port 8003`
4.  **Terminal 4 (Orquestrador):** `cd orchestrator && uvicorn main:app --port 8004`
5.  **Terminal 5 (Gateway):** `cd gateway && uvicorn main:app --port 8000`

## 5. Como Testar

1.  Com todos os terminais rodando, abra o arquivo `frontend/index.html` no seu navegador.
2.  Digite uma pergunta (ex: "Quais minhas tarefas mais urgentes?") e clique em **Priorizar**.
3.  O fluxo seguirá este caminho:
    `Frontend` -> `Gateway (8000)` -> `Orquestrador (8004)` -> `(RAG + MCP + LLM)` -> `Resposta Final`.

## 6. Configuração das APIs do Google

Para o serviço **MCP** funcionar com seus dados reais:
1.  Coloque seu `credentials.json` em `mcp_service/`.
2.  Na primeira vez que rodar, o terminal do **MCP Service** pedirá para você clicar em um link para autorizar o acesso no navegador.
3.  O arquivo `token.json` será criado automaticamente na pasta `mcp_service/`.

---
**Dica para o Professor:** Esta estrutura demonstra uma arquitetura de microserviços completa, onde o **Gateway** protege o sistema, o **Orquestrador** gerencia a lógica de negócio e os demais serviços agem como provedores de dados e inteligência de forma independente.
