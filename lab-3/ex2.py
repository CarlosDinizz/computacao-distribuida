import random
import sys
import time

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000_000

N_local = N // size
resto = N % size
if rank < resto:
    N_local += 1

comm.Barrier()
inicio = time.time()

random.seed(time.time_ns() ^ ((rank + 1) * 7919))

dentro_local = 0
for _ in range(N_local):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
        dentro_local += 1

dentro_total = comm.reduce(dentro_local, op=MPI.SUM, root=0)

if rank == 0:
    fim = time.time()
    pi_estimado = 4.0 * dentro_total / N
    tempo_ms = (fim - inicio) * 1000

    print(f"Processos utilizados   : {size}")
    print(f"Total de pontos (N)    : {N}")
    print(f"Pontos dentro do circulo: {dentro_total}")
    print(f"PI aproximado          : {pi_estimado:.6f}")
    print(f"Tempo distribuido MPI  : {tempo_ms:.2f} ms")
