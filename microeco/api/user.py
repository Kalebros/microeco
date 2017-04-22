# -*- coding: utf-8 -*-
from flask import Blueprint,request,jsonify

from ..auth import *
from ..models import User

api_user = Blueprint('api_user',__name__)

@api_user.route('/user')
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

@api_user.route('/user/<user_id>')
@jwt_required()
@nivel_requerido(['Admin'])
def informacion_usuario(user_id):
    user=User.query.filter_by(id=user_id).first()
    return jsonify(user.to_dict())
