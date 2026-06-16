from fastapi import FastAPI
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import rag

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    saga_id: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/context")
async def get_context_endpoint(request: QueryRequest, x_saga_id: Optional[str] = Header(default=None)):
    saga_id = x_saga_id or request.saga_id
    context = rag.buscar_contexto(request.query)
    return {"context": context, "saga_id": saga_id}
