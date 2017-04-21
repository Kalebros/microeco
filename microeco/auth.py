# -*- coding: utf-8 -*-

from .app import db,app
from .models import User

from flask_jwt import JWT,jwt_required,current_identity,JWTError
from functools import update_wrapper
from flask import request

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
