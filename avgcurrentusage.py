import logging
import json
import decimal
from decimal import Decimal
import time
from datetime import datetime, timedelta
import boto3
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check(event, context):
    #logger.info(event)

    # Connect to DDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('currentusage')
    
    # Iterate over new records, calculate average current usage
    # and publish alert if necessary
    for record in event['Records']:
        if record["eventName"] == 'INSERT':
            devid = record['dynamodb']['Keys']['deviceid']['S']
            
            # Query all records for particular deviece
            condition = Key('deviceid').eq(devid)
            response = table.query(KeyConditionExpression = condition)

            history = []
            current_sum = 0.0
            
            # Iterate over records and calculate average current usage
            for item in response['Items']:
                timestampstr = item['sampletimestamp']
                timestamp = datetime.fromtimestamp(float(timestampstr) / 1000.0)
                current = float(item['payload']['current'])
                current_alert = float(item['payload']['current_alert'])
                current_sum += current
                history.append((devid, timestampstr, timestamp, current, current_alert))
            
            history_len = len(history)
            if history_len == 0: # Should not happen
                logger.info('No history data')
                return
            
            # Just extract attributes of latest item for convenient access later
            latest_devid, latest_timestampstr, latest_timestamp, latest_current, latest_current_alert = history[-1]
            
            avg_current = current_sum / history_len
            logger.info(history)
            logger.info('Setting avg current to {}'.format(avg_current))

            # See if we need to publish alert
            if latest_current >= latest_current_alert:
                # Publish SNS notification
                sns = boto3.client('sns')
                # Creating a topic is idempotent, so if it already exists
                # then we will just get the topic returned.
                topic_arn = sns.create_topic(Name = 'hi-current-alarm')['TopicArn']
                msg = 'Device {0} current usage allert {1}. \nCurrent use: {2} \nLast 5 minutes average {3}'.format(latest_devid, 
                    latest_current_alert, latest_current, avg_current)
                sns.publish(
                    TopicArn = topic_arn,
                    Message = msg,
                    Subject = 'Hi current'
                )

            # Removing old items.
            # History records are sorted. Latest item is the last one.
            report_period = timedelta(minutes = 5)
            history_horizon = latest_timestamp - report_period
            del_counter = 0
            for candidate in history:
                candidate_id, candidate_ts_str, candidate_ts, _, _ = candidate
                if latest_timestamp - candidate_ts > report_period:
                    del_counter += 1
                    logger.info('Deletion candidate {0} {1}'.format(candidate_id, candidate_ts_str))
                    response = table.delete_item(
                        Key = {
                            'deviceid': candidate_id,
                            'sampletimestamp': candidate_ts_str
                        }
                    )
                else:
                    break
            logger.info('{0} of {1} records should be deleted'.format(del_counter, history_len))
            
    logger.info("Successfully processed {} records.".format(len(event['Records'])))
