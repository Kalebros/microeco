# -*- coding: utf-8 -*-

from flask import Flask,request,jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt import JWT,jwt_required,current_identity,JWTError
import json
from functools import update_wrapper
from datetime import datetime,timedelta

app=Flask(__name__)
app.debug=True
app.config['SECRET_KEY']='super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_EXPIRATION_DELTA']=timedelta(days=10)
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True)
    email=db.Column(db.String(120),unique=True)
    password_hash=db.Column(db.String(256),nullable=False)
    nivel=db.Column(db.String(80),nullable=False,default='User')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)

    def to_dict(self):
        return {
            'id':self.id,
            'username':self.username,
            'email':self.email,
            'nivel':self.nivel
        }

    def __init__(self,username,email,nivel='Tecnico'):
        self.username=username
        self.email=email
        self.nivel=nivel

    def __repr__(self):
        return '<User %r>' % self.username

class Cuenta(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(120),nullable=False)
    saldo_inicial=db.Column(db.Float,default=0.0,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    user=db.relationship('User',backref=db.backref('cuentas',lazy='dynamic'))

    def to_dict(self):
        return {
            'id':self.id,
            'nombre':self.nombre,
            'saldo':str(self.saldo_cuenta()),
            'saldo_inicial':str(self.saldo_inicial)
        }

    @classmethod
    def from_dict(cls,validated_data):
        user=User.query.filter_by(id=validated_data['user']).first()
        result=cls(nombre=validated_data['nombre'],user=user)
        return result

    def saldo_cuenta(self):
        saldo=self.saldo_inicial
        operaciones_entrada=self.destino.all()
        for operacion in operaciones_entrada:
            saldo+=operacion.valor
        operaciones_salida=self.origen.all()
        for operacion in operaciones_salida:
            saldo-=operacion.valor
        return saldo


    def __init__(self,nombre,user,saldo_inicial=0.0):
        self.nombre=nombre
        self.user=user
        self.saldo_inicial=saldo_inicial

    def __repr__(self):
        return '<Cuenta %r>' % self.nombre

class Operacion(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    descripcion=db.Column(db.String(120),nullable=False)
    valor=db.Column(db.Float,nullable=False)
    fecha=db.Column(db.DateTime,nullable=False)
    origen_id=db.Column(db.Integer,db.ForeignKey('cuenta.id'))
    destino_id=db.Column(db.Integer,db.ForeignKey('cuenta.id'))
    origen=db.relationship('Cuenta',foreign_keys=[origen_id],backref=db.backref('origen',lazy='dynamic'))
    destino=db.relationship('Cuenta',foreign_keys=[destino_id],backref=db.backref('destino',lazy='dynamic'))

    def to_dict(self):
        return {
            'id':self.id,
            'descripcion':self.descripcion,
            'valor':str(self.valor),
            'origen':self.origen.nombre,
            'destino':self.destino.nombre,
            'fecha':self.fecha.strftime('%d-%m-%Y')
        }

    @classmethod
    def from_dict(cls,validated_data):
        result=cls(descripcion=validated_data['descripcion'],
                    valor=float(validated_data['valor']),
                    fecha=datetime.strptime(validated_data['fecha'],'%d-%m-%Y'))
        return result

    def __init__(self,descripcion,valor,fecha=None):
        self.descripcion=descripcion
        self.valor=valor
        if fecha is None:
            self.fecha=datetime.now()
        else:
            self.fecha=fecha

    def __repr__(self):
        return '<Operacion %r>' % self.descripcion

def authenticate(username,password):
    user=User.query.filter_by(username=username).first()
    if user and user.validate_password(password):
        return user

def identity(payload):
    user_id=payload['identity']
    return User.query.filter_by(id=user_id).first()

jwt=JWT(app,authenticate,identity)

def nivel_requerido(nivel):
    def decorator(fn):
        def wrapped_function(*args,**kwargs):
            if current_identity.nivel not in nivel:
                raise JWTError('Acceso no permitido','No tiene suficientes privilegios para acceder al recurso')
            return fn(*args,**kwargs)
        return update_wrapper(wrapped_function,fn)
    return decorator

def isOwnerOrAdmin(model):
    def decorator(fn):
        def wrapped_function(*args,**kwargs):
            resource_id=request.path.split('/')[-1]
            resource=model.query.filter_by(id=resource_id).first()
            if current_identity.id != resource.user.id and current_identity.nivel!='Admin':
                raise JWTError('Acceso no permitido','No tiene suficientes privilegios para acceder al recurso')
            return fn(*args,**kwargs)
        return update_wrapper(wrapped_function,fn)
    return decorator

@app.after_request
def gnu_terry_pratchett(resp):
    resp.headers.add('X-Clacks-Overhead','GNU Terry Pratchett')
    return resp

@app.route('/')
def hello():
    return 'Hello world!'

@app.route('/user')
@jwt_required()
@nivel_requerido(['Admin','User'])
def users():
    print request.args.get('show',None)
    if request.args.get('show',None) == 'all':
        if current_identity.nivel == 'Admin':
            listaUsers=[]
            listado=User.query.all()
            for user in listado:
                listaUsers.append(user.to_dict())
            return jsonify(listaUsers)
    return jsonify(current_identity.to_dict())

@app.route('/cuentas',methods=['GET'])
@jwt_required()
@nivel_requerido(['Admin','User'])
def cuentas():
    lista_cuentas=current_identity.cuentas.all()
    result=[]
    for cuenta in lista_cuentas:
        result.append(cuenta.to_dict())
    return json.dumps(result)

@app.route('/cuentas',methods=['POST'])
@jwt_required()
@nivel_requerido(['Admin','User'])
def addCuenta():
    cuenta=Cuenta.from_dict(request.get_json())
    db.session.add(cuenta)
    db.session.commit()
    r=jsonify(cuenta.to_dict())
    r.status_code=201
    return r

@app.route('/cuentas/<cuenta_id>',methods=['GET'])
@jwt_required()
@nivel_requerido(['Admin','User'])
@isOwnerOrAdmin(Cuenta)
def listar_operaciones(cuenta_id):
    cuenta=Cuenta.query.filter_by(id=cuenta_id).first()
    result=cuenta.to_dict()
    operaciones_entrada=cuenta.destino.all()
    lista_Entrada=[]
    for operacion in operaciones_entrada:
        lista_Entrada.append(operacion.to_dict())
    operaciones_salida=cuenta.origen.all()
    lista_Salida=[]
    for operacion in operaciones_salida:
        lista_Salida.append(operacion.to_dict())
    result['operaciones']={}
    result['operaciones']['entrada']=lista_Entrada
    result['operaciones']['salida']=lista_Salida
    return jsonify(result)

@app.route('/cuentas/<cuenta_id>',methods=['POST'])
@jwt_required()
@nivel_requerido(['Admin','User'])
@isOwnerOrAdmin(Cuenta)
def add_operacion(cuenta_id):
    cuenta=Cuenta.query.filter_by(id=cuenta_id).first()
    nOperacion=Operacion.from_dict(request.get_json())
    cOrigen=Cuenta.query.filter_by(id=request.get_json()['origen']).first()
    cDestino=Cuenta.query.filter_by(id=request.get_json()['destino']).first()
    if cOrigen.user.id!=current_identity.id:
        raise JWTError('Violacion de cuenta','No tiene permisos sobre la cuenta de origen')
    elif cDestino.user.id!=current_identity.id:
        raise JWTError('Violacion de cuenta','No tiene permisos sobre la cuenta de destino')
    else:
        nOperacion.origen=cOrigen
        nOperacion.destino=cDestino
        db.session.add(nOperacion)
        db.session.commit()
        return jsonify(nOperacion.to_dict())
    raise JWTError('Error desconocido','No se pudo llevar a cabo la operacion solicitada')

@app.route('/user/<user_id>')
@jwt_required()
@nivel_requerido(['Admin'])
def informacion_usuario(user_id):
    user=User.query.filter_by(id=user_id).first()
    return jsonify(user.to_dict())

if __name__=="__main__":
    app.run()
