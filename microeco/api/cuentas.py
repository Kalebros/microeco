#-*- coding: utf-8 -*-
from flask import Blueprint,request,jsonify

from ..auth import *
from ..models import Cuenta,Operacion

api_cuentas=Blueprint('api_cuentas',__name__)

@api_cuentas.route('/cuentas',methods=['GET'])
@jwt_required()
@nivel_requerido(['Admin','User'])
def cuentas():
    lista_cuentas=current_identity.cuentas.all()
    result=[]
    for cuenta in lista_cuentas:
        result.append(cuenta.to_dict())
    return jsonify(result)

@api_cuentas.route('/cuentas',methods=['POST'])
@jwt_required()
@nivel_requerido(['Admin','User'])
def addCuenta():
    cuenta=Cuenta.from_dict(request.get_json())
    db.session.add(cuenta)
    db.session.commit()
    r=jsonify(cuenta.to_dict())
    r.status_code=201
    return r

@api_cuentas.route('/cuentas/<cuenta_id>',methods=['GET'])
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

@api_cuentas.route('/cuentas/<cuenta_id>',methods=['POST'])
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
