from mpi4py import MPI
import random

# Inicialização do MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
#
# Função para gerar logs
#
def gerar_logs(qtd):
    ips = [f"192.168.1.{i}" for i in range(2,254)]
    endpoints = [
        "/",
        "/login",
        "/products",
        "/cart",
        "/checkout",
        "/api/users",
        "/api/orders"
    ]
    metodos = ["GET", "POST"]
    status = ["200", "200", "200", "404", "500"]

    logs = []
    # INSIRA AQUI O SEU CÓDIGO PARA GERAR OS DADOS DO LOG
    # RANDOMIZE OS IPS, ENDPOINTS, METODOS E STATUS

    for i in range (qtd):
        ipAleatorio = random.randint(2, len(ips) - 1)
        endpointAleatorio = random.randint(0, len(endpoints) - 1)
        metodoAleatorio = random.randint(0, 1)
        statusAleatorio = random.randint(0, len(status) - 1)

        novoLog = f"{ips[ipAleatorio]} {metodos[metodoAleatorio]} {endpoints[endpointAleatorio]} {status[statusAleatorio]}"
        logs.append(novoLog)
           
    return logs

#
# Processo 0 gera o dataset
#
logs_divididos = None
TOTAL_LOGS = 100000

if rank == 0:
    print("\nGerando dataset de logs...\n")
    logs = gerar_logs(TOTAL_LOGS)
    # DIVIDIR AQUI O DATASET ENTRE OS PROCESSOS
    # O NÓ MASTER TAMBÉM PROCESSA SUA PARTE DO DATASET
    logs_divididos = []
    tamanho = TOTAL_LOGS // size
    for i in range (size):
        logProcesso = logs[tamanho * i : tamanho * (i + 1)]
        logs_divididos.append(logProcesso)



    

#
# Distribuição usando Scatter
#
# DISTRIBUIR OS DADOS USANDO SCATTER
#

logs_locais = comm.scatter(logs_divididos, root=0)


#
# Processamento local em cada nó
#
# INSIRA AQUI O CÓDIGO DE PROCESSAMENTO LOCAL DO LOG
#

erros = 0
for log in logs_locais:
    partesLog = log.split(" ")
    statusEncontrado = partesLog[3]

    if statusEncontrado == "500":
        erros += 1
    elif statusEncontrado == "404":
        erros += 1


# Nós Master
# Imprime os resultados de cada nó worker e seu também
#
# A variável 'logs_locais' representa a fatia recebida e 'erros' o contador
print(f"Processo {rank} analisou {len(logs_locais)} linhas "
      f"e encontrou {erros} erros."
)
