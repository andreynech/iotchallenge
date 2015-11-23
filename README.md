# Overview

This repository contains the set of Python scripts and JSON configuration files to implement the first task from Actyx challenge http://challenges.actyx.io/ .

We are using Amazon Web Services platform. In particular, the following services are used:
* IoT to keep track of the known devices and post updates
* SNS to send notifications about current alerts to subscribed users
* EC2 micro instance running machine state query/update script
* We are planing to use Kinesis, Machine Learning and DynamoDB to store all sensor data and search for correlations as requested by the second challenge task

# How it works

There is a createdev.py script which queries the machine park for all known machines. Then all machines are added to IoT repository with machine ID (UUID) as a unique thing name and two attributes: name and type which corresponds to machine name and type returned by machine park API. Machines names used by Actyx contains symbols which are not allowed by AWS IoT static propertis. That is why the python script replace them with those accepted by AWS IoT.

There is also the rule described in publish-to-sns-rule.json which is triggered by each update on device state and sends notification using preconfigured SNS subject. SQL-like query ensures that updates are sent only if current attribute is higher then current_alert.

Finally, there is statemonitor.py script which is permanently running on EC2 AMI micro instance and executing two steps:
* Query state for all known machines using Actyx machine park API. To reduce latency, query is performed using preconfigured amount of threads (currently 64).
* Update device (shadow) on AWS IoT by publishing new state to the corresonding MQTT topic associated with particular machne.

State updates trigger the rule which compares current and current_allert attributes and forward complete state data to the SNS subject if necessary. It in turns triggers email notification to subscribers.

