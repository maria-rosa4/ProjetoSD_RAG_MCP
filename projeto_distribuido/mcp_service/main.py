from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import tools
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
def autenticar_google_no_startup():
    print("\n" + "="*50)
    print("Preparando autenticação inicial do Google...")
    print("="*50 + "\n")
    try:
        import tools
        # Força a verificação e geração do token logo ao ligar o servidor
        tools.get_credentials()
        print("Verificação de credenciais concluída com sucesso! Token pronto.")
    except Exception as e:
        print(f"Erro na autenticação inicial: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "mcp service is running"}

@app.get("/tasks")
async def get_google_tasks_endpoint():
    try:
        tasks = tools.get_tasks()
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Erro ao buscar tarefas: {e}")
        return {"tasks": ["Google Tasks indisponível (verifique credentials.json)"], "error": str(e)}

@app.get("/calendar")
async def get_google_calendar_events_endpoint():
    try:
        events = tools.get_calendar()
        return {"events": events}
    except Exception as e:
        logger.error(f"Erro ao buscar calendário: {e}")
        return {"events": ["Google Calendar indisponível"], "error": str(e)}
