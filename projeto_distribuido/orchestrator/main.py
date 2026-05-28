from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging

# Configuração de logs para ajudar no debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RAG_SERVICE_URL = "http://127.0.0.1:8001"
MCP_SERVICE_URL = "http://127.0.0.1:8002"
LLM_SERVICE_URL = "http://127.0.0.1:8003"

class PrioritizeRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "orchestrator is running"}

@app.post("/prioritize")
async def prioritize_tasks(request: PrioritizeRequest):
    async with httpx.AsyncClient() as client:
        # 1. Tentar RAG
        try:
            rag_response = await client.post(f"{RAG_SERVICE_URL}/context", json={"query": request.query}, timeout=10.0)
            rag_response.raise_for_status()
            context = rag_response.json().get("context", [])
        except Exception as e:
            logger.error(f"Falha no RAG Service: {str(e)}")
            context = ["Erro ao recuperar contexto do RAG."]

        # 2. Tentar MCP (Google)
        try:
            tasks_response = await client.get(f"{MCP_SERVICE_URL}/tasks", timeout=15.0)
            tasks_response.raise_for_status()
            tasks = tasks_response.json().get("tasks", [])
        except Exception as e:
            logger.error(f"Falha no MCP Service (Tasks): {str(e)}")
            tasks = ["Erro ao recuperar tarefas do Google Tasks. Verifique as credenciais."]

        try:
            calendar_response = await client.get(f"{MCP_SERVICE_URL}/calendar", timeout=15.0)
            calendar_response.raise_for_status()
            events = calendar_response.json().get("events", [])
        except Exception as e:
            logger.error(f"Falha no MCP Service (Calendar): {str(e)}")
            events = ["Erro ao recuperar eventos do Google Calendar."]

        # 3. Tentar LLM
        prompt = f"""
        Você é um assistente de priorização.
        Regras: {context}
        Tarefas Reais: {tasks}
        Agenda: {events}
        Pergunta do Usuário: {request.query}
        Por favor, priorize as tarefas e explique o motivo.
        """

        try:
            llm_response = await client.post(f"{LLM_SERVICE_URL}/generate", json={"prompt": prompt}, timeout=180.0)
            llm_response.raise_for_status()
            final_response = llm_response.json().get("response", "Erro na geração")
            return {"prioritized_response": final_response}
        except Exception as e:
            logger.error(f"Falha no LLM Service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"O serviço de IA (LLM) falhou. Verifique se o Ollama está rodando. Erro: {str(e)}")
