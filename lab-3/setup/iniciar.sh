#!/bin/bash
set -e

NODES="master worker1 worker2 worker3"

# 1. Inicialização dos containers e serviço SSH
docker compose up -d

for node in $NODES; do
    docker compose exec "$node" service ssh start
done

# 2. Instalação das dependências (pip e mpi4py) nos nós do cluster
for node in $NODES; do
    docker compose exec "$node" apt update
    docker compose exec "$node" apt install -y python3-pip
    docker compose exec "$node" python3 -m pip install mpi4py
done

# 3. Transferência do código-fonte e do hostfile para todos os nós
for node in $NODES; do
    docker cp ../programa.py "$node:/home/mpiuser/"
    docker cp hosts "$node:/home/mpiuser/"
done

# 4. Configuração do SSH sem senha entre os nós
docker compose exec -u mpiuser master bash -c \
    "mkdir -p /home/mpiuser/.ssh && \
     [ -f /home/mpiuser/.ssh/id_rsa ] || ssh-keygen -t rsa -N '' -f /home/mpiuser/.ssh/id_rsa"

docker cp master:/home/mpiuser/.ssh/id_rsa.pub ./id_rsa.pub

for node in $NODES; do
    docker cp id_rsa.pub "$node:/tmp/id_rsa.pub"
    docker compose exec "$node" bash -c \
        "mkdir -p /home/mpiuser/.ssh && \
         cat /tmp/id_rsa.pub >> /home/mpiuser/.ssh/authorized_keys && \
         chmod 700 /home/mpiuser/.ssh && \
         chmod 600 /home/mpiuser/.ssh/authorized_keys"
done

rm -f id_rsa.pub

# 5. Ajuste de permissões (docker cp grava como root)
for node in $NODES; do
    docker compose exec "$node" chown -R mpiuser:mpiuser /home/mpiuser
done

# 6. Execução do programa MPI a partir do host
docker compose exec master su - mpiuser -c \
    "mpirun --hostfile hosts -np 4 \
     --mca plm_rsh_args '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' \
     python3 programa.py"