#!/bin/bash

echo "Iniciando todos os microserviços..."

# Iniciar RAG Service na porta 8001
echo "Iniciando RAG Service na porta 8001..."
cd rag_service && uvicorn main:app --port 8001 &
cd ..

# Iniciar MCP Service na porta 8002
echo "Iniciando MCP Service na porta 8002..."
cd mcp_service && uvicorn main:app --port 8002 &
cd ..

# Iniciar LLM Service na porta 8003
echo "Iniciando LLM Service na porta 8003..."
cd llm_service && uvicorn main:app --port 8003 &
cd ..

# Iniciar Orquestrador na porta 8004
echo "Iniciando Orquestrador na porta 8004..."
cd orchestrator && uvicorn main:app --port 8004 &
cd ..

# Iniciar API Gateway na porta 8000
echo "Iniciando API Gateway na porta 8000..."
cd gateway && uvicorn main:app --port 8000 &
cd ..

echo "Todos os serviços foram iniciados em segundo plano."
echo "Pressione Ctrl+C para encerrar (ou use 'pkill uvicorn')."
wait
