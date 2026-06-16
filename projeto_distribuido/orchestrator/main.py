from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from saga import SagaCoordinator


app = FastAPI()
saga_coordinator = SagaCoordinator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PrioritizeRequest(BaseModel):
    query: str
    saga_id: Optional[str] = None
    create_google_task: bool = False
    create_calendar_event: bool = False
    calendar_start_datetime: Optional[str] = None
    calendar_end_datetime: Optional[str] = None


async def call_json_step(
    client: httpx.AsyncClient,
    saga_id: str,
    step_name: str,
    method: str,
    url: str,
    headers: Dict[str, str],
    json_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    step_id = saga_coordinator.start_step(
        saga_id,
        step_name,
        {"method": method, "url": url, "json": json_payload or {}},
    )
    try:
        response = await client.request(
            method,
            url,
            json=json_payload,
            headers=headers,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(payload["error"])
        saga_coordinator.complete_step(step_id, payload)
        return payload
    except Exception as exc:
        saga_coordinator.fail_step(step_id, str(exc))
        raise


@app.get("/health")
async def health_check():
    return {"status": "orchestrator is running"}


@app.get("/sagas/{saga_id}")
async def get_saga_status(saga_id: str):
    saga = saga_coordinator.get_saga(saga_id)
    if saga is None:
        raise HTTPException(status_code=404, detail="Saga not found")
    return saga


@app.post("/prioritize")
async def prioritize_tasks(
    request: PrioritizeRequest,
    x_saga_id: Optional[str] = Header(default=None),
):
    saga_id = saga_coordinator.create_saga(
        query=request.query,
        saga_id=x_saga_id or request.saga_id,
    )
    headers = {"X-Saga-Id": saga_id}
    created_resources: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            prompt_classificacao = f"""
            Classifique a seguinte mensagem do usuario com '1' ou '0'.

            Mensagem: "{request.query}"

            Regras:
            1 = A mensagem e um pedido de ajuda com organizacao, tarefas, agenda ou produtividade.
            0 = A mensagem e sobre qualquer outro assunto.

            Sua resposta deve conter APENAS O NUMERO, sem ponto, sem texto extra e sem justificativa.
            """

            classificacao = await call_json_step(
                client,
                saga_id,
                "CLASSIFY_INTENT",
                "POST",
                "http://127.0.0.1:8003/generate",
                headers,
                {"prompt": prompt_classificacao, "saga_id": saga_id},
            )
            intencao = str(classificacao.get("response", "")).strip()

            if "[Erro" in intencao:
                raise RuntimeError(f"Erro ao classificar intencao: {intencao}")

            if "0" in intencao or "1" not in intencao:
                resposta_padrao = (
                    "Ola! Eu sou um Assistente Especializado em Produtividade.\n\n"
                    "Meu escopo e focado em organizar suas tarefas do Google, "
                    "analisar sua agenda e definir prioridades para o seu dia.\n\n"
                    "Como posso ajudar a organizar seu trabalho hoje?"
                )
                saga_coordinator.mark_rejected(saga_id, resposta_padrao)
                return {
                    "saga_id": saga_id,
                    "prioritized_response": resposta_padrao,
                    "status": "REJECTED",
                }

            rag_response = await call_json_step(
                client,
                saga_id,
                "FETCH_RAG",
                "POST",
                "http://127.0.0.1:8001/context",
                headers,
                {"query": request.query, "saga_id": saga_id},
            )
            contexto_regras = rag_response.get("context", "")

            tasks_response = await call_json_step(
                client,
                saga_id,
                "FETCH_TASKS",
                "GET",
                "http://127.0.0.1:8002/tasks",
                headers,
            )
            tarefas_google = tasks_response.get("tasks", [])

            calendar_response = await call_json_step(
                client,
                saga_id,
                "FETCH_CALENDAR",
                "GET",
                "http://127.0.0.1:8002/calendar",
                headers,
            )
            agenda_google = calendar_response.get(
                "events",
                calendar_response.get("calendar", []),
            )

            plan_step_id = saga_coordinator.start_step(
                saga_id,
                "SAVE_PRIORITY_PLAN",
                {"query": request.query, "status": "PENDING"},
            )
            plan_id = saga_coordinator.create_priority_plan(saga_id, request.query)
            created_resources.append({"type": "priority_plan", "id": plan_id})
            saga_coordinator.complete_step(plan_step_id, {"plan_id": plan_id})

            data_atual = datetime.now().strftime("%d/%m/%Y")
            super_prompt = f"""
            Voce e um Assistente Inteligente de Produtividade.
            Saga atual: {saga_id}
            Data de hoje: {data_atual}

            DADOS DISPONIVEIS:
            - Regras de Negocio (RAG): {contexto_regras}
            - Tarefas Pendentes (Google Tasks): {tarefas_google}
            - Compromissos/Eventos da Agenda (Google Calendar): {agenda_google}

            PERGUNTA DO USUARIO: "{request.query}"

            CRITERIOS DE CLASSIFICACAO:
            - Saude e bem-estar sao sempre urgentes e importantes.
            - Compromissos com horario para hoje sao inadiaveis.
            - Deveres academicos/profissionais sao importantes.
            - Lazer e entretenimento devem ficar para o fim do dia.

            INSTRUCOES:
            1. Responda diretamente a pergunta usando os dados disponiveis.
            2. Se o usuario pedir priorizacao, crie um plano ordenado para o dia.
            3. Seja direto, conciso e mantenha um tom profissional.
            """

            final_response = await call_json_step(
                client,
                saga_id,
                "GENERATE_RESPONSE",
                "POST",
                "http://127.0.0.1:8003/generate",
                headers,
                {"prompt": super_prompt, "saga_id": saga_id},
            )
            resposta_final = final_response.get("response") or ""

            saga_coordinator.activate_priority_plan(plan_id, resposta_final)

            if request.create_google_task:
                task_payload = await call_json_step(
                    client,
                    saga_id,
                    "CREATE_GOOGLE_TASK",
                    "POST",
                    "http://127.0.0.1:8002/tasks",
                    headers,
                    {
                        "title": f"Plano de priorizacao - {saga_id}",
                        "notes": resposta_final,
                        "saga_id": saga_id,
                    },
                )
                task_id = task_payload.get("task", {}).get("id")
                if not task_id:
                    raise RuntimeError("MCP nao retornou id da tarefa criada")
                created_resources.append({"type": "google_task", "id": task_id})
                saga_coordinator.register_resource(saga_id, "google_task", task_id)

            if request.create_calendar_event:
                if not request.calendar_start_datetime or not request.calendar_end_datetime:
                    raise RuntimeError(
                        "Para criar evento no calendario, informe calendar_start_datetime "
                        "e calendar_end_datetime"
                    )
                event_payload = await call_json_step(
                    client,
                    saga_id,
                    "CREATE_CALENDAR_EVENT",
                    "POST",
                    "http://127.0.0.1:8002/calendar/events",
                    headers,
                    {
                        "summary": f"Plano de priorizacao - {saga_id}",
                        "description": resposta_final,
                        "start_datetime": request.calendar_start_datetime,
                        "end_datetime": request.calendar_end_datetime,
                        "saga_id": saga_id,
                    },
                )
                event_id = event_payload.get("event", {}).get("id")
                if not event_id:
                    raise RuntimeError("MCP nao retornou id do evento criado")
                created_resources.append({"type": "google_calendar_event", "id": event_id})
                saga_coordinator.register_resource(
                    saga_id,
                    "google_calendar_event",
                    event_id,
                )

            saga_coordinator.mark_completed(saga_id, resposta_final)
            return {
                "saga_id": saga_id,
                "plan_id": plan_id,
                "prioritized_response": resposta_final,
                "status": "COMPLETED",
            }
        except Exception as exc:
            error_text = str(exc)
            try:
                await saga_coordinator.compensate(
                    saga_id,
                    created_resources,
                    error_text,
                    client,
                    headers,
                )
            except Exception as compensation_error:
                error_text = f"{error_text}; compensation_error={compensation_error}"
            saga_coordinator.mark_failed(saga_id, error_text)
            raise HTTPException(
                status_code=500,
                detail={"saga_id": saga_id, "error": error_text},
            )
