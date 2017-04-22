# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash

from ..app import db

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
