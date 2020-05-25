import json
from flask import Flask, jsonify, request
# from flask_jwt import JWT, jwt_required, current_identity
# from werkzeug.security import safe_str_cmp
import os
import boto3

app = Flask(__name__)

# Database configuration
USER_TABLE = os.environ['USER1_TABLE']
dynamodb = boto3.client('dynamodb', region_name='us-east-1')



def authenticate(user, userPassword):
    if user.password == userPassword:
        return user


def findUserByEmail(userEmail):
    user = dynamodb.get_item(
        TableName=USER_TABLE,
        Key={'email': {'S': userEmail}}
    )
    item = user.get('Item')
    if not item:
        return None
    return item


@app.route("/user/login", methods=["POST"])
def logInUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = findUserByEmail(userEmail)
    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        authenticate(user, userPassword)

    return jsonify({'message': 'Everything is ok'}), 200


@app.route("/")
def hello():
    return "Hello World!"
