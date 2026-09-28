from mpi4py import MPI
import numpy as np
import time
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Parâmetros padrão de teste
LINHAS = 2000
COLUNAS = 2000
LIMIAR_SUSPEITO = 200
LIMIAR_ALTO = 230
PCT_CRITICO = 5.0 # percentual em %

imagem_completa = None
parametros = None

t_inicio = time.time()

# Etapa 2 & 3: Processo 0 gera radiografia e define configurações
if rank == 0:
    print(f"[Master] Inicializando análise com {size} processos MPI...")
    # Geração simulada da radiografia
    imagem_completa = np.random.randint(30, 90, size=(LINHAS, COLUNAS), dtype=np.uint8)

    # Injeção de foco suspeito artificial no pulmão direito
    imagem_completa[600:900, 1200:1600] = np.random.randint(180, 245, size=(300, 400), dtype=np.uint8)
    
    parametros = {
        'linhas': LINHAS,
        'colunas': COLUNAS,
        'limiar_suspeito': LIMIAR_SUSPEITO,
        'limiar_alto': LIMIAR_ALTO,
        'pct_critico': PCT_CRITICO
    }

# Etapa 3: Difusão dos parâmetros via Broadcast
parametros = comm.bcast(parametros, root=0)

# Etapa 4: Sincronização inicial
comm.Barrier()

# Etapa 5: Divisão e distribuição da imagem (suporta divisão não exata)
blocos_divididos = None
if rank == 0:
    # array_split divide o array em partes o mais iguais possível, mesmo sem divisão exata
    blocos_divididos = np.array_split(imagem_completa, size, axis=0)

# Cada processo recebe o seu bloco correspondente
bloco_local = comm.scatter(blocos_divididos, root=0)
linhas_locais = bloco_local.shape[0]

# Etapa 6 & 7: Processamento e classificação local
total_local = bloco_local.size
soma_local = int(np.sum(bloco_local))
max_local = int(np.max(bloco_local))

col_meio = parametros['colunas'] // 2
esq_mask = bloco_local[:, :col_meio] > parametros['limiar_suspeito']
dir_mask = bloco_local[:, col_meio:] > parametros['limiar_suspeito']
suspeitos_esq = int(np.sum(esq_mask))
suspeitos_dir = int(np.sum(dir_mask))
suspeitos_local = suspeitos_esq + suspeitos_dir
altamente_suspeitos_local = int(np.sum(bloco_local > parametros['limiar_alto']))

# Classificação da faixa
pct_suspeito = (suspeitos_local / total_local) * 100.0
if pct_suspeito >= parametros['pct_critico']:
    classificacao_local = "CRÍTICA"
elif pct_suspeito >= 1.0:
    classificacao_local = "ATENÇÃO"
else:
    classificacao_local = "NORMAL"

# Etapa 8: Simulação de heterogeneidade de nós
if rank % 2 != 0:
    time.sleep(0.3 * rank)

# Etapa 9: Sincronização pré-consolidação
comm.Barrier()

# Etapa 10: Consolidação numérica com MPI_Reduce
total_pixels_global = comm.reduce(total_local, op=MPI.SUM, root=0)
soma_global = comm.reduce(soma_local, op=MPI.SUM, root=0)
max_global = comm.reduce(max_local, op=MPI.MAX, root=0)
suspeitos_global = comm.reduce(suspeitos_local, op=MPI.SUM, root=0)
altos_global = comm.reduce(altamente_suspeitos_local, op=MPI.SUM, root=0)
esq_global = comm.reduce(suspeitos_esq, op=MPI.SUM, root=0)
dir_global = comm.reduce(suspeitos_dir, op=MPI.SUM, root=0)

# Etapa 11: Coleta de estatísticas por processo com MPI_Gather
# Coleta do deslocamento de linhas reais para cada processo
linhas_acumuladas = comm.gather(linhas_locais, root=0)

if rank == 0:
    inicio_acc = 0
    intervalos_linhas = []
    for l in linhas_acumuladas:
        intervalos_linhas.append((inicio_acc, inicio_acc + l - 1))
        inicio_acc += l
else:
    intervalos_linhas = None

intervalo_local = comm.scatter(intervalos_linhas, root=0)

relatorio_local = {
    'rank': rank,
    'linhas_inicio': intervalo_local[0],
    'linhas_fim': intervalo_local[1],
    'pixels': total_local,
    'suspeitos': suspeitos_local,
    'classificacao': classificacao_local,
    'max_local': max_local
}
todos_relatorios = comm.gather(relatorio_local, root=0)

# Etapa 12: Relatório final emitido pelo processo 0
if rank == 0:
    t_total = (time.time() - t_inicio) * 1000.0
    media_intensidade = soma_global / total_pixels_global
    taxa_comprometida = (suspeitos_global / total_pixels_global) * 100.0

    print("\n" + "="*60)
    print("      RELATÓRIO CONSOLIDADO DE TRIAGEM DISTRIBUÍDA")
    print("="*60)
    print(f"Dimensões do Exame       : {LINHAS} x {COLUNAS} pixels")
    print(f"Processos MPI Utilizados: {size}")
    print(f"Tempo Total de Execução  : {t_total:.2f} ms")
    print(f"Intensidade Média Global: {media_intensidade:.2f} (Máxima: {max_global})")
    print(f"Total de Pixels Suspeitos: {suspeitos_global} ({taxa_comprometida:.2f}%)")
    print(f"  - Pulmão Esquerdo      : {esq_global} suspeitos")
    print(f"  - Pulmão Direito       : {dir_global} suspeitos")

    lado_critico = "Direito" if dir_global > esq_global else "Esquerdo" if esq_global > dir_global else "Equilibrado"
    print(f"Maior Concentração       : Pulmão {lado_critico}")
    print("\n--- Auditoria por Processo (Faixas) ---")
    for rel in todos_relatorios:
        print(f"Processo {rel['rank']:02d} | Linhas [{rel['linhas_inicio']:04d}-{rel['linhas_fim']:04d}] | "
              f"Suspeitos: {rel['suspeitos']:05d} | Máx: {rel['max_local']:03d} | Faixa: {rel['classificacao']}")
    print("="*60 + "\n")
