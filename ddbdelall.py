#!/usr/bin/env python3

import boto3
from boto3.dynamodb.conditions import Key, Attr

# Connect to DDB
client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('currentusage')
response = client.scan(TableName='currentusage')

# Iterate over records
l = len(response['Items'])
i = 0

for item in response['Items']:
    devid = item['deviceid']['S']
    timestampstr = item['sampletimestamp']['S']

    k = {
        'deviceid': devid,
        'sampletimestamp': timestampstr
    }
    res = table.delete_item(Key = k)
    print('{0} out of {1}'.format(i, l))
    i += 1
