from database import db

class Cientista(db.Model):
    __tablename__ = 'cientista'
    
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(50), nullable = False)
    
    def _to_dict(self):
        return { "id": self.id, "nome": self.nome }

class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    
    id = db.Column(db.Integer, primary_key = True)
    id_cientista = (db.Integer, db.ForeignKey("cientista.id"))
    data_agendamento = db.Column(db.DateTime, nullable = False)
    
    def _to_dict(self):
        return { "id": self.id, "id_cientista": self.id_cientista, "data_agendamento": self.data_agendamento }