# Este código é onde tudo se junta RAG (conhecimento) + MCP (dados reais) + LLM (resposta)

# conectando com os módulos:
from rag import buscar_contexto
from tools import get_tasks, get_calendar
from llm import gerar_resposta

def processar(pergunta):
    contexto = buscar_contexto(pergunta) # pega a pergunta e busca regras relevantes
    tasks = get_tasks() # pega a lista de tarefas
    events = get_calendar() # pega a agenda do dia

    # aqui é criado um super contexto, ou seja, o modelo vai ler regras + dados reais + pergunta
    # isso faz com que o modelo seja contextualizado e não genérico
    prompt = f"""
    Você é um assistente que ajuda a priorizar tarefas de forma objetiva.

    Siga EXATAMENTE estas regras:
    - Classifique tarefas em: Alta, Média ou Baixa prioridade
    - NÃO invente tarefas
    - NÃO repita categorias vazias
    - Seja direto e organizado
    - Use as regras fornecidas como base principal

    Regras de priorização:
    {contexto}

    Tarefas:
    {tasks}

    Agenda:
    {events}

    Pergunta:
    {pergunta}

    Formato da resposta:

    Prioridade Alta:
    - tarefa 1
    - tarefa 2

    Prioridade Média:
    - tarefa 1

    Prioridade Baixa:
    - tarefa 1

    Explique brevemente o motivo das prioridades.
    """

    return gerar_resposta(prompt) # aqui envia tudo para o modelo via ollama

# testando o funcionamento localmente
if __name__ == "__main__":
    resposta = processar("O que devo fazer hoje?")
    print(resposta)