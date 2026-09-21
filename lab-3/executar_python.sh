#!/bin/bash

ls 

# Entra na pasta do setup
cd ./setup/ || exit 1

# Captura os IDs pesquisando explicitamente pelos nomes dos containers
CONTAINER_IDS=($(docker ps --filter "name=master" --filter "name=worker" -q))

# Verifica se encontrou algum container
if [ ${#CONTAINER_IDS[@]} -eq 0 ]; then
    echo "Nenhum container encontrado. Inicializando containers..."
    ./iniciar.sh
fi

NODES="master worker1 worker2 worker3"

for node in $NODES; do
    # Copia os arquivos diretamente da pasta atual (setup)
    docker cp ../ex2.py "$node:/home/mpiuser/"
    docker cp hosts "$node:/home/mpiuser/"
    
    # Ajusta as permissões dentro do container
    docker compose exec "$node" chown -R mpiuser:mpiuser /home/mpiuser/
done

echo \ 
echo \

# Execução do programa MPI a partir do nó master
docker compose exec master su - mpiuser -c \
    "mpirun --hostfile hosts -np 4 \
     --mca plm_rsh_args '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' \
     python3 ex2.py"
