from fastapi import FastAPI
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import llm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    saga_id: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/generate")
async def generate_response_endpoint(request: PromptRequest, x_saga_id: Optional[str] = Header(default=None)):
    saga_id = x_saga_id or request.saga_id
    response = llm.gerar_resposta(request.prompt)
    return {"response": response, "saga_id": saga_id}
