import os
import boto3


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
