# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash

from app import db

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
