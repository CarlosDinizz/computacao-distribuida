from mpi4py import MPI
from random import randint, random
import threading
from time import time
N = 600

A = [[random() for _ in range(N)] for _ in range(N)]
B = [[random() for _ in range(N)] for _ in range(N)]
C = [[0]*N for _ in range(N)]
inicio = time()
for i in range(N):
    for j in range(N):
        for k in range(N):
            C[i][j] += A[i][k] * B[k][j]
fim = time()
print(f"Tempo sequencial: {(fim - inicio) * 1000:.2f} ms")


THREADS = 4
A = [[random() for _ in range(N)] for _ in range(N)]
B = [[random() for _ in range(N)] for _ in range(N)]
C = [[0]*N for _ in range(N)]

def calcular(inicio, fim):
    for i in range(inicio, fim):
        for j in range(N):
            for k in range(N):
                C[i][j] += A[i][k] * B[k][j]
inicio = time()
threads = []
linhas_por_thread = N // THREADS
for t in range(THREADS):
    ini = t * linhas_por_thread
    fim_t = N if t == THREADS - 1 else (t + 1) * linhas_por_thread
    th = threading.Thread(target=calcular, args=(ini, fim_t))
    threads.append(th)
    th.start()
for th in threads:
    th.join()
fim = time()
print(f"Tempo com threads: {(fim - inicio) * 1000:.2f} ms")

def calcular_matriz(matrizA, matrizB, N, inicio, fim, resultante):
    for i in range(inicio, fim):
        for j in range(N):
            for k in range(N):
                resultante[i][j] += matrizA[i][k] * matrizB[k][j]

tempo_inicio = time()

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()



if rank == 0:
    matrizA = [[randint(0, 100) for _ in range(N)] for _ in range(N)]
    matrizB = [[randint(0, 100) for _ in range(N)] for _ in range(N)]

else:
    matrizA = None
    matrizB = None

matrizA = comm.bcast(matrizA, root=0)
matrizB = comm.bcast(matrizB, root=0)


n = N//size
inicio = rank * n
fim = (rank + 1) * n

matrizC = [[0] * N for _ in range(N)]

calcular_matriz(matrizA, matrizB, n, inicio, fim, matrizC)

parte_calculada = matrizC[inicio:fim]
total = comm.gather(parte_calculada, root=0)

if rank == 0:
    matrizC_final = []
    for l in total:
        matrizC_final.extend(l)

    tempo_fim = time()
    print(f"Tempo distribuído: {(tempo_fim - tempo_inicio) * 1000:.2f}")
    

# 2. Finaliza o ambiente MPI (opcional; mpi4py finaliza automaticamente ao encerrar)
MPI.Finalize()