from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

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
async def route_prioritize(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{ORCHESTRATOR_SERVICE_URL}/prioritize", json=body, timeout=180.0)
            response.raise_for_status()
            return JSONResponse(content=response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
