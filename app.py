import json
from flask import Flask, jsonify, request
# from flask_jwt import JWT, jwt_required, current_identity
# from werkzeug.security import safe_str_cmp
import os
import boto3

app = Flask(__name__)

# Database configuration
USER_TABLE = os.environ['USER1_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')
if IS_OFFLINE:
    dynamodb = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')


# dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def authenticate(user, userPassword):
    if user.get('password').get('S') == userPassword:
        return True
    else:
        return False


def findUserByEmail(userEmail):
    user = dynamodb.get_item(
        TableName=USER_TABLE,
        Key={'email': {'S': userEmail}}
    )
    item = user.get('Item')
    if not item:
        return None
    return item


def addUser(userEmail, userPassword):
    resp = dynamodb.put_item(
        TableName=USER_TABLE,
        Item={
            'email': {'S': userEmail},
            'password': {'S': userPassword}
        }
    )


@app.route("/user/login", methods=["POST"])
def logInUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = findUserByEmail(userEmail)
    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        if not authenticate(user, userPassword):
            return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'message': 'Everything is ok'}), 200


@app.route("/user/signup", methods=["POST"])
def signUpUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = findUserByEmail(userEmail)

    if user is not None:
        return jsonify({'message': 'Email already registered'}), 409
    else:
        addUser(userEmail, userPassword)

    return jsonify({'message': 'User succesfuly created'}), 200


@app.route("/")
def hello():
    return "Hello World!"
