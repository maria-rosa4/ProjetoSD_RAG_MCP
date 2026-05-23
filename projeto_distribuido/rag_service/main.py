from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/context")
async def get_context_endpoint(request: QueryRequest):
    context = rag.buscar_contexto(request.query)
    return {"context": context}
