from flask import Flask, jsonify, request
import datetime
import re
app = Flask(__name__)

produtos_fiscais = { "1": { "preco": 2500.0, "categoria": "Laptops" }, "2": {"preco": 1200.0, "categoria": "Monitores"} }

ERRO_ID_INVALIDO = {
    "error": "INVALID_ID",
    "message": "O ID deve ser um inteiro positivo"
}

def id_valido(valor):
    """Aceita somente inteiros positivos (1, 2, 3...). Rejeita -5, 0, abc, 1.5 etc."""
    return re.fullmatch(r"[0-9]+", str(valor)) is not None and int(valor) > 0


def erro_nao_encontrado(id):
    return jsonify({
        "error": "NOT_FOUND",
        "message": f"Produto com ID {id} não encontrado"
    }), 404


@app.before_request
def validar_id_da_url():
    if request.view_args and "id" in request.view_args:
        if not id_valido(request.view_args["id"]):
            return jsonify(ERRO_ID_INVALIDO), 400
        request.view_args["id"] = str(int(request.view_args["id"]))

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "mensagem": "Olá do Flask!",
        "status": "sucesso",
    "tecnologia": "Python"
    })

@app.route('/api/data/produtos_fiscais/<string:id>', methods=["GET"])
def get_produtos_fiscais(id):
    if id not in produtos_fiscais:
        return erro_nao_encontrado(id)
    return jsonify((produtos_fiscais[id]))

@app.route('/detalhes/<string:id>', methods=["GET"])
def get_detalhes(id):
    if id not in produtos_fiscais:
        return erro_nao_encontrado(id)
    return jsonify((produtos_fiscais[id]))

@app.route('/status', methods=["GET"])
def get_status():
    status = {
        "service": "flask",
        "status": 'online',
        "timestamp": str(datetime.datetime.now())
    }
    return jsonify(status), 200



@app.route('/fiscal/cadastrar', methods=["POST"])
def post_cadastrar():
    req = request.get_json(silent=True) or {}
    if not id_valido(req.get("id")):
        return jsonify(ERRO_ID_INVALIDO), 400
    id = str(int(req["id"]))
    produtos_fiscais[id] = {
        "preco": float(req["preco_base"]) + (float(req["preco_base"]) * 0.2),
        "categoria": req["categoria"]
    }
    return jsonify({"message": f"Cadastro foi realizado. ID: {id}"}), 201

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
