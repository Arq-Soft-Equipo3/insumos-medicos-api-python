import os
import boto3
import bcrypt

#Database configuration
USER_TABLE = os.environ['USER1_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')
if IS_OFFLINE:
    dynamodb = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')

class User:
    def __init__(self, anEmailAddress, aPassword):
        self.email = anEmailAddress
        self.password = bcrypt.hashpw(aPassword.encode('utf8'), bcrypt.gensalt())

    def addUser(self):
        resp = dynamodb.put_item(
            TableName=USER_TABLE,
            Item={
                'email': {'S': self.email},
                'password': {'B': self.password}
            }
        )
        return resp

    def findUserByEmail(userEmail):
        user = dynamodb.get_item(
            TableName=USER_TABLE,
            Key={'email': {'S': userEmail}}
        )
        item = user.get('Item')
        if not item:
            return None
        return item



