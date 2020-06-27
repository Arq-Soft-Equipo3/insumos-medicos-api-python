import re
import bcrypt
from src import userDatabaseManager


class User:
    def __init__(self, anEmailAddress, aPassword, repeatedPassword, aPhone, anOrganization, aPosition, aCity):
        self.assertFieldsNotEmpty(anEmailAddress, aPassword, aPhone, anOrganization, aPosition, aCity)
        self.email = self.validateEmailAddressFor(anEmailAddress)
        self.password = self.checkAndGenerateHashedPassword(aPassword, repeatedPassword)
        self.phoneNumber = int(aPhone)
        self.organization = anOrganization
        self.position = aPosition
        self.city = aCity

    @classmethod
    def checkAndGenerateHashedPassword(cls, aPassword, anotherPassword):
        if aPassword == anotherPassword:
            return bcrypt.hashpw(aPassword.encode('utf8'), bcrypt.gensalt())
        else:
            raise ValueError('Passwords don not match')

    @classmethod
    def assertFieldsNotEmpty(cls,anEmailAddress, aPassword, aPhone, anOrganization, aPosition, aCity):
        if(not (not (anEmailAddress is None) and not (aPassword is None) and not (aPhone is None) and not (
                anOrganization is None) and not (aPosition is None) and not (aCity is None))):
            raise ValueError('Instance creation Failed')

    @classmethod
    def validateEmailAddressFor(cls, anEmailAddress):
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", anEmailAddress):
            raise ValueError('Invalid email address')
        else:
            return anEmailAddress

    def addUser(self):
        objectManager = userDatabaseManager.DatabaseManager()
        resp = objectManager.dynamoDB().put_item(
            TableName=objectManager.userTable(),
            Item={
                'email': {'S': self.email},
                'password': {'B': self.password}
            }
        )
        return resp

    def findUserByEmail(userEmail):
        objectManager = userDatabaseManager.DatabaseManager()
        user = objectManager.dynamoDB().get_item(
            TableName=objectManager.userTable(),
            Key={'email': {'S': userEmail}}
        )
        item = user.get('Item')
        if not item:
            return None
        return item
