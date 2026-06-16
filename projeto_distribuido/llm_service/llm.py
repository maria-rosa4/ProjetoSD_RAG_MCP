# Este código conecta o Python com o Ollama (modelo Llama 3)
import requests

def gerar_resposta(prompt):
    try:
        response = requests.post( 
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            },
            timeout=180.0 # Evita que a requisição fique travada para sempre
        )
        
        dados = response.json()
        
        # Verifica se a resposta foi um sucesso
        if "response" in dados:
            return dados["response"]
        
        # Se o Ollama devolveu um erro (ex: modelo não encontrado), repassamos o erro de forma clara
        elif "error" in dados:
            return f"[Erro Interno do Ollama]: {dados['error']}"
            
        else:
            return f"[Retorno Inesperado do Ollama]: {dados}"

    except requests.exceptions.ConnectionError:
        return "[Erro Crítico]: Não foi possível conectar ao Ollama. Verifique se o aplicativo do Ollama está aberto e rodando no seu computador."
    except Exception as e:
        return f"[Erro no Serviço LLM]: {str(e)}"

# testando o funcionamento
if __name__ == "__main__":
    resposta = gerar_resposta("Diga olá")
    print(resposta)