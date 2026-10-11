import requests


def consumir_api(nome, url):
    try:
        response = requests.get(url)
        dados = response.json()
        print(f"--- Resposta do {nome} ---")
        print(f"{dados}")
    except Exception as e:
        print(f"Erro ao conectar no {nome}: Servidor está rodando?")

def receber_urls():
    lista_urls = []
    continuar = 1
    
    while continuar == 1:
        url = str(input(f"Digite a url: "))
            
        lista_urls.append(url)    
        continuar = int(input("Deseja continuar escrevendo urls?\n0. Para encerrar\n1. Para continuar\nResposta: "))
    
    return lista_urls
        

if __name__ == "__main__":
    urls = receber_urls()
    for url in urls:
        try:
            consumir_api(url, url)
        except:
            continue
            
        
    
    print("Programa finalizado.")