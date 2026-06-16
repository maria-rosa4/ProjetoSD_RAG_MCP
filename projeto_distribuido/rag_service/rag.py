from chromadb import Client

client = Client()

def obter_ou_criar_colecao():
    try:
        # Tenta deletar se existir para resetar ou apenas tenta pegar
        # Para simplificar no ambiente do aluno, vamos tentar obter, se falhar criamos
        try:
            return client.get_collection(name="regras")
        except:
            col = client.create_collection(name="regras")
            col.add(
                documents=[
                    "Tarefas urgentes e importantes devem ser feitas primeiro",
                    "Tarefas importantes devem ser planejadas",
                    "Tarefas urgentes e não importantes podem ser delegadas",
                    "Tarefas não importantes devem ser evitadas"
                ],
                ids=["1", "2", "3", "4"]
            )
            return col
    except Exception as e:
        print(f"Erro ao inicializar ChromaDB: {e}")
        return None

collection = obter_ou_criar_colecao()

def buscar_contexto(pergunta):
    if collection is None:
        return ["Erro na base RAG"]
    try:
        resultado = collection.query(
            query_texts=[pergunta],
            n_results=2
        )
        return resultado["documents"]
    except Exception as e:
        return [f"Erro na busca: {str(e)}"]
