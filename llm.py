# Este código conecta o Python com o Ollama (modelo Llama 3), ou seja, transforma o código em uma mensagem para a IA
# código -> envia o prompt -> Ollama -> responde -> código
import requests

# função para receber um texto (prompt)
def gerar_resposta(prompt):
    response = requests.post( 
        "http://localhost:11434/api/generate", # enviando requisição para o ollama, esse endereço é o endereço local do Ollama
        json={
            "model": "llama3", # aqui indicamos qual o modelo queremos usar
            "prompt": prompt, # indicamos o que ele deve ler (nesse caso, um prompt)
            "stream": False # indica se necessita de resposta completa
        }
    )

    return response.json()["response"] # momento de recebimento da resposta >> o Ollama retorna um JSON

# testando o funcionamento
if __name__ == "__main__":
    resposta = gerar_resposta("Diga olá")
    print(resposta)