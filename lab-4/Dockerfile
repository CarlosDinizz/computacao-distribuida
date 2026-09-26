FROM ubuntu:22.04 AS base

RUN apt update && apt install -y openmpi-bin libopenmpi-dev openssh-server sudo figlet net-tools iputils-ping vim python3 python3-pip
RUN pip install mpi4py
RUN pip install numpy

FROM base AS build

RUN useradd -m -s /bin/bash mpiuser && \
    echo "mpiuser:mpi123" | chpasswd && \
    mkdir /var/run/sshd

COPY --chown=mpiuser hosts /home/mpiuser/

EXPOSE 22
CMD service ssh start && sleep infinity