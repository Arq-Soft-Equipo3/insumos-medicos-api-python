import bcrypt
import jwt
import datetime


class AuthManager:
    def __init__(self):
        True

    def encodeAuthToken(self,userEmail):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=1),
                'iat': datetime.datetime.utcnow(),
                'sub': userEmail
            }
            return jwt.encode(
                payload,
                'super-secret',
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def authenticate(self, user, aPassword):
        userPassword = user.get('password').get('B')
        userEmail = user.get('email').get('S')

        if bcrypt.checkpw(aPassword.encode('utf8'), userPassword):
            return self.encodeAuthToken(userEmail).decode()
        else:
            return False