import logging
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import tools


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class CreateTaskRequest(BaseModel):
    title: str
    notes: Optional[str] = None
    saga_id: Optional[str] = None


class CreateCalendarEventRequest(BaseModel):
    summary: str
    start_datetime: str
    end_datetime: str
    description: Optional[str] = None
    saga_id: Optional[str] = None


@app.on_event("startup")
def autenticar_google_no_startup():
    print("\n" + "=" * 50)
    print("Preparando autenticacao inicial do Google...")
    print("=" * 50 + "\n")
    try:
        tools.get_credentials()
        print("Verificacao de credenciais concluida com sucesso. Token pronto.")
    except Exception as exc:
        print(f"Erro na autenticacao inicial: {exc}")


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
async def get_google_tasks_endpoint(x_saga_id: Optional[str] = Header(default=None)):
    try:
        tasks = tools.get_tasks()
        return {"tasks": tasks, "saga_id": x_saga_id}
    except Exception as exc:
        logger.error("Erro ao buscar tarefas: %s", exc)
        raise HTTPException(status_code=502, detail={"saga_id": x_saga_id, "error": str(exc)})


@app.post("/tasks")
async def create_google_task_endpoint(
    request: CreateTaskRequest,
    x_saga_id: Optional[str] = Header(default=None),
):
    saga_id = x_saga_id or request.saga_id
    try:
        task = tools.create_task(request.title, request.notes)
        return {"task": task, "saga_id": saga_id}
    except Exception as exc:
        logger.error("Erro ao criar tarefa: %s", exc)
        raise HTTPException(status_code=502, detail={"saga_id": saga_id, "error": str(exc)})


@app.delete("/tasks/{task_id}")
async def delete_google_task_endpoint(
    task_id: str,
    x_saga_id: Optional[str] = Header(default=None),
):
    try:
        result = tools.delete_task(task_id)
        return {"result": result, "saga_id": x_saga_id}
    except Exception as exc:
        logger.error("Erro ao deletar tarefa: %s", exc)
        raise HTTPException(status_code=502, detail={"saga_id": x_saga_id, "error": str(exc)})


@app.get("/calendar")
async def get_google_calendar_events_endpoint(x_saga_id: Optional[str] = Header(default=None)):
    try:
        events = tools.get_calendar()
        return {"events": events, "saga_id": x_saga_id}
    except Exception as exc:
        logger.error("Erro ao buscar calendario: %s", exc)
        raise HTTPException(status_code=502, detail={"saga_id": x_saga_id, "error": str(exc)})


@app.post("/calendar/events")
async def create_google_calendar_event_endpoint(
    request: CreateCalendarEventRequest,
    x_saga_id: Optional[str] = Header(default=None),
):
    saga_id = x_saga_id or request.saga_id
    try:
        event = tools.create_calendar_event(
            request.summary,
            request.start_datetime,
            request.end_datetime,
            request.description,
        )
        return {"event": event, "saga_id": saga_id}
    except Exception as exc:
        logger.error("Erro ao criar evento: %s", exc)
        raise HTTPException(status_code=502, detail={"saga_id": saga_id, "error": str(exc)})


@app.delete("/calendar/events/{event_id}")
async def delete_google_calendar_event_endpoint(
    event_id: str,
    x_saga_id: Optional[str] = Header(default=None),
):
    try:
        result = tools.delete_calendar_event(event_id)
        return {"result": result, "saga_id": x_saga_id}
    except Exception as exc:
        logger.error("Erro ao deletar evento: %s", exc)
        raise HTTPException(status_code=502, detail={"saga_id": x_saga_id, "error": str(exc)})
