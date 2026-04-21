# se a execução de scripts tiver desabilitada no sistema, rodar: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Esse codigo é responsável pelo RAG, ou seja, pela base de conhecimento

from chromadb import Client

client = Client() # conecta ao banco

collection = client.create_collection(name="regras") # onde estamos guardando os textos

# adicionando os textos na coleção e indexando
collection.add(
    documents=[
        "Tarefas urgentes e importantes devem ser feitas primeiro",
        "Tarefas importantes devem ser planejadas",
        "Tarefas urgentes e não importantes podem ser delegadas",
        "Tarefas não importantes devem ser evitadas"
    ],
    ids=["1", "2", "3", "4"]
)

# função que recebe a pergunta realizada via interface, transforma a pergunta em vetor, compara com os textos e retorna o mais parecido
def buscar_contexto(pergunta):
    resultado = collection.query(
        query_texts=[pergunta],
        n_results=2
    )
    return resultado["documents"]

# só pra testar o funcionamento
if __name__ == "__main__":
    pergunta = "O que devo fazer primeiro?"
    contexto = buscar_contexto(pergunta)
    print(contexto)