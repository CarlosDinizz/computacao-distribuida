#!/usr/bin/env python3
"""
Atividade Lab - Processamento Distribuído de Imagens Médicas com MPI
Disciplina de Computação Distribuída - Prof. Alcides / Prof. Mário

Simulação computacional de triagem de radiografias de tórax usando mpi4py.
Implementa os cinco mecanismos coletivos exigidos pelo enunciado - Bcast,
Scatter, Barrier, Reduce e Gather - seguindo as 12 etapas descritas.

IMPORTANTE: esta é uma simulação educacional de paralelismo de dados e
padrões de comunicação MPI. NÃO constitui um sistema de diagnóstico
médico real.
"""

import argparse
import csv
import os
import time

import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

t_inicio = time.time()

# ---------------------------------------------------------------------------
# Etapas 2 e 3 - Geração da radiografia simulada e definição dos parâmetros
# (executado apenas pelo processo root; os demais recebem tudo via Bcast)
# ---------------------------------------------------------------------------
parametros = None
imagem_completa = None

if rank == 0:
    parser = argparse.ArgumentParser(description="Triagem distribuída de radiografias (MPI)")
    parser.add_argument("--linhas", type=int, default=2000)
    parser.add_argument("--colunas", type=int, default=2000)
    parser.add_argument("--limiar-suspeito", type=int, default=200)
    parser.add_argument("--limiar-alto", type=int, default=230)
    parser.add_argument("--pct-critico", type=float, default=5.0)
    parser.add_argument("--sleep-fator", type=float, default=0.5,
                         help="Fator de latência artificial para ranks ímpares (Etapa 8)")
    parser.add_argument("--log-csv", type=str, default=None,
                         help="Se informado, acrescenta uma linha [linhas,colunas,processos,tempo_ms] neste CSV")
    parser.add_argument("--seed", type=int, default=None,
                         help="Semente do gerador aleatório, para comparações justas entre execuções")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    print(f"[Master] Inicializando análise com {size} processo(s) MPI "
          f"({args.linhas}x{args.colunas})...")

    # Fundo/mediastino: intensidades médias/baixas plausíveis (tecido mole/ar)
    imagem_completa = np.random.randint(30, 90, size=(args.linhas, args.colunas), dtype=np.uint8)

    # Injeção controlada de foco suspeito (simulando consolidação), em posição
    # PROPORCIONAL ao tamanho da imagem. O template original usava índices fixos
    # (600:900, 1200:1600), o que funciona para 2000x2000 mas fica fora dos limites
    # (e some silenciosamente) em imagens menores, como os 500x500 da Questão 6.
    li0, li1 = int(args.linhas * 0.30), int(args.linhas * 0.45)
    co0, co1 = int(args.colunas * 0.60), int(args.colunas * 0.80)
    imagem_completa[li0:li1, co0:co1] = np.random.randint(
        180, 245, size=(li1 - li0, co1 - co0), dtype=np.uint8
    )

    parametros = {
        "linhas": args.linhas,
        "colunas": args.colunas,
        "limiar_suspeito": args.limiar_suspeito,
        "limiar_alto": args.limiar_alto,
        "pct_critico": args.pct_critico,
        "sleep_fator": args.sleep_fator,
        "log_csv": args.log_csv,
    }

# Etapa 3 - Difusão dos parâmetros via Broadcast
parametros = comm.bcast(parametros, root=0)

# Etapa 4 - Sincronização inicial: garante que ninguém comece a tratar dados
# de imagem antes que TODOS tenham os parâmetros de calibração.
comm.Barrier()

# ---------------------------------------------------------------------------
# Etapa 5 - Particionamento e distribuição com Scatter
#
# Desafio de divisibilidade (Questão 9 do enunciado): em vez de exigir que
# 'linhas' seja múltiplo exato de 'size' (o que quebraria com, por exemplo,
# 2003 linhas e 4 processos), usamos FATIAMENTO BALANCEADO via
# np.array_split - uma das estratégias explicitamente aceitas no enunciado.
# Ele distribui o resto das linhas entre os primeiros processos (diferença
# de no máximo 1 linha entre fatias), sem descartar dados e sem precisar de
# padding artificial. Cada pacote enviado carrega também o intervalo de
# linhas [inicio, fim] correspondente na imagem original, para que cada
# processo saiba sua posição sem precisar de comunicação extra.
# ---------------------------------------------------------------------------
pacotes = None
if rank == 0:
    blocos = np.array_split(imagem_completa, size, axis=0)
    linha_atual = 0
    pacotes = []
    for bloco in blocos:
        n = bloco.shape[0]
        pacotes.append({
            "dados": bloco,
            "linha_inicio": linha_atual,
            "linha_fim": linha_atual + n - 1,
        })
        linha_atual += n

pacote_local = comm.scatter(pacotes, root=0)
bloco_local = pacote_local["dados"]
linha_inicio_global = pacote_local["linha_inicio"]
linha_fim_global = pacote_local["linha_fim"]

# ---------------------------------------------------------------------------
# Etapa 6 - Análise local de cada processo
# ---------------------------------------------------------------------------
total_local = bloco_local.size
soma_local = int(np.sum(bloco_local, dtype=np.int64))
max_local = int(np.max(bloco_local))

col_meio = parametros["colunas"] // 2
esq_mask = bloco_local[:, :col_meio] > parametros["limiar_suspeito"]
dir_mask = bloco_local[:, col_meio:] > parametros["limiar_suspeito"]
suspeitos_esq = int(np.sum(esq_mask))
suspeitos_dir = int(np.sum(dir_mask))
suspeitos_local = suspeitos_esq + suspeitos_dir
altamente_suspeitos_local = int(np.sum(bloco_local > parametros["limiar_alto"]))

# ---------------------------------------------------------------------------
# Etapa 7 - Classificação heurística da faixa local
#
# O enunciado define "Crítica" como taxa >= percentual_critico OU "presença
# expressiva de pixels altamente suspeitos", sem dar um número exato para
# essa segunda condição. Escolha de projeto adotada aqui: consideramos
# expressiva quando os pixels altamente suspeitos (> limiar_alto) sozinhos
# já somam metade do percentual crítico. Isso está documentado aqui para
# poder ser citado/justificado no relatório.
# ---------------------------------------------------------------------------
pct_suspeito = (suspeitos_local / total_local) * 100.0
pct_altamente_suspeito = (altamente_suspeitos_local / total_local) * 100.0

if pct_suspeito >= parametros["pct_critico"] or pct_altamente_suspeito >= (parametros["pct_critico"] / 2):
    classificacao_local = "CRÍTICA"
elif pct_suspeito >= 1.0:
    classificacao_local = "ATENÇÃO"
else:
    classificacao_local = "NORMAL"

# ---------------------------------------------------------------------------
# Etapa 8 - Simulação de heterogeneidade de hardware
# Ranks ímpares pausam proporcionalmente ao próprio rank; ranks pares seguem
# sem pausa artificial - reproduz assimetrias típicas de clusters reais.
# ---------------------------------------------------------------------------
if rank % 2 != 0:
    time.sleep(parametros["sleep_fator"] * rank)

# Etapa 9 - Sincronização pré-consolidação: evidencia o straggler effect,
# já que ninguém passa da barreira até o nó mais lento chegar.
comm.Barrier()

# ---------------------------------------------------------------------------
# Etapa 10 - Consolidação numérica global com Reduce
# ---------------------------------------------------------------------------
total_pixels_global = comm.reduce(total_local, op=MPI.SUM, root=0)
soma_global = comm.reduce(soma_local, op=MPI.SUM, root=0)
max_global = comm.reduce(max_local, op=MPI.MAX, root=0)
suspeitos_global = comm.reduce(suspeitos_local, op=MPI.SUM, root=0)
altos_global = comm.reduce(altamente_suspeitos_local, op=MPI.SUM, root=0)
esq_global = comm.reduce(suspeitos_esq, op=MPI.SUM, root=0)
dir_global = comm.reduce(suspeitos_dir, op=MPI.SUM, root=0)

# ---------------------------------------------------------------------------
# Etapa 11 - Coleta de relatórios descritivos com Gather
# ---------------------------------------------------------------------------
relatorio_local = {
    "rank": rank,
    "linhas_inicio": linha_inicio_global,
    "linhas_fim": linha_fim_global,
    "pixels": total_local,
    "suspeitos": suspeitos_local,
    "altamente_suspeitos": altamente_suspeitos_local,
    "classificacao": classificacao_local,
    "max_local": max_local,
}
todos_relatorios = comm.gather(relatorio_local, root=0)

# ---------------------------------------------------------------------------
# Etapa 12 - Relatório final consolidado e diagnóstico (apenas root)
# ---------------------------------------------------------------------------
if rank == 0:
    t_total_ms = (time.time() - t_inicio) * 1000.0
    media_intensidade = soma_global / total_pixels_global
    taxa_comprometida = (suspeitos_global / total_pixels_global) * 100.0
    taxa_altos = (altos_global / total_pixels_global) * 100.0

    if taxa_comprometida >= parametros["pct_critico"] or taxa_altos >= (parametros["pct_critico"] / 2):
        classificacao_geral = "QUADRO CRÍTICO / ALTA CONCENTRAÇÃO DE ALTERAÇÕES"
    elif taxa_comprometida >= 1.0:
        classificacao_geral = "ATENÇÃO CLÍNICA"
    else:
        classificacao_geral = "SEM INDÍCIOS RELEVANTES"

    lado_critico = ("Direito" if dir_global > esq_global
                     else "Esquerdo" if esq_global > dir_global
                     else "Equilibrado")

    print("\n" + "=" * 60)
    print(" RELATÓRIO CONSOLIDADO DE TRIAGEM DISTRIBUÍDA")
    print("=" * 60)
    print(f"Dimensões do Exame        : {parametros['linhas']} x {parametros['colunas']} pixels")
    print(f"Processos MPI Utilizados  : {size}")
    print(f"Limiares Adotados         : suspeito > {parametros['limiar_suspeito']}, "
          f"alto > {parametros['limiar_alto']}, crítico >= {parametros['pct_critico']}%")
    print(f"Tempo Total de Execução   : {t_total_ms:.2f} ms")
    print(f"Intensidade Média Global  : {media_intensidade:.2f} (Máxima: {max_global})")
    print(f"Total de Pixels Suspeitos : {suspeitos_global} ({taxa_comprometida:.2f}%)")
    print(f"  - Altamente suspeitos   : {altos_global} ({taxa_altos:.2f}%)")
    print(f"  - Pulmão Esquerdo       : {esq_global} suspeitos")
    print(f"  - Pulmão Direito        : {dir_global} suspeitos")
    print(f"Maior Concentração        : Pulmão {lado_critico}")
    print(f"Classificação Geral       : {classificacao_geral}")

    print("\n--- Auditoria por Processo (Faixas) ---")
    for rel in sorted(todos_relatorios, key=lambda r: r["rank"]):
        print(f"Processo {rel['rank']:02d} | Linhas [{rel['linhas_inicio']:04d}-{rel['linhas_fim']:04d}] | "
              f"Suspeitos: {rel['suspeitos']:05d} | Altos: {rel['altamente_suspeitos']:04d} | "
              f"Máx: {rel['max_local']:03d} | Faixa: {rel['classificacao']}")
    print("=" * 60 + "\n")

    if parametros["log_csv"]:
        novo = not os.path.exists(parametros["log_csv"])
        with open(parametros["log_csv"], "a", newline="") as f:
            w = csv.writer(f)
            if novo:
                w.writerow(["linhas", "colunas", "processos", "tempo_ms", "classificacao_geral"])
            w.writerow([parametros["linhas"], parametros["colunas"], size,
                        f"{t_total_ms:.2f}", classificacao_geral])
