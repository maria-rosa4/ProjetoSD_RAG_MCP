from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import httpx
import logging


# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrioritizeRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "orchestrator is running"}

@app.post("/prioritize")
async def prioritize_tasks(request: PrioritizeRequest):
    async with httpx.AsyncClient(timeout=180.0) as client:
        
        # ==========================================================
        # PASSO 1: O PORTEIRO (Classificação de Intenção Binária)
        # ==========================================================
        prompt_classificacao = f"""
        Classifique a seguinte mensagem do usuário com '1' ou '0'.
        
        Mensagem: "{request.query}"
        
        Regras:
        1 = A mensagem é um pedido de ajuda com organização, tarefas, agenda ou produtividade.
        0 = A mensagem é sobre qualquer outro assunto (clima, curiosidades, piadas, bate-papo).
        
        Sua resposta deve conter APENAS O NÚMERO, sem ponto, sem texto extra e sem justificativa.
        """
        
        try:
            resposta_porteiro = await client.post("http://127.0.0.1:8003/generate", json={"prompt": prompt_classificacao})
            intencao = resposta_porteiro.json().get("response", "").strip()
            print(f"\n[DEBUG DO PORTEIRO] Resposta crua do Llama 3: '{intencao}'\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao classificar intenção: {str(e)}")

        # ==========================================================
        # PASSO 2: A BIFURCAÇÃO (O Guardrail)
        # ==========================================================
        
        # 1. Se a IA devolveu a nossa mensagem de erro customizada, mostra na tela!
        if "[Erro" in intencao:
            return {"prioritized_response": f"⚠️ Ops! O Porteiro encontrou um problema no motor da IA: {intencao}"}

        # 2. O Guardrail normal (barra assuntos aleatórios)
        if "0" in intencao or "1" not in intencao:
            resposta_padrao = (
                "Olá! 🎯 Eu sou um Assistente Especializado em Produtividade.\n\n"
                "Meu escopo é estritamente focado em organizar suas tarefas do Google, "
                "analisar sua agenda e definir prioridades para o seu dia.\n\n"
                "Infelizmente, não posso ajudar com assuntos externos como previsão do tempo ou conhecimentos gerais. "
                "Como posso ajudar a organizar seu trabalho hoje?"
            )
            return {"prioritized_response": resposta_padrao}

        # ==========================================================
        # PASSO 3: O FLUXO NORMAL E INTELIGENTE (Tasks + Calendar)
        # ==========================================================
        try:
            # 1. Puxa o RAG
            rag_response = await client.post("http://127.0.0.1:8001/context", json={"query": request.query})
            contexto_regras = rag_response.json().get("context", "")

            # 2. Puxa o MCP (Google Tasks)
            tasks_response = await client.get("http://127.0.0.1:8002/tasks")
            tarefas_google = tasks_response.json().get("tasks", [])

            # 3. Puxa o MCP (Google Calendar)
            calendar_response = await client.get("http://127.0.0.1:8002/calendar")
            agenda_google = calendar_response.json().get("events", calendar_response.json().get("calendar", []))

            # 4. Monta o Super Prompt Solto Combinando Tudo
            data_atual = datetime.now().strftime("%d/%m/%Y")
            super_prompt = f"""
            Você é um Assistente Inteligente de Produtividade.
            data de hoje: {data_atual}
            
            DADOS DISPONÍVEIS:
            - Regras de Negócio (RAG): {contexto_regras}
            - Tarefas Pendentes (Google Tasks): {tarefas_google}
            - Compromissos/Eventos da Agenda (Google Calendar): {agenda_google}
            
            PERGUNTA DO USUÁRIO: "{request.query}"

            CRITÉRIOS DE CLASSIFICAÇÃO UNIVERSAL (Atenção máxima aqui):
            - SAÚDE E BEM-ESTAR (remédios, médicos, fisioterapia, tratamentos) são SEMPRE considerados "Urgentes e Importantes" (Prioridade 1).
            - COMPROMISSOS COM HORÁRIO (Agenda) para o dia de HOJE são inadiáveis e também Prioridade 1.
            - DEVERES ACADÊMICOS/PROFISSIONAIS (trabalhos, inscrições, relatórios) são "Importantes", mas vêm depois da saúde (Prioridade 2).
            - LAZER E ENTRETENIMENTO (videogame, TV) são "Não importantes" e devem ficar para o fim do dia.
            
            INSTRUÇÕES:
            1. Responda DIRETAMENTE à pergunta do usuário usando os DADOS DISPONÍVEIS (cruze tanto as tarefas quanto os eventos da agenda).
            2. Se o usuário pedir para listar compromissos ou tarefas de um dia específico, filtre e mostre apenas os daquele dia.
            3. Se o usuário pedir priorização, crie uma lista usando as Regras de Negócio para ordenar o dia dele.
            4. Ignore dados ou anotações que não sejam tarefas ou compromissos reais, a menos que o usuário pergunte especificamente.
            5. Seja direto, conciso e mantenha um tom profissional.
            """
            
            # 5. Chama o LLM para responder
            final_response = await client.post("http://127.0.0.1:8003/generate", json={"prompt": super_prompt})
            
            return {"prioritized_response": final_response.json().get("response")}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha no fluxo de priorização com Tasks/Calendar: {str(e)}")