import os

import bcrypt
import jwt
import datetime


class AuthManager:
    def __init__(self):
        True

    @staticmethod
    def encodeAuthToken(userEmail):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=5),
                'iat': datetime.datetime.utcnow(),
                'sub': userEmail
            }
            return jwt.encode(
                payload,
                os.environ['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decodeAuthToken(anAuthToken):
        secretKey = os.environ['SECRET_KEY']
        try:
            payload = jwt.decode(anAuthToken, secretKey)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Token has expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def authenticate(self, user, aPassword):
        userPassword = user.get('password').get('B')
        userEmail = user.get('email').get('S')

        if bcrypt.checkpw(aPassword.encode('utf8'), userPassword):
            return self.encodeAuthToken(userEmail).decode()
        else:
            return False
