from src import applicationStatus, applicationDatabaseManager
from src.applicationStatus import ApplicationStatus
from src import idProvider


class Application:
    def __init__(self, anEmailAddress, supplyName, area):
        self.assertFieldsNotEmpty(anEmailAddress, supplyName, area)
        self.ID = str(idProvider.getID())
        self.filler = anEmailAddress
        self.supply = supplyName
        self.area = area
        self.status = ApplicationStatus.PENDING.value

    @classmethod
    def assertFieldsNotEmpty(cls, anEmailAddress, supplyName, area):
        if anEmailAddress is None or supplyName is None or area is None:
            raise ValueError('Instance creation Failed')

    def cancelApplication(self):
        self.status = ApplicationStatus.CANCELED.value

    def approveApplication(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.ACCEPTED.value
        else:
            raise ValueError('Canceled applications cannot be approved')

    def addApplication(self):
        objectManager = applicationDatabaseManager.DatabaseManager()
        resp = objectManager.dynamoDB().put_item(
            TableName=objectManager.applicationTable(),
            Item={
                'applicationID': {'S': self.ID},
                'filler': {'S': self.filler},
                'supply': {'S': self.supply},
                'area': {'S': self.area},
                'status': {'S': self.status}
            }
        )
        return self.ID

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
