from src import applicationStatus, applicationDatabaseManager, supplyProvider, customExceptions, idProvider
from src.customExceptions import DatabaseConnectionFailed, InstanceCreationFailed, StatusTransitionFailed
from src.applicationStatus import ApplicationStatus
from src.supplyProvider import SupplyProvider
import datetime


class Application:
    def __init__(self, anEmailAddress, supplyName, area, drugName):
        self.assertFieldsNotEmpty(anEmailAddress, supplyName, area)
        self.ID = str(idProvider.getID())
        self.filler = anEmailAddress
        self.supply = self.assertIsValidSupply(supplyName)
        self.area = area
        self.status = ApplicationStatus.PENDING.value
        self.drugName = drugName
        self.timeStamp = datetime.datetime.now()

    @classmethod
    def assertIsValidSupply(cls, supplyName):
        for supply in SupplyProvider:
            if supply.value == supplyName:
                return supply.value
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

    def approveApplication(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.ACCEPTED.value
        else:
            raise StatusTransitionFailed('Canceled applications cannot be approved')

    def cancelApplication(userEmail, appID):
        try:
            app = applicationDatabaseManager.DatabaseManager().findApplicationBy(userEmail, appID)
            if app is None:
                raise ValueError('Application #' + appID + ' Does not exist for the current user')
            else:
                appID = app['applicationID'].get('S')
                appStatus = app['status'].get('S')
                appFiller = app['filler'].get('S')
                appArea = app['area'].get('S')
                appSupply = app['supply'].get('S')
                app = Application(appFiller, appSupply, appArea, None)
                app.ID = appID
                app.status = appStatus
                app.cancel()
                app.updateWithNewStatus()
        except (ValueError, DatabaseConnectionFailed) as e:
            return e

    def addApplication(self):
        self.itemToInsert()
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            resp = objectManager.dynamoDB().put_item(
                TableName=objectManager.applicationTable(),
                Item=self.itemToInsert()
            )
            return self.ID
        except:
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

    def updateWithNewStatus(self):
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            resp = objectManager.dynamoDB().update_item(
                TableName=objectManager.applicationTable(),
                Key={
                    'applicationID': {'S': self.ID},
                    'filler': {'S': self.filler}
                },
                UpdateExpression="set #stat = :stat",
                ExpressionAttributeValues={
                    ':stat': {'S': self.status}
                },
                ExpressionAttributeNames={
                    '#stat': 'status'
                }
            )
        except:
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")

    def applicationsBy(userEmail):
        try:
            objectManager = applicationDatabaseManager.DatabaseManager()
            applications = objectManager.dynamoDB().query(
                TableName=objectManager.applicationTable(),
                KeyConditionExpression='filler = :filler',
                ExpressionAttributeValues={':filler': {'S': userEmail}}
            )
            items = applications['Items']
            if not items:
                return []
            return items
        except:
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")
