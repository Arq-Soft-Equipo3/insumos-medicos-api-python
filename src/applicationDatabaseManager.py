import logging
import os
import boto3

from src.applicationStatus import ApplicationStatus
from src.customExceptions import DatabaseConnectionFailed
from src.supplyProvider import SupplyProvider

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DatabaseManager:
    def __init__(self):
        self.application_Table = os.environ['APPLICATION_TABLE']
        self.dynamo_db = self.onlineConfiguration()

    @classmethod
    def onlineConfiguration(cls):
        isOffline = os.environ.get('IS_OFFLINE')
        if isOffline:
            return boto3.client(
                'dynamodb',
                region_name='localhost',
                endpoint_url='http://localhost:8000')
        else:
            return boto3.client('dynamodb', region_name='us-east-1')

    def dynamoDB(self):
        return self.dynamo_db

    def applicationTable(self):
        return self.application_Table

    def findApplicationBy(self, userEmail, applicationID):
        application = self.dynamoDB().get_item(
            TableName=self.applicationTable(),
            Key={
                'applicationID': {'S': applicationID},
                'filler': {'S': userEmail}
            }
        )
        item = application.get('Item')
        if not item:
            return None
        return item

    def allApplications(self):
        applications = self.dynamoDB().scan(
            TableName=self.applicationTable()
        )
        items = applications['Items']
        if not items:
            return []
        return items

    def applicationsForUser(self, userEmail):
        applications = self.dynamoDB().query(
            TableName=self.applicationTable(),
            KeyConditionExpression='filler = :filler',
            ExpressionAttributeValues={':filler': {'S': userEmail}}
        )
        items = applications['Items']
        if not items:
            return []
        return items

    def cancelApplication(self, anApplication):
        try:
            self.dynamoDB().update_item(
                TableName=self.applicationTable(),
                Key={
                    'applicationID': {'S': anApplication.ID},
                    'filler': {'S': anApplication.filler}
                },
                UpdateExpression="set #stat = :stat",
                ExpressionAttributeValues={
                    ':stat': {'S': anApplication.status}
                },
                ExpressionAttributeNames={
                    '#stat': 'status'
                }
            )
        except Exception as e:
            logger.error('Database error: ' + str(e))
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")

    def approveApplication(self, anApplication, aProvider):
        try:
            self.dynamoDB().update_item(
                TableName=self.applicationTable(),
                Key={
                    'applicationID': {'S': anApplication.ID},
                    'filler': {'S': anApplication.filler}
                },
                UpdateExpression="set #stat = :stat, #prov = :provider",
                ExpressionAttributeValues={
                    ':stat': {'S': anApplication.status},
                    ':provider': {'S': aProvider}
                },
                ExpressionAttributeNames={
                    '#stat': 'status',
                    '#prov': 'provider'
                }
            )
        except Exception as e:
            logger.error('Database error: ' + str(e))
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")

    def rejectApplication(self, anApplication, aMotive):
        try:
            self.dynamoDB().update_item(
                TableName=self.applicationTable(),
                Key={
                    'applicationID': {'S': anApplication.ID},
                    'filler': {'S': anApplication.filler}
                },
                UpdateExpression="set #stat = :stat, #motive = :motive",
                ExpressionAttributeValues={
                    ':stat': {'S': anApplication.status},
                    ':motive': {'S': aMotive}
                },
                ExpressionAttributeNames={
                    '#stat': 'status',
                    '#motive': 'motive'
                }
            )
        except Exception as e:
            logger.error('Database error: ' + str(e))
            raise DatabaseConnectionFailed("Connection with the database failed, please try again later")

    # This method should do the query in the database. This will be correctly implemented soon.
    # I filtered this in memory because I need a little more time to learn 'bout complex querys in Dynamo
    def findExistingApplication(self, anEmailAddress, supplyName, area, drugName=None):
        applications = self.applicationsForUser(anEmailAddress)
        if applications:
            return self.findIfExistingApplication(applications, supplyName, area, drugName)
        else:
            return None

    def findIfExistingApplication(self, applications, supplyName, area, drugName=None):
        for app in applications:
            if app['area'].get('S') == area and app['supply'].get('S') == supplyName and app['status'].get(
                    'S') == ApplicationStatus.PENDING.value and (
                    app['supply'].get('S') == SupplyProvider.MEDICAMENTO.value and app['medicine'].get(
                'S') == drugName):
                print('I encountered something!')
                return app
