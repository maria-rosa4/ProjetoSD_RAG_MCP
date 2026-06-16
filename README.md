# Assistente Inteligente de Gestão de Atividades e Priorização de Tarefas (Gamma)

GCC129 - Sistemas Distribuídos | UFLA (Universidade Federal de Lavras)

Desenvolvimento de um sistema inteligente distribuído utilizando RAG (Retrieval-Augmented Generation) e MCP (Model Context Protocol) para resolver o problema real da gestão e priorização de rotinas diárias.

# 📌 Visão Geral do Projeto

Este projeto consiste em um assistente cognitivo distribuído capaz de auxiliar usuários na priorização dinâmica de suas tarefas diárias, considerando regras científicas de produtividade (Matriz de Eisenhower) e dados reais de sua agenda física e lista de afazeres.

O sistema é construído inteiramente sob os conceitos modernos de Sistemas Distribuídos, utilizando o padrão de Microsserviços de forma assíncrona, desacoplada e resiliente.

# 🧱 Topologia do Ecossistema Distribuído

Para garantir o desacoplamento e a especialização de responsabilidades, o ecossistema é dividido em 5 microsserviços e 1 cliente frontend estruturados da seguinte forma:

Frontend: Localizado na pasta /frontend. Opera na porta de rede padrão 5173. Desenvolvido utilizando React, Vite, TypeScript e Tailwind CSS.

API Gateway: Localizado na pasta /gateway. Opera na porta de rede 8004. Desenvolvido em Python com FastAPI e HTTPX.

Orchestrator (Orquestrador): Localizado na pasta /orchestrator. Opera na porta de rede 8000. Desenvolvido em Python com FastAPI, atuando como o cérebro e coordenador do fluxo de execução.

RAG Service (Serviço RAG): Localizado na pasta /rag_service. Opera na porta de rede 8001. Desenvolvido em Python com FastAPI e banco de dados vetorial ChromaDB.

MCP Service (Serviço MCP): Localizado na pasta /mcp_service. Opera na porta de rede 8002. Desenvolvido em Python com Google Client SDK para integração direta com as APIs do Google Tasks e Google Calendar.

LLM Service (Serviço LLM): Localizado na pasta /llm_service. Opera na porta de rede 8003. Desenvolvido em Python utilizando Ollama e o modelo de linguagem local Llama 3.



# ⚙️ Como Instalar e Executar o Projeto

O projeto exige o interpretador Python 3.10+ para o backend e o Node.js (v18+) para o frontend.

1. Preparação e Execução do Backend

Abra o seu terminal na raiz do projeto (projeto_distribuido/):

1.1 Criar e ativar o ambiente virtual (Recomendado)

# Windows:
python -m venv venv
venv\Scripts\activate

# Linux / macOS:
python -m venv venv
source venv/bin/activate


1.2 Instalar dependências de rede e IA

pip install -r requirements.txt


(Caso não possua o arquivo unificado, instale manualmente os pacotes principais):

pip install fastapi uvicorn chromadb requests httpx google-auth google-auth-oauthlib google-api-python-client


1.3 Instalar e executar o Ollama (Llama 3)

Faça o download do Ollama em ollama.com e inicialize-o.

Baixe o modelo requerido localmente via terminal:

ollama pull llama3


1.4 Configuração das Credenciais do Google MCP

Acesse o Google Cloud Console, crie um projeto e habilite a Google Tasks API e a Google Calendar API.

Crie uma tela de consentimento OAuth e gere uma credencial do tipo ID do cliente OAuth (Aplicativo Desktop).

Baixe o arquivo JSON dessas credenciais, renomeie para credentials.json e coloque-o dentro da pasta /mcp_service.

Nota: Na primeira inicialização, o servidor abrirá uma aba no navegador para que você faça login em sua conta do Google para gravar o token de acesso no arquivo token.json.

1.5 Inicializar todos os Microsserviços

Para não ter que abrir 5 terminais manualmente, utilize os scripts integrados de lote na pasta raiz:

No Windows:

.\start_all.bat


No Linux / macOS:

chmod +x start_all.sh
./start_all.sh


# 2. Preparação e Execução do Frontend (React + Vite)

Navegue até a pasta de interface do usuário (projeto_distribuido/frontend):

cd frontend


2.1 Instalar dependências do Node.js

npm install


2.2 Iniciar o servidor de desenvolvimento

npm run dev


O terminal exibirá o endereço local da interface gráfica, normalmente: 👉 http://localhost:5173

# 👨‍💻 Grupo e Participantes

Este projeto foi apresentado para a banca examinadora da UFLA pelo seguinte grupo de alunos:

Adrielly Ferreira da Silva

Marco Antonio Roquini Espudario

Maria Clara Souza Rosa

Milena de Lourdes Barbosa

Universidade Federal de Lavras — GCC129 (Sistemas Distribuídos)
