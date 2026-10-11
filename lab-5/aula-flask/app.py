from flask import Flask, jsonify, request
import datetime
app = Flask(__name__)

produtos_fiscais = { "1": { "preco": 2500.0, "categoria": "Laptops" }, "2": {"preco": 1200.0, "categoria": "Monitores"} }

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "mensagem": "Olá do Flask!",
        "status": "sucesso",
    "tecnologia": "Python"
    })

@app.route('/api/data/produtos_fiscais/<string:id>', methods=["GET"])
def get_produtos_fiscais(id):
    print(produtos_fiscais[id])
    return jsonify((produtos_fiscais[id]))

@app.route('/detalhes/<string:id>', methods=["GET"])
def get_detalhes(id):
    print(produtos_fiscais[id])
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
    req = request.get_json()
    id = req["id"]
    produtos_fiscais[id] = {
        "preco": float(req["preco_base"]) + (float(req["preco_base"]) * 0.2),
        "categoria": req["categoria"]
    }
    return jsonify({"message": f"Cadastro foi realizado. ID: {id}"}), 201

    
if __name__ == '__main__':
    # No Codespaces, use host='0.0.0.0' para permitir acesso externo
    app.run(debug=True, host='0.0.0.0', port=5000)