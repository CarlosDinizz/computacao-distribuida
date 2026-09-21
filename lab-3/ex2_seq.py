import random
import time

N = 10_000_000
dentro = 0

inicio = time.time()
for i in range(N):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
        dentro += 1

pi_estimado = 4.0 * dentro / N
fim = time.time()

print(f"Pi aproximado: {pi_estimado:.6f}")
print(f"Tempo experimental: {(fim - inicio) * 1000:.2f} ms")
