from src import applicationStatus, applicationDatabaseManager
from src.applicationStatus import ApplicationStatus
from src.supplyProvider import SupplyProvider
from src import idProvider


class Application:
    def __init__(self, anEmailAddress, supplyName, area, drugName):
        self.assertFieldsNotEmpty(anEmailAddress, supplyName, area)
        self.ID = str(idProvider.getID())
        self.filler = anEmailAddress
        self.supply = self.assertIsValidSupply(supplyName)
        self.area = area
        self.status = ApplicationStatus.PENDING.value
        self.drugName = drugName

    @classmethod
    def assertIsValidSupply(cls, supplyName):
        for supply in SupplyProvider:
            if supply.value == supplyName:
                return supply.value
        raise ValueError(supplyName + ' is not a valid Supply')

    @classmethod
    def assertFieldsNotEmpty(cls, anEmailAddress, supplyName, area):
        if anEmailAddress is None or supplyName is None or area is None:
            raise ValueError('Instance creation Failed')

    def cancel(self):
        self.status = ApplicationStatus.CANCELED.value

    def reject(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.REJECTED.value
        else:
            raise ValueError('Canceled applications cannot be rejected')

    def approveApplication(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.ACCEPTED.value
        else:
            raise ValueError('Canceled applications cannot be approved')

    def cancelApplication(userEmail, appID):
        app = applicationDatabaseManager.DatabaseManager().findApplicationBy(userEmail, appID)
        if app is None:
            return ValueError('Application #' + appID + ' Does not exist for the current user')
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

    def addApplication(self):
        if self.drugName is None:
            itemToInsert = {
                'applicationID': {'S': self.ID},
                'filler': {'S': self.filler},
                'area': {'S': self.area},
                'status': {'S': self.status},
                'supply': {'S': self.supply},
            }
        else:
            itemToInsert ={
                'applicationID': {'S': self.ID},
                'filler': {'S': self.filler},
                'area': {'S': self.area},
                'status': {'S': self.status},
                'supply': {'S': self.supply},
                'medicine': {'S': self.drugName}
            }
        objectManager = applicationDatabaseManager.DatabaseManager()
        resp = objectManager.dynamoDB().put_item(
            TableName=objectManager.applicationTable(),
            Item= itemToInsert
        )
        return self.ID

    def updateWithNewStatus(self):
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

    def applicationsBy(userEmail):
        objectManager = applicationDatabaseManager.DatabaseManager()
        applications = objectManager.dynamoDB().query(
            TableName=objectManager.applicationTable(),
            KeyConditionExpression='filler = :filler',
            ExpressionAttributeValues={':filler': {'S': userEmail}}
        )
        items = applications['Items']
        if not items:
            return None
        return items
