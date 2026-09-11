from mpi4py import MPI
# 1. Inicializa o ambiente de execução MPI (gerenciado ao importar mpi4py)
comm = MPI.COMM_WORLD
# Obtenção do tamanho do comunicador e do rank do processo atual
size = comm.Get_size()
rank = comm.Get_rank()
print(f"Processo {rank} de {size}")
# 2. Finaliza o ambiente MPI (opcional; mpi4py finaliza automaticamente ao encerrar)
# MPI.Finalize()