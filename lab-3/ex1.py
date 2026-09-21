
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