import logging
import os
import boto3

from src.customExceptions import DatabaseConnectionFailed

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
