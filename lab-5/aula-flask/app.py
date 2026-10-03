from flask import Flask, jsonify
app = Flask(__name__)

produtos_fiscais = { "1": { "preco": 2500.0, "categoria": "Laptops" }, "2": {"preco": 1200.0, "categoria": "Monitores"} }

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "mensagem": "Olá do Flask!",
        "status": "sucesso",
    "tecnologia": "Python"
    })

@app.route('/api/data/<string:id>', methods=["GET"])
def get_produtos_fiscais(id):
    print(produtos_fiscais[id])
    return jsonify((produtos_fiscais[id]))
    
if __name__ == '__main__':
    # No Codespaces, use host='0.0.0.0' para permitir acesso externo
    app.run(debug=True, host='0.0.0.0', port=5000)