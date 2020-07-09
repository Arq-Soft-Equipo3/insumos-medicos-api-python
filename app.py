from flask import Flask, jsonify, request
from flask_cors import CORS
from src import auth, user
from src.application import Application
from src.customExceptions import AuthorizationFailed, DatabaseConnectionFailed, InstanceCreationFailed

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
    try:
        userEmail = request.json.get('email')
        userPassword = request.json.get('password')

        usr = user.User.findUserByEmail(userEmail)
        if usr is None:
            return jsonify({'message': 'Invalid credentials'}), 401
        else:
            authToken = auth.AuthManager().authenticate(usr, userPassword)
        return jsonify({'token': authToken}), 200
    except DatabaseConnectionFailed as e:
        return jsonify({"message": e.message}), 500
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401


@app.route("/user/signup", methods=["POST"])
def signUpUser():
    try:
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
    except InstanceCreationFailed as e:
        return jsonify({"errors": e.message}), 422
    except DatabaseConnectionFailed as e:
        return jsonify({"message": e.message}), 500
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401


@app.route("/applications", methods=["POST"])
def submitApplication():
    try:
        bearer = request.headers.get('Authorization')
        supply = request.json.get('supply')
        area = request.json.get('area')
        medicine = request.json.get('medicine')
        applicationID = createApplicationWith(bearer, supply, area, medicine)

        return jsonify({"message": "The application #" + applicationID + " was successfully submitted"}), 200
    except InstanceCreationFailed as e:
        return jsonify({"errors": e.message}), 422
    except DatabaseConnectionFailed as e:
        return jsonify({"message": e.message}), 500
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401


@app.route("/applications", methods=["GET"])
def applications():
    try:
        bearer = request.headers.get('Authorization')
        userEmail = decodeToken(bearer)
        appls = Application.applicationsBy(userEmail)
        return jsonify(appls), 200
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401
    except DatabaseConnectionFailed as e:
        return jsonify({e.message}), 500


@app.route("/applications/cancel", methods=["POST"])
def cancelApplication():
    try:
        bearer = request.headers.get('Authorization')
        userEmail = decodeToken(bearer)
        if request.json.get('id') is None:
            return jsonify({"errors": [{"field": "id", "message": "id is required"}]}), 422
        else:
            Application.cancelApplication(userEmail, request.json.get('id'))
        return jsonify({'message': 'Application #' + request.json.get('id') + ' was successfully canceled'}), 200
    except DatabaseConnectionFailed as dcf:
        return jsonify({"message": dcf.message}), 500
    except AuthorizationFailed as af:
        return jsonify({"message": af.message}), 401


# test route
@app.route("/")
def hello():
    return "Hello World!"
