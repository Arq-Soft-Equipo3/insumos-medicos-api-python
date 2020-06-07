import json
from flask import Flask, jsonify, request
import datetime
import bcrypt
import jwt
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

app.config['SECRET_KEY'] = 'super-secret'


# dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def encodeAuthToken(userEmail):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=1),
            'iat': datetime.datetime.utcnow(),
            'sub': userEmail
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


def authenticate(user, aPassword):
    userPassword = user.get('password').get('B')
    userEmail = user.get('email').get('S')

    if bcrypt.checkpw(aPassword.encode('utf8'), userPassword):
        return encodeAuthToken(userEmail).decode()
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
    authToken = encodeAuthToken(userEmail)

    hashedPass = bcrypt.hashpw(userPassword.encode('utf8'), bcrypt.gensalt())
    resp = dynamodb.put_item(
        TableName=USER_TABLE,
        Item={
            'email': {'S': userEmail},
            'password': {'B': hashedPass}
        }
    )

    return authToken.decode()


@app.route("/user/login", methods=["POST"])
def logInUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = findUserByEmail(userEmail)
    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        authToken = authenticate(user, userPassword)
        if not authToken:
            return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'token': authToken}), 200


@app.route("/user/signup", methods=["POST"])
def signUpUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = findUserByEmail(userEmail)

    if user is not None:
        return jsonify({'message': 'Email already registered'}), 409
    else:
        authToken = addUser(userEmail, userPassword)

    return jsonify({'token': authToken}), 200


# test route
@app.route("/")
def hello():
    return "Hello World!"
