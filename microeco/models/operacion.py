# -*- coding: utf-8 -*-
from ..app import db
from .user import User
from .cuenta import Cuenta
from datetime import datetime

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
