# -*- coding: utf-8 -*-

from flask import Flask,request,jsonify
import os
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime,timedelta

app=Flask(__name__)
app.debug=True
app.config['SECRET_KEY']='super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_EXPIRATION_DELTA']=timedelta(days=10)
db=SQLAlchemy(app)

from .models import *
from .auth import *

from .api import api as api_blueprint
app.register_blueprint(api_blueprint,url_prefix='/api/v1')

@app.after_request
def gnu_terry_pratchett(resp):
    resp.headers.add('X-Clacks-Overhead','GNU Terry Pratchett')
    return resp

@app.route('/')
def hello():
    return 'Hello world!'
