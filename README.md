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

## 🧱 Arquitetura do Sistema

O sistema é composto por múltiplos componentes:

* **API (FastAPI)** → interface de entrada
* **Pipeline** → orquestra o fluxo
* **RAG (ChromaDB)** → recuperação de conhecimento
* **MCP (tools.py)** → acesso a dados externos (simulados)
* **LLM (Ollama + Llama3)** → geração de respostas

---

## 🔄 Fluxo de Funcionamento

1. O usuário faz uma pergunta
2. O sistema consulta a base de conhecimento (RAG)
3. O sistema obtém tarefas e agenda (MCP)
4. O prompt é construído com todas as informações
5. O modelo gera uma resposta contextualizada

---

## 🧠 RAG (Retrieval-Augmented Generation)

O sistema utiliza RAG para fornecer ao modelo conhecimento sobre priorização de tarefas.

### Base de conhecimento:

* tarefas urgentes e importantes devem ser feitas primeiro
* tarefas importantes devem ser planejadas
* tarefas urgentes e não importantes podem ser delegadas
* tarefas não importantes devem ser evitadas

---

## 🔗 MCP (Model Context Protocol)

O MCP é utilizado para integrar dados externos ao sistema.

Atualmente, foi implementado de forma simulada:

* `get_tasks()` → retorna lista de tarefas
* `get_calendar()` → retorna compromissos do dia

---

## 🤖 Modelo de Linguagem

O sistema utiliza:

* Ollama
* Modelo: Llama 3

O modelo é responsável por gerar respostas com base no contexto fornecido.

---

## ⚙️ Tecnologias Utilizadas

* Python
* FastAPI
* ChromaDB
* Requests
* Ollama

---

## 📁 Estrutura do Projeto

```
SistemasDistribuidos/
│
├── venv/                # ambiente virtual
├── rag.py              # recuperação de conhecimento
├── tools.py            # simulação de ferramentas externas (MCP)
├── llm.py              # conexão com o modelo
├── pipeline.py         # lógica principal do sistema
├── main.py             # API
```

---

## 🚀 Como Executar o Projeto

### 1. Criar ambiente virtual

```
python -m venv venv
```

### 2. Ativar ambiente

Windows:

```
venv\Scripts\activate
```

Caso ocorra erro de permissão:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

### 3. Instalar dependências

```
pip install fastapi uvicorn chromadb requests
```

---

### 4. Instalar e executar o Ollama

Baixar:
https://ollama.com

Verificar instalação:

```
ollama --version
```

Baixar modelo:

```
ollama pull llama3
```

Executar:

```
ollama run llama3
```

---

### 5. Testar componentes

RAG:

```
python rag.py
```

MCP:

```
python tools.py
```

LLM:

```
python llm.py
```

Pipeline:

```
python pipeline.py
```

---

### 6. Executar API

```
uvicorn main:app --reload
```

Acessar:

```
http://127.0.0.1:8000/priorizar?pergunta=O que devo fazer hoje?
```

---

## ⚠️ Observações

* A agenda é tratada como **restrição de tempo**, não como tarefa
* Apenas tarefas são priorizadas
* O comportamento do modelo é controlado via engenharia de prompt

---

## 📌 Próximos Passos

* Integração real com Google Calendar e Google Tasks
* Interface gráfica
* Aprimoramento da priorização
* Sugestão automática de horários

---

## 👨‍💻 Autor(es)

* Maria Clara Souza Rosa
* Milena de Lourdes Barbosa
*
* 

---
