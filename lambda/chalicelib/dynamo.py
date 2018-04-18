import boto3
import boto3.exceptions
import os
import time
import datetime
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

class SecretDB:
    def __init__(self,table):
        self.table = table

    def __create__(self):
        pass

    def putItem(self, key, ttl, value, expires):
        try:
            tbl = dynamodb.Table(self.table)
            return tbl.put_item(Item={
                'id' : key,
                'ttl': ttl,
                'secret': value,
                'expires': expires
            })
        except Exception as ex:
            print("put item exception:",ex)
    
    def getItem(self, key, epoch):
        try:
            tbl = dynamodb.Table(self.table)
            items = tbl.query(
                KeyConditionExpression=Key('id').eq(key),
                FilterExpression=Attr('ttl').gte(epoch)
            )
            #print(items)
            if ( items['Count'] > 0 ) :
                item = items['Items'][0]
                tbl.delete_item(Key={
                    'id' : item['id']
                })
                return item
            return {}
        except Exception as ex:
            print("get item exception:",ex)
            return {}  
    
#https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html