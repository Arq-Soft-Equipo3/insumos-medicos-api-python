import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import user
import auth

app = Flask(__name__)
CORS(app)


def createUserWith(userEmail, userPassword):
    authToken = auth.AuthManager().encodeAuthToken(userEmail)

    user = user.User(userEmail, userPassword)
    user.addUser() 

    return authToken.decode()


@app.route("/user/login", methods=["POST"])
def logInUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = user.User.findUserByEmail(userEmail)
    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        authToken = auth.AuthManager().authenticate(user, userPassword)
        if not authToken:
            return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'token': authToken}), 200


@app.route("/user/signup", methods=["POST"])
def signUpUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    user = user.User.findUserByEmail(userEmail)

    if user is not None:
        return jsonify({'message': 'Email already registered'}), 409
    else:
        authToken = createUserWith(userEmail, userPassword)

    return jsonify({'token': authToken}), 200


# test route
@app.route("/")
def hello():
    return "Hello World!"
