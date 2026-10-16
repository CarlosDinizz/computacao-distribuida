import requests

URL_FLASK = "http://localhost:5000"
URL_NODE = "http://localhost:3000"

ERRO_ESPERADO = {
    "error": "INVALID_ID",
    "message": "O ID deve ser um inteiro positivo",
}

CASOS = [
    ("Node  - ID negativo",       "GET",  f"{URL_NODE}/estoque/-5",            None, 400),
    ("Node  - ID texto",          "GET",  f"{URL_NODE}/estoque/abc",           None, 400),
    ("Node  - ID zero",           "GET",  f"{URL_NODE}/estoque/0",             None, 400),
    ("Node  - ID decimal",        "GET",  f"{URL_NODE}/estoque/1.5",           None, 400),
    ("Node  - full-info negativo", "GET", f"{URL_NODE}/api/full-info/-5",      None, 400),
    ("Flask - ID negativo",       "GET",  f"{URL_FLASK}/detalhes/-5",          None, 400),
    ("Flask - ID texto",          "GET",  f"{URL_FLASK}/detalhes/abc",         None, 400),
    ("Node  - POST id inválido",  "POST", f"{URL_NODE}/api/cadastrar",
        {"id": "-3", "nome": "teclado", "estoque": 20, "preco_base": 200.0, "categoria": "Perifericos"}, 400),
    ("Flask - POST id inválido",  "POST", f"{URL_FLASK}/fiscal/cadastrar",
        {"id": "xyz", "preco_base": 200.0, "categoria": "Perifericos"}, 400),

    ("Node  - ID válido",         "GET",  f"{URL_NODE}/estoque/1",             None, 200),
    ("Node  - full-info válido",  "GET",  f"{URL_NODE}/api/full-info/1",       None, 200),
    ("Flask - ID válido",         "GET",  f"{URL_FLASK}/detalhes/2",           None, 200),

    ("Node  - ID inexistente",    "GET",  f"{URL_NODE}/estoque/99",            None, 404),
    ("Flask - ID inexistente",    "GET",  f"{URL_FLASK}/detalhes/99",          None, 404),
]


def testar(descricao, metodo, url, corpo, esperado):
    try:
        resposta = requests.request(metodo, url, json=corpo, timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"[ERRO] {descricao}: servidor fora do ar ({url})")
        return False

    try:
        dados = resposta.json()
    except ValueError:
        dados = resposta.text

    ok = resposta.status_code == esperado
    if esperado == 400:
        ok = ok and dados == ERRO_ESPERADO

    marca = "OK  " if ok else "FALHOU"
    print(f"[{marca}] {descricao}")
    print(f"        {metodo} {url}")
    print(f"        status: {resposta.status_code} (esperado {esperado})")
    print(f"        corpo:  {dados}\n")
    return ok


if __name__ == "__main__":
    resultados = [testar(*caso) for caso in CASOS]
    print(f"Resultado: {sum(resultados)}/{len(resultados)} testes passaram.")
