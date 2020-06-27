from flask import Flask, jsonify, request
from flask_cors import CORS
from src import auth, user

app = Flask(__name__)
CORS(app)


def createUserWith(userEmail, userPassword, repeatedPassword, phone, organization,position, city):
    authToken = auth.AuthManager().encodeAuthToken(userEmail)

    newUser = user.User(userEmail, userPassword, repeatedPassword, phone, organization,position, city)
    newUser.addUser() 

    return authToken.decode()


@app.route("/user/login", methods=["POST"])
def logInUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')

    usr = user.User.findUserByEmail(userEmail)
    if usr is None:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        authToken = auth.AuthManager().authenticate(usr, userPassword)
        if not authToken:
            return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'token': authToken}), 200


@app.route("/user/signup", methods=["POST"])
def signUpUser():
    userEmail = request.json.get('email')
    userPassword = request.json.get('password')
    repeatedPassword = request.json.get('repeat_password')
    phone = request.json.get('phone')
    organization = request.json.get('organization')
    position = request.json.get('position')
    city = request.json.get('city')

    usr = user.User.findUserByEmail(userEmail)

    if usr is not None:
        return jsonify({'message': 'Email already registered'}), 409
    else:
        authToken = createUserWith(userEmail, userPassword, repeatedPassword, phone, organization,position, city)

    return jsonify({'token': authToken}), 200


# test route
@app.route("/")
def hello():
    return "Hello World!"
