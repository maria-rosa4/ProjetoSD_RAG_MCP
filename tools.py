# Esse código é responsável pela simulação do MCP, ou seja, do recebimento dos dados externos (calendar e tasks)
# função para simular as tarefas
def get_tasks():
    return [
        "Estudar sistemas distribuídos",
        "Fazer trabalho de IA",
        "Ir à academia"
    ]

# função para simular as agendas do calendar
def get_calendar():
    return [
        "Reunião às 10h",
        "Aula às 14h"
    ]

# para testar o funcionamento
if __name__ == "__main__":
    print(get_tasks())
    print(get_calendar())