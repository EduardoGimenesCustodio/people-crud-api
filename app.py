from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json
from flask_cors import CORS
from flask_cors import cross_origin
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + os.environ['DATABASE_USERNAME'] + ':' + os.environ['DATABASE_PASSWORD'] + '@' + os.environ['DATABASE_HOST'] + ':' + os.environ['DATABASE_PORT'] + '/' + os.environ['DATABADE_NAME']
db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = "pessoas"
    id_pessoa = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    rg = db.Column(db.String(100))
    cpf = db.Column(db.String(100))
    data_nascimento = db.Column(db.Date)
    data_admissao = db.Column(db.Date)
    funcao = db.Column(db.String(100))

    def to_json(self):
        return {
            "id_pessoa": self.id_pessoa,
            "nome": self.nome,
            "rg": self.rg,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.isoformat(),
            "data_admissao": self.data_admissao.isoformat(),
            "funcao": self.funcao,
        }

@app.route("/person", methods=["GET"])
@cross_origin()
def list_people():
    people_objects = Person.query.all()
    people_json = [person.to_json() for person in people_objects]

    return make_response(200, "pessoas", people_json)

@app.route("/person/<id_pessoa>", methods=["GET"])
@cross_origin()
def get_person_by_id(id_pessoa):
    person_object = Person.query.filter_by(id_pessoa=id_pessoa).first()
    person_json = person_object.to_json()

    return make_response(200, "pessoa", person_json)

@app.route("/person", methods=["POST"])
@cross_origin()
def create_person():
    body = request.get_json()

    try:
        person = Person(nome=body["nome"], rg=body["rg"], cpf=body["cpf"], data_nascimento=body["data_nascimento"], data_admissao=body["data_admissao"], funcao=body["funcao"])
        db.session.add(person)
        db.session.commit()
        return make_response(201, "pessoa", person.to_json(), "successfully created")
    except Exception as error:
        print('Error', error)
        return make_response(400, "pessoa", {}, "error when registering")

@app.route("/person/<id_pessoa>", methods=["PUT"])
@cross_origin()
def update_person_by_id(id_pessoa):
    person_object = Person.query.filter_by(id_pessoa=id_pessoa).first()
    body = request.get_json()

    try:
        if('nome' in body):
            person_object.nome = body['nome']
        if('rg' in body):
            person_object.rg = body['rg']
        if('cpf' in body):
            person_object.cpf = body['cpf']
        if('data_nascimento' in body):
            person_object.data_nascimento = body['data_nascimento']
        if('data_admissao' in body):
            person_object.data_admissao = body['data_admissao']
        if('funcao' in body):
            person_object.funcao = body['funcao']

        db.session.add(person_object)
        db.session.commit()
        return make_response(200, "pessoa", person_object.to_json(), "updated successfully")
    except Exception as error:
        print('Error', error)
        return make_response(400, "pessoa", {}, "error when updating")

@app.route("/person/<id_pessoa>", methods=["DELETE"])
@cross_origin()
def delete_person_by_id(id_pessoa):
    person_object = Person.query.filter_by(id_pessoa=id_pessoa).first()

    try:
        db.session.delete(person_object)
        db.session.commit()
        return make_response(200, "pessoa", person_object.to_json(), "successfully deleted")
    except Exception as error:
        print('Error', error)
        return make_response(400, "pessoa", {}, "error when deleting")

def make_response(status, content_name, content, message=False):
    body = {}
    body[content_name] = content

    if(message):
        body["message"] = message

    return Response(json.dumps(body), status=status, mimetype="application/json")

app.run()