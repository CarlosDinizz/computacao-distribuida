#include <mpi.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc, char** argv) {
    int rank, size;
    char hostname[256];

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    gethostname(hostname, sizeof(hostname));

    if (size < 26) {
        if (rank == 0) {
            printf("Erro: Este programa requer exatamente ou pelo menos 26 processos (-np 26).\n");
        }
        MPI_Finalize();
        return 1;
    }

    if (rank < 26) {
        char letter = 'A' + rank;
        
        // Loop com barreira para garantir que o alfabeto seja impresso em ordem legível
        for (int i = 0; i < 26; i++) {
            if (i == rank) {
                printf("\n[Processo Rank %d | Host: %s]\n", rank, hostname);
                fflush(stdout);
                
                char cmd[256];
                sprintf(cmd, "figlet '%c'", letter);
                system(cmd);
                
                fflush(stdout);
            }
            MPI_Barrier(MPI_COMM_WORLD);
        }
    }

    MPI_Finalize();
    return 0;
}