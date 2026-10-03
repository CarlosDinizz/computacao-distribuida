import requests


# No Codespaces, enquanto você testa localmente no terminal:
url_flask = "http://localhost:5000/api/data"
url_node = "http://localhost:3000/api/data"


def consumir_api(nome, url, id):
    try:
        response = requests.get(f"{url}/{id}")
        return response;
        
    except Exception as e:
        print(f"Erro ao conectar no {nome}: Servidor está rodando?")

if __name__ == "__main__":
    id = int(input("Digite um id entre 1 e 2: "))
    response_produtos_estoque = consumir_api("Node", url_node, id)
    response_produtos_fiscais = consumir_api("Flask", url_flask, id)
    
    dados_estoque = response_produtos_estoque.json()
    dados_fiscais = response_produtos_fiscais.json()
    print(f"Estoque: {dados_estoque}")
    print(f"Fiscais: {dados_fiscais}")
    
    dados = {
        "id": id,
        "nome": dados_estoque['nome'],
        "preco": dados_fiscais['preco'],
        "estoque": dados_estoque['estoque']
    };

    print(f"ID: {dados.get('id')} | Nome: {dados.get('nome')} | Preço: {dados.get('preco')} | Estoque: {dados.get('estoque')}")
