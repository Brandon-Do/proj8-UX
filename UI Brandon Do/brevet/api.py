from pymongo import MongoClient
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import json
import random
import pymongo
import csv
import time
import os

client = MongoClient("db", 27017)
db = client.tododb
cred_db = client.cred_db
DEFAULT_TOP = 20

                            ###################
                            ### API SERVICE ###
                            ###################

def retrieve_json(top = DEFAULT_TOP, fields = ["km", "open", "close"]):
    """
        The data within the MongoDB is structured to have fields 'km', 'open', 'close'.
        Pass this function a list of fields that are wanted, returns dictionary with corresponding fields.
    """
    data = db.tododb.find().sort("open", pymongo.ASCENDING)
    results = {}
    count = 0
    for field in fields:
        results[field] = []
    for d in data:
        if top == 0:
            break
        top -= 1
        count += 1
        for field in fields:
            results[field].append(d[field])
    return results, count, 200


def retrieve_csv(top = DEFAULT_TOP, fields = ["km", "open", "close"]):
    """
        The data within the MongoDB is structured to have fields 'km', 'open', 'close'.
        Pass this function a list of fields that are wanted, returns dictionary with corresponding fields.
    """

    data = db.tododb.find().sort("open", pymongo.ASCENDING)
    results = ""
    count = 0
    for field in fields:
        results += field + ","
    results  += os.linesep
    for d in data:
        if top == 0:
            break
        top -= 1
        count += 1
        for field in fields:
            results += d[field] + ","
        results  += os.linesep
    return results.strip(os.linesep), 0, 200

def handle(arg_str):
    if arg_str == None or not arg_str.isdigit():
        global DEFAULT_TOP
        top = DEFAULT_TOP
    else:
        top = int(arg_str)
    return top

#####################
### AUTHORIZATION ###
#####################

def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def generate_auth_token(profile_id, expiration=60 * 10):
   s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
   return s.dumps({'profile_id': profile_id})

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False    # valid token, but expired
    except BadSignature:
        return False    # invalid token
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
