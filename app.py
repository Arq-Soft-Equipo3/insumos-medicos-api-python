from flask import Flask, jsonify, request
from flask_cors import CORS
from src import auth, user
from src.application import Application

app = Flask(__name__)
CORS(app)


def createUserWith(userEmail, userPassword, repeatedPassword, phone, organization, position, city):
    authToken = auth.AuthManager().encodeAuthToken(userEmail)

    newUser = user.User(userEmail, userPassword, repeatedPassword, phone, organization, position, city)
    newUser.addUser()

    return authToken.decode()


def createApplicationWith(bearer, supply, area, medicine):
    userEmail = decodeToken(bearer)
    application = Application(userEmail, supply, area, medicine)

    return application.addApplication()


def decodeToken(bearer):
    authToken = bearer.split(" ")[1]
    userEmail = auth.AuthManager().decodeAuthToken(authToken)
    return userEmail


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
        authToken = createUserWith(userEmail, userPassword, repeatedPassword, phone, organization, position, city)

    return jsonify({'token': authToken}), 200


@app.route("/applications", methods=["POST"])
def submitApplication():
    bearer = request.headers.get('Authorization')
    supply = request.json.get('supply')
    area = request.json.get('area')
    medicine = request.json.get('medicine')
    applicationID = createApplicationWith(bearer, supply, area, medicine)

    return jsonify({"message": "The application #" + applicationID + " was successfully submitted"}), 200


@app.route("/applications", methods=["GET"])
def applications():
    bearer = request.headers.get('Authorization')
    userEmail = decodeToken(bearer)
    appls = Application.applicationsBy(userEmail)
    return jsonify(appls), 200


@app.route("/applications/cancel", methods=["POST"])
def cancelApplication():
    bearer = request.headers.get('Authorization')
    userEmail = decodeToken(bearer)
    if request.args.get('id') is None:
        return jsonify({"errors": [{"field": "id", "message": "id is required"}]}), 422
    else:
        Application.cancelApplication(userEmail, request.args.get('id'))
    return jsonify({'message': 'Application #' + request.args.get('id') + 'was succefully canceled'}), 200


# test route
@app.route("/")
def hello():
    return "Hello World!"
