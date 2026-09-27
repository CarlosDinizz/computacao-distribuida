docker compose exec master service ssh start
docker compose exec worker1 service ssh start
docker compose exec worker2 service ssh start
docker compose exec worker3 service ssh start

docker cp ./src/lab4.py master:/home/mpiuser/
docker cp ./src/lab4.py worker1:/home/mpiuser/
docker cp ./src/lab4.py worker2:/home/mpiuser/
docker cp ./src/lab4.py worker3:/home/mpiuser/

# 4. Execução do programa MPI a partir do host (Codespaces)
docker compose exec master su - mpiuser -c "mpirun --hostfile hosts -np 3 python3 lab4.py"
