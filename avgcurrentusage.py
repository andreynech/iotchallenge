import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check(event, context):
    logger.info(event)
    for record in event['Records']:
        #logger.info(record)
        #logger.info(record["eventID"])
        #logger.info(record["eventName"])
        if record["eventName"] == 'INSERT':
            current = float(record['dynamodb']['NewImage']['payload']['M']['current']['N'])
            current_alarm = float(record['dynamodb']['NewImage']['payload']['M']['current_alert']['N'])
            logger.info('Current {0}. Alarm {1}'.format(current, current_alarm))
    print ("Successfully processed {} records.".format(len(event['Records'])))
