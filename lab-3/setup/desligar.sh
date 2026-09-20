#!/bin/bash

# Captura os IDs pesquisando explicitamente pelos nomes dos containers
CONTAINER_IDS=($(docker ps --filter "name=master" --filter "name=worker" -q))

# Verifica se encontrou algum container
if [ ${#CONTAINER_IDS[@]} -eq 0 ]; then
    echo "Nenhum container encontrado. Certifique-se de que estão rodando com 'docker ps'."
    exit 1
fi

# Imprime os IDs encontrados e desliga os containers
for id in "${CONTAINER_IDS[@]}"; do
    echo "Desligando container $id"
    docker stop "$id"
done

echo \n

for id in "${CONTAINER_IDS[@]}"; do 
    echo "Excluindo container $id."
    docker rm -f $id
done

echo "Programa finalizado!"