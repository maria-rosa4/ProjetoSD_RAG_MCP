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


# MEMÓRIA GLOBAL DO ASSISTENTE

historico_conversa = []

@app.get("/health")
async def health_check():
    return {"status": "orchestrator is running"}

@app.post("/prioritize")
async def prioritize_tasks(request: PrioritizeRequest):
    global historico_conversa
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        

        # PASSO 1: O PORTEIRO (Classificação de Intenção Binária)

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

        # PASSO 2: A BIFURCAÇÃO (O Guardrail)
    
        if "[Erro" in intencao:
            return {"prioritized_response": f"Ops! O Porteiro encontrou um problema no motor da IA: {intencao}"}

        if "0" in intencao or "1" not in intencao:
            resposta_padrao = (
                "Olá! Eu sou um Assistente Especializado em Produtividade.\n\n"
                "Meu escopo é estritamente focado em organizar suas tarefas do Google, "
                "analisar sua agenda e definir prioridades para o seu dia.\n\n"
                "Como posso ajudar a organizar seu trabalho hoje?"
            )
            return {"prioritized_response": resposta_padrao}
        
        # PASSO 3: O FLUXO NORMAL E INTELIGENTE (Tasks + Calendar)

        try:
            # 1. Puxa os Dados
            rag_response = await client.post("http://127.0.0.1:8001/context", json={"query": request.query})
            contexto_regras = rag_response.json().get("context", "")

            tasks_response = await client.get("http://127.0.0.1:8002/tasks")
            tarefas_google = tasks_response.json().get("tasks", [])

            calendar_response = await client.get("http://127.0.0.1:8002/calendar")
            agenda_google = calendar_response.json().get("events", calendar_response.json().get("calendar", []))

            # 2. Prepara a Data e o Histórico
            data_atual = datetime.now().strftime("%d/%m/%Y")
            historico_texto = "\n".join(historico_conversa) if historico_conversa else "Nenhuma conversa anterior."

            # 3. Monta o Prompt com Memória
            super_prompt = f"""
            Você é um Assistente Inteligente de Produtividade.
            data de hoje: {data_atual}
            
            HISTÓRICO DA CONVERSA:
            {historico_texto}
            
            DADOS DISPONÍVEIS:
            - Regras de Negócio (RAG): {contexto_regras}
            - Tarefas Pendentes (Google Tasks): {tarefas_google}
            - Compromissos/Eventos da Agenda (Google Calendar): {agenda_google}
            
            PERGUNTA ATUAL DO USUÁRIO: "{request.query}"

            REGRA DE CLASSIFICAÇÃO OBRIGATÓRIA (Mapeie TODAS as tarefas nestas 4 categorias):
            1. SAÚDE E BEM-ESTAR (ex: remédios, fisioterapia, médicos, exames, tratamentos): É SEMPRE a Prioridade 1 Máxima.
            2. COMPROMISSOS DE AGENDA: É Prioridade 1 (Cruze a data de HOJE com a data da Agenda).
            3. TRABALHO/ESTUDO (ex: infraestrutura, suporte, disciplinas, trainee, projetos): É Prioridade 2 (Importante, mas vem DEPOIS da saúde).
            4. LAZER (ex: videogame, hobbies, descanso): Prioridade 3 (Não urgente).
            
            INSTRUÇÕES:
            1. Leia o HISTÓRICO DA CONVERSA para entender o contexto, mas responda DIRETAMENTE à PERGUNTA ATUAL DO USUÁRIO.
            2. Se o usuário pedir explicação sobre uma tarefa específica, explique o que ela é e por que tem essa prioridade.
            3. Você DEVE listar e classificar TODAS as tarefas que vieram do Google Tasks quando solicitado. NUNCA omita ou esconda uma tarefa.
            4. Seja direto, conciso e mantenha um tom profissional.
            """
            
            # 4. Chama o LLM para responder
            final_response = await client.post("http://127.0.0.1:8003/generate", json={"prompt": super_prompt})
            resposta_texto = final_response.json().get("response")

            # 5. Salva na memória (limita a 4 mensagens para o prompt não explodir de tamanho)
            historico_conversa.append(f"Usuário: {request.query}")
            historico_conversa.append(f"Assistente: {resposta_texto}")
            if len(historico_conversa) > 4:
                historico_conversa = historico_conversa[-4:]

            return {"prioritized_response": resposta_texto}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha no fluxo de priorização com Tasks/Calendar: {str(e)}")