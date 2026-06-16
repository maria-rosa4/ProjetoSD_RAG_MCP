import uuid
from typing import Optional

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ORCHESTRATOR_SERVICE_URL = "http://127.0.0.1:8004"


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/prioritize")
async def route_prioritize(
    request: Request,
    x_saga_id: Optional[str] = Header(default=None),
):
    saga_id = x_saga_id or str(uuid.uuid4())
    try:
        body = await request.json()
        body["saga_id"] = saga_id
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ORCHESTRATOR_SERVICE_URL}/prioritize",
                json=body,
                headers={"X-Saga-Id": saga_id},
                timeout=180.0,
            )
            response.raise_for_status()
            payload = response.json()
            payload["saga_id"] = payload.get("saga_id", saga_id)
            return JSONResponse(
                content=payload,
                headers={"X-Saga-Id": saga_id},
            )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        try:
            detail = exc.response.json()
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"saga_id": saga_id, "error": str(exc)})
