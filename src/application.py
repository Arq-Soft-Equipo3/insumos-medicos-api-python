from src import applicationStatus, applicationDatabaseManager, supplyProvider, customExceptions, idProvider
from src.customExceptions import DatabaseConnectionFailed, InstanceCreationFailed, StatusTransitionFailed
from src.applicationStatus import ApplicationStatus
from src.supplyProvider import SupplyProvider
from dynamodb_json import json_util as json
from src.user import User
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Application:
    def __init__(self, anEmailAddress, supplyName, area, drugName=None):
        self.assertFieldsNotEmpty(anEmailAddress, supplyName, area)
        self.ID = str(idProvider.getID())
        self.filler = anEmailAddress
        self.supply = self.assertIsValidSupply(supplyName)
        self.area = area
        self.status = ApplicationStatus.PENDING.value
        self.drugName = drugName
        self.timeStamp = str(datetime.datetime.now())

    @classmethod
    def assertIsValidSupply(cls, supplyName):
        for supply in SupplyProvider:
            if supply.value == supplyName:
                return supply.value
        logger.info('Invalid supply name: ' + supplyName)
        raise InstanceCreationFailed(supplyName + ' is not a valid Supply')

    @classmethod
    def assertFieldsNotEmpty(cls, anEmailAddress, supplyName, area):
        if anEmailAddress is None or supplyName is None or area is None:
            raise InstanceCreationFailed('Missing information')

    def cancel(self):
        self.status = ApplicationStatus.CANCELED.value

    def reject(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.REJECTED.value
        else:
            raise StatusTransitionFailed('Canceled applications cannot be rejected')

    def approve(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.APPROVED.value
        else:
            raise StatusTransitionFailed('Canceled applications cannot be approved')

    def cancelApplication(userEmail, appID):
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            app = objectManager.findApplicationBy(userEmail, appID)
            if app is None:
                raise ValueError('Application #' + appID + ' Does not exist for the current user')
            else:
                appID = app['applicationID']
                appStatus = app['status']
                appFiller = app['filler']
                appArea = app['area']
                appSupply = app['supply']
                app = Application(appFiller, appSupply, appArea)
                app.ID = appID
                app.status = appStatus
                app.cancel()
                objectManager.cancelApplication(app)
        except (ValueError, DatabaseConnectionFailed) as e:
            return e

    def addApplication(self):
        self.assertNotDuplicatePetition()
        item = self.itemToInsert()
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            resp = objectManager.dynamoDB().put_item(
                TableName=objectManager.applicationTable(),
                Item=item
            )
            return json.loads(item)
        except Exception as e:
            logger.error('Database error: ' + str(e))
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")

    def itemToInsert(self):
        if self.drugName is None:
            return {
                'applicationID': {'S': self.ID},
                'filler': {'S': self.filler},
                'area': {'S': self.area},
                'status': {'S': self.status},
                'supply': {'S': self.supply},
                'timeStamp': {'S': self.timeStamp}
            }
        else:
            return {
                'applicationID': {'S': self.ID},
                'filler': {'S': self.filler},
                'area': {'S': self.area},
                'status': {'S': self.status},
                'supply': {'S': self.supply},
                'medicine': {'S': self.drugName},
                'timeStamp': {'S': self.timeStamp}
            }

    def approveApplication(filler, appID, provider):
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            app = objectManager.findApplicationBy(filler, appID)
            if app is None:
                raise ValueError('Application #' + appID + ' Does not exist')
            else:
                appID = app['applicationID']
                appStatus = app['status']
                appFiller = app['filler']
                appArea = app['area']
                appSupply = app['supply']
                app = Application(appFiller, appSupply, appArea, None)
                app.ID = appID
                app.status = appStatus
                app.approve()
                objectManager.approveApplication(app, provider)
        except (ValueError, DatabaseConnectionFailed, StatusTransitionFailed) as e:
            return e

    def rejectApplication(filler, appID, aMotive):
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            app = objectManager.findApplicationBy(filler, appID)
            if app is None:
                raise ValueError('Application #' + appID + ' Does not exist')
            else:
                appID = app['applicationID']
                appStatus = app['status']
                appFiller = app['filler']
                appArea = app['area']
                appSupply = app['supply']
                app = Application(appFiller, appSupply, appArea, None)
                app.ID = appID
                app.status = appStatus
                app.reject()
                objectManager.rejectApplication(app, aMotive)
        except (ValueError, DatabaseConnectionFailed, StatusTransitionFailed) as e:
            return e

    def assertNotDuplicatePetition(self):
        objectManager = applicationDatabaseManager.DatabaseManager()
        app = objectManager.findExistingApplication(self.filler, self.supply, self.area, self.drugName)
        if app is not None:
            raise ValueError('A similar application is pending, please check again.')

    @classmethod
    def applicationsBy(cls, userEmail):
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            user = User.findUserByEmail(userEmail)
            if user.get('role').get('S') == 'administrator':
                return objectManager.allApplications()
            else:
                return objectManager.applicationsForUser(userEmail)
        except Exception as e:
            logger.error('Database error: ' + str(e))
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")
