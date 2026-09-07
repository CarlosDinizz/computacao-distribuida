# Relatório LAB 1

O programa em python foi executado no Codespaces do Github, que possui as seguintes configurações ao executar o comando lscpu:

```bash
Architecture:                x86_64
  CPU op-mode(s):            32-bit, 64-bit
  Address sizes:             48 bits physical, 48 bits virtual
  Byte Order:                Little Endian
CPU(s):                      2
  On-line CPU(s) list:       0,1
Vendor ID:                   AuthenticAMD
  Model name:                AMD EPYC 9V74 80-Core Processor
    CPU family:              25
    Model:                   17
    Thread(s) per core:      2
    Core(s) per socket:      1
    Socket(s):               1
    Stepping:                1
    BogoMIPS:                5192.25
    Flags:                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pd
                             pe1gb rdtscp lm constant_tsc rep_good nopl tsc_reliable nonstop_tsc cpuid extd_apicid aperfmperf tsc_known_freq pni pclmulqdq ssse
                             3 fma cx16 pcid sse4_1 sse4_2 movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm cmp_legacy svm cr8_legacy abm sse4a misali
                             gnsse 3dnowprefetch osvw topoext vmmcall fsgsbase bmi1 avx2 smep bmi2 erms invpcid rdseed adx smap clflushopt clwb sha_ni xsaveopt
                              xsavec xgetbv1 xsaves user_shstk clzero xsaveerptr rdpru arat npt nrip_save tsc_scale vmcb_clean flushbyasid decodeassists pausef
                             ilter pfthreshold v_vmsave_vmload umip vaes vpclmulqdq rdpid fsrm
Virtualization features:     
  Virtualization:            AMD-V
  Hypervisor vendor:         Microsoft
  Virtualization type:       full
Caches (sum of all):         
  L1d:                       32 KiB (1 instance)
  L1i:                       32 KiB (1 instance)
  L2:                        1 MiB (1 instance)
  L3:                        32 MiB (1 instance)
NUMA:                        
  NUMA node(s):              1
  NUMA node0 CPU(s):         0,1
Vulnerabilities:             
  Gather data sampling:      Not affected
  Indirect target selection: Not affected
  Itlb multihit:             Not affected
  L1tf:                      Not affected
  Mds:                       Not affected
  Meltdown:                  Not affected
  Mmio stale data:           Not affected
  Reg file data sampling:    Not affected
  Retbleed:                  Not affected
  Spec rstack overflow:      Vulnerable: Safe RET, no microcode
  Spec store bypass:         Vulnerable
  Spectre v1:                Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:                Mitigation; Retpolines; STIBP disabled; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected
  Srbds:                     Not affected
  Tsa:                       Vulnerable: Clear CPU buffers attempted, no microcode
  Tsx async abort:           Not affected
  Vmscape:                   Not affected
```

## Resultados

Uso com 2 processos:
```bash
@CarlosDinizz ➜ /workspaces/computacao-distribuida/lab-1.2 (main) $ mpirun --oversubscribe -np 2 python programa.py 

Gerando dataset de logs...

Processo 0 analisou 50000 linhas e encontrou 19966 erros.
Processo 1 analisou 50000 linhas e encontrou 19860 erros.
```

Uso com 4 processos:
```bash
@CarlosDinizz ➜ /workspaces/computacao-distribuida/lab-1.2 (main) $ mpirun --oversubscribe -np 4 python programa.py 

Gerando dataset de logs...

Processo 2 analisou 25000 linhas e encontrou 10137 erros.
Processo 1 analisou 25000 linhas e encontrou 10099 erros.
Processo 0 analisou 25000 linhas e encontrou 9973 erros.
Processo 3 analisou 25000 linhas e encontrou 9867 erros.
```

Uso com 8 processos:
```bash
@CarlosDinizz ➜ /workspaces/computacao-distribuida/lab-1.2 (main) $ mpirun --oversubscribe -np 8 python programa.py 

Gerando dataset de logs...

Processo 3 analisou 12500 linhas e encontrou 5098 erros.
Processo 2 analisou 12500 linhas e encontrou 5009 erros.
Processo 5 analisou 12500 linhas e encontrou 4943 erros.
Processo 7 analisou 12500 linhas e encontrou 4940 erros.
Processo 4 analisou 12500 linhas e encontrou 5131 erros.
Processo 1 analisou 12500 linhas e encontrou 4871 erros.
Processo 6 analisou 12500 linhas e encontrou 5014 erros.
Processo 0 analisou 12500 linhas e encontrou 4850 erros.
```

Foi possível perceber que conforme a quantidade de processos em execução aumentava, a execução se tornava mais lenta. Isso se deve ao codespaces possuir somente 2 threads e 1 núcleo físico.
## Funcionamento do programa

Para randomizar os logs, foi utilizado a função randint() da biblioteca random.

Para cada dado a ser inserido no log, foi utilizado uma variavel para armazenar um índice aleatório para ser consultado nas listas.

A string foi montada e armazenada na lista `logs`.

```python
def gerar_logs(qtd):
    ...

    logs = []

    for i in range (qtd):
        ipAleatorio = random.randint(2, len(ips) - 1)
        endpointAleatorio = random.randint(0, len(endpoints) - 1)
        metodoAleatorio = random.randint(0, 1)
        statusAleatorio = random.randint(0, len(status) - 1)

        novoLog = f"{ips[ipAleatorio]} {metodos[metodoAleatorio]} {endpoints[endpointAleatorio]} {status[statusAleatorio]}"
        logs.append(novoLog)
           
    return logs
```


---

Neste momento o processo Master (rank 0) realiza a divisão dos logs para serem executadas nos diferentes processos.

O tamanho para cada processo foi obtido através da divisão inteira `TOTAL_LOGS // size `.

Para cada processo existente, uma sublista de tamanho `TOTAL_LOGS // size` da lista `logs` foi adicionada em `logs_divididos`.

```python
logs_divididos = None
TOTAL_LOGS = 100000

if rank == 0:
    print("\nGerando dataset de logs...\n")
    logs = gerar_logs(TOTAL_LOGS)
    
    logs_divididos = []
    tamanho = TOTAL_LOGS // size
    for i in range (size):
        logProcesso = logs[tamanho * i : tamanho * (i + 1)]
        logs_divididos.append(logProcesso)
```
---

Aqui a função scatter é utilizada para fazer a distribuição entre os processos.

```python
logs_locais = comm.scatter(logs_divididos, root=0)
```
---

E então, por último é feito o processamento por cada processo, que verifica se contém o status 500 ou 404 na string de log.

A função split é utilizada para separar a string por espaços.

Como o log segue o padrão IP MÉTODO ENDPOINT STATUS, então por meio da função split(), o status pode ser obtido pelo índice 3.
```python
erros = 0
for log in logs_locais:
    partesLog = log.split(" ")
    statusEncontrado = partesLog[3]

    if statusEncontrado == "500":
        erros += 1
    elif statusEncontrado == "404":
        erros += 1
```
---

Finalizando com print da finalização da execução do programa.
```python
print(f"Processo {rank} analisou {len(logs_locais)} linhas "
      f"e encontrou {erros} erros."
)
```

