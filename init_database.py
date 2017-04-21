# -*- coding: utf-8 -*-

from app import db
from app import User,Cuenta,Operacion
from datetime import datetime

#Limpiar la base de datos
db.drop_all()

#Crear base de datos
db.create_all()

#Preparar usuarios
for usuario in TEST_CONFIGURATION['usuarios']:
    user=User(username=usuario['user'],email=usuario['email'],nivel=usuario['nivel'])
    user.password=usuario['password']
    db.session.add(user)
    listaCuentas=[]
    for cuenta in usuario['cuentas']:
        nCuenta=Cuenta(nombre=cuenta['nombre'],user=user,saldo_inicial=cuenta['saldo_inicial'])
        db.session.add(nCuenta)
        listaCuentas.append(nCuenta)
    for operacion in usuario['operaciones']:
        nOperacion=Operacion(descripcion=operacion['descripcion'],valor=float(operacion['valor']))
        for cuenta in listaCuentas:
            if operacion['origen']==cuenta.nombre:
                nOperacion.origen=cuenta
            if operacion['destino']==cuenta.nombre:
                nOperacion.destino=cuenta
        nOperacion.fecha=datetime.strptime(operacion['fecha'],'%d-%m-%Y')
        db.session.add(nOperacion)
    db.session.commit()
