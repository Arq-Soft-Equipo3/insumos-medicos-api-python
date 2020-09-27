from flask import Flask, jsonify, request
from flask_cors import CORS
from src import auth, user
from src.application import Application
from src.customExceptions import AuthorizationFailed, DatabaseConnectionFailed, InstanceCreationFailed

app = Flask(__name__)
CORS(app)


def createUserWith(userEmail, userPassword, repeatedPassword, phone, organization, position, city):

    newUser = user.User(userEmail, userPassword, repeatedPassword, phone, organization, position, city)
    newUser.addUser()
    authToken = auth.AuthManager().encodeAuthToken(userEmail, newUser.role)

    return authToken.decode()


def createApplicationWith(bearer, supply, area, medicine):
    userEmail = decodeToken(bearer)
    application = Application(userEmail, supply, area, medicine)

    return application.addApplication()


def decodeToken(bearer):
    authToken = bearer.split(" ")[1]
    userEmail = auth.AuthManager().decodeAuthToken(authToken)
    return userEmail


@app.route("/users/login", methods=["POST"])
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
        return jsonify({"message": "Something went wrong"}), 500
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401


@app.route("/users/signup", methods=["POST"])
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
        return jsonify({"message": "Something went wrong"}), 500
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401


@app.route("/applications", methods=["POST"])
def submitApplication():
    try:
        bearer = request.headers.get('Authorization')
        supply = request.json.get('supply')
        area = request.json.get('area')
        medicine = request.json.get('medicine')
        application = createApplicationWith(bearer, supply, area, medicine)

        return jsonify(application), 200
    except InstanceCreationFailed as e:
        return jsonify({"errors": e.message}), 422
    except DatabaseConnectionFailed as e:
        return jsonify({"message": "Something went wrong"}), 500
    except AuthorizationFailed as e:
        return jsonify({"message": e.message}), 401
    except ValueError as e:
        return jsonify({"message": str(e)}), 412


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
        return jsonify({"Something went wrong"}), 500


@app.route("/applications/<id>/cancel", methods=["POST"])
def cancelApplication(id):
    print(id)
    try:
        bearer = request.headers.get('Authorization')
        userEmail = decodeToken(bearer)
        Application.cancelApplication(userEmail, id)
        return jsonify({'message': 'Application #' + id + ' was successfully canceled'}), 200
    except DatabaseConnectionFailed as dcf:
        return jsonify({"message": "Something went wrong"}), 500
    except AuthorizationFailed as af:
        return jsonify({"message": af.message}), 401


@app.route("/applications/<id>/approve", methods=["POST"])
def approveApplication(id):
    try:
        bearer = request.headers.get('Authorization')
        provider = request.json.get('provider')
        filler = request.json.get('filler')
        decodeToken(bearer)
        Application.approveApplication(filler, id, provider)
        return jsonify({'message': 'Application #' + id + ' was approved'}), 200
    except DatabaseConnectionFailed as dcf:
        return jsonify({"message": "Something went wrong"}), 500
    except AuthorizationFailed as af:
        return jsonify({"message": af.message}), 401


@app.route("/applications/<id>/reject", methods=["POST"])
def rejectApplication(id):
    try:
        bearer = request.headers.get('Authorization')
        motive = request.json.get('motive')
        filler = request.json.get('filler')
        decodeToken(bearer)
        Application.rejectApplication(filler, id, motive)
        return jsonify({'message': 'Application #' + id + ' was rejected'}), 200
    except DatabaseConnectionFailed as dcf:
        return jsonify({"message": "Something went wrong"}), 500
    except AuthorizationFailed as af:
        return jsonify({"message": af.message}), 401