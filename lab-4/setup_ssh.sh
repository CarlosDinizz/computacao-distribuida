#!/bin/bash
echo "Gerando chave no master..."
docker compose exec master sudo -u mpiuser ssh-keygen -t rsa -N "" -f /home/mpiuser/.ssh/id_rsa

PUBKEY=$(docker compose exec master cat /home/mpiuser/.ssh/id_rsa.pub)

for node in worker1 worker2 worker3; do
    echo "Configurando $node..."
    echo "$PUBKEY" | docker compose exec -T $node bash -c "
        mkdir -p /home/mpiuser/.ssh &&
        cat >> /home/mpiuser/.ssh/authorized_keys &&
        chown -R mpiuser:mpiuser /home/mpiuser/.ssh &&
        chmod 700 /home/mpiuser/.ssh &&
        chmod 600 /home/mpiuser/.ssh/authorized_keys
    "
done

docker compose exec master bash -c "
  echo -e 'Host worker1 worker2 worker3\n
  StrictHostKeyChecking no' >> /home/mpiuser/.ssh/config
"

echo "SSH configurado."