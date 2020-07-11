import logging
import re
import bcrypt
from src import userDatabaseManager
from src.customExceptions import InstanceCreationFailed, DatabaseConnectionFailed

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class User:
    def __init__(self, anEmailAddress, aPassword, repeatedPassword, aPhone, anOrganization, aPosition, aCity):
        self.assertFieldsNotEmpty(anEmailAddress, aPassword, aPhone, anOrganization, aPosition, aCity)
        self.email = self.validateEmailAddressFor(anEmailAddress)
        self.password = self.checkAndGenerateHashedPassword(aPassword, repeatedPassword)
        self.phoneNumber = int(aPhone)
        self.organization = anOrganization
        self.position = aPosition
        self.city = aCity
        self.role = 'user'

    @classmethod
    def checkAndGenerateHashedPassword(cls, aPassword, anotherPassword):
        if aPassword == anotherPassword:
            return bcrypt.hashpw(aPassword.encode('utf8'), bcrypt.gensalt())
        else:
            logger.info('Log: Passwords does not match')
            raise InstanceCreationFailed('Passwords does not match')

    @classmethod
    def assertFieldsNotEmpty(cls, anEmailAddress, aPassword, aPhone, anOrganization, aPosition, aCity):
        if (not (not (anEmailAddress is None) and not (aPassword is None) and not (aPhone is None) and not (
                anOrganization is None) and not (aPosition is None) and not (aCity is None))):
            logger.info(
                'Log: One parameter is missing ' + str(anEmailAddress) + str(aPhone) + str(anOrganization) + str(
                    aPosition) + str(aCity))
            raise InstanceCreationFailed('Missing Information')

    @classmethod
    def validateEmailAddressFor(cls, anEmailAddress):
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", anEmailAddress):
            logger.info('Invalid email address ' + anEmailAddress)
            raise InstanceCreationFailed('Invalid email address')
        else:
            return anEmailAddress

    @classmethod
    def findUserByEmail(cls, userEmail):
        #Should return an instantiated user
        try:
            return userDatabaseManager.DatabaseManager().findUserByEmail(userEmail)
        except Exception as e:
            logger.error('Database error occurred: ' + str(e))
            raise DatabaseConnectionFailed('Connection with the database failed, please try again later')

    def addUser(self):
        try:
            userDatabaseManager.DatabaseManager().addUser(self)
        except Exception as e:
            logger.error('Database error occurred: ' + str(e))
            raise DatabaseConnectionFailed('Connection with the database failed, please try again later')

    def isAdministrator(self):
        return self.role == 'Administrator'



