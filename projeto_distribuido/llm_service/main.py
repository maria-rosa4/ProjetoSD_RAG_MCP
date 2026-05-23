from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/generate")
async def generate_response_endpoint(request: PromptRequest):
    response = llm.gerar_resposta(request.prompt)
    return {"response": response}
