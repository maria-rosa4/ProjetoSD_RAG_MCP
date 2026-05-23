@echo off
echo Iniciando todos os microservicos...

start "RAG Service" cmd /k "cd rag_service && uvicorn main:app --port 8001"
start "MCP Service" cmd /k "cd mcp_service && uvicorn main:app --port 8002"
start "LLM Service" cmd /k "cd llm_service && uvicorn main:app --port 8003"
start "Orquestrador" cmd /k "cd orchestrator && uvicorn main:app --port 8004"
start "API Gateway" cmd /k "cd gateway && uvicorn main:app --port 8000"

echo Todos os servicos foram iniciados em janelas separadas.
pause
