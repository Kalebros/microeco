# -*- coding: utf-8 -*-

from flask import Flask,request,jsonify
import os
from flask_sqlalchemy import SQLAlchemy
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

from models import *

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
