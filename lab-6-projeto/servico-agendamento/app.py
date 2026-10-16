from flask import Flask, jsonify, request
from database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agendamento.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', methods=["GET"])
def hello_world():
    return jsonify('Hello World!'), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)