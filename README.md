# Overview

This repository contains the set of Python scripts and JSON configuration files to implement the first task from Actyx challenge http://challenges.actyx.io/ .

We are using Amazon Web Services platform. In particular, the following services are used:
* IoT to keep track of the known devices and post updates
* SNS to send notifications about current alerts to subscribed users
* EC2 micro instance running machine state query/update script
* DynamoDB to store 5 minutes history for average current consumption calculation
* Lambda to perform average calculation and publish SNS updates
* We are planing to use Machine Learning and S3 to store all sensor data and search for correlations as requested by the second challenge task

# How it works

There is a createdev.py script which queries the machine park for all known machines. Then all machines are added to IoT repository with machine ID (UUID) as a unique thing name and two attributes: name and type which corresponds to machine name and type returned by machine park API. Machines names used by Actyx contains symbols which are not allowed by AWS IoT static propertis. That is why the python script replace them with those accepted by AWS IoT.

There is also the rule described in publish-to-sns-rule.json which is triggered by each update on device state and sends notification using preconfigured SNS subject. SQL-like query ensures that updates are sent only if current attribute is higher then current_alert. This corresponds to the "simple" part of the first challenge.

To implement the 5 minutes average part of the first challenge we create the rule to store state updates in DynamoDB. Please see store-to-ddb-rule.json for the rule implementation. In addition we configure Lambda function (trigger) which is executed every time the new record is added to the DynamoDB table. This function is in the avgcurrentusage.py and performs the following activities:
* Calculates average current usage based on the 5 minutes history data for particular device
* Publish SNS alert if current usage exceeds the configured alarm level
* Removes outdated history records from the DynamoDB table

Finally, there is statemonitor.py script which is permanently running on EC2 AMI micro instance and executing two steps:
* Query state for all known machines using Actyx machine park API. To reduce latency, query is performed using preconfigured amount of threads (currently 64).
* Update device (shadow) on AWS IoT by publishing new state to the corresonding MQTT topic associated with particular machne.

State updates trigger the rule which compares current and current_allert attributes and forward state data either to the SNS subject if necessary or to DynamoDB for average calculation. It in turns triggers email notification to subscribers.

# Analytics support
To perform data analysis as requested by the thecond challenge task, we need to capture all sensor data. For these purposes we configured AWS Firehose stream to store all incoming data to S3 bucket. Later on we can load these data to AWS RedShift, AWS Machine Learning or perform custom analysis. We provide publish-to-firehose.json rule which instructs AWS IoT infrastructure to forward all machine state updates to the Firehose stream.
