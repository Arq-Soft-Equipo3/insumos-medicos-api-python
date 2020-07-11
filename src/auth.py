import os

import bcrypt
import jwt
import datetime

from src.customExceptions import AuthorizationFailed


class AuthManager:
    def __init__(self):
        True

    @staticmethod
    def encodeAuthToken(userEmail, userRole):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=5),
                'iat': datetime.datetime.utcnow(),
                'sub': userEmail,
                'role': userRole
            }
            return jwt.encode(
                payload,
                os.environ['SECRET_KEY'],
                algorithm='HS256'
            )
        except:
            raise AuthorizationFailed('Authentication Failed, try again')

    @staticmethod
    def decodeAuthToken(anAuthToken):
        secretKey = os.environ['SECRET_KEY']
        try:
            payload = jwt.decode(anAuthToken, secretKey)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise AuthorizationFailed('Token has expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise AuthorizationFailed('Invalid token. Please log in again.')

    def authenticate(self, user, aPassword):
        userPassword = user.get('password').get('B')
        userEmail = user.get('email').get('S')
        userRole = user.get('role').get('S')

        if bcrypt.checkpw(aPassword.encode('utf8'), userPassword):
            return self.encodeAuthToken(userEmail, userRole).decode()
        else:
            raise AuthorizationFailed('Invalid credentials. Try again')
