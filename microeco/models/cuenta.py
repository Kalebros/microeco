# -*- coding: utf-8 -*-
from ..app import db

from .user import User

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
