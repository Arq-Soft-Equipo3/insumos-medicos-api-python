import os
import boto3


class DatabaseManager:
    def __init__(self):
        self.user_Table = os.environ['USER1_TABLE']
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

    def userTable(self):
        return self.user_Table
