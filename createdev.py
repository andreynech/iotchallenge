#!/usr/bin/env python3

import boto3
import json
import machinepark as mp
import dateutil.parser
from time import sleep

if __name__ == "__main__":
        
    iot_client = boto3.client('iot')

    machine_ids = mp.machines_list()

    sample = {}

    mp.query_sample(machine_ids, sample)

    envsensor = sample['env']

#    response = iot_client.create_thing(thingName='envsensor')

#    things = iot_client.list_things()
#    print(things)

    for id in machine_ids:
        machine = sample[id]
        allowed_name = machine['name'].replace(' ', '_')
        allowed_name = allowed_name.replace('[', '/')
        allowed_name = allowed_name.replace(']', '/')
        allowed_name = allowed_name.replace('(', ':')
        allowed_name = allowed_name.replace(')', ':')
        print('Adding {0}'.format(allowed_name))
        
        response = iot_client.create_thing(
            thingName = id,
            attributePayload = {
                'attributes': {
                    'name': allowed_name,
                    'type': machine['type'],
                }
            }
        )

        # Attach certificate to machine
        response = iot_client.attach_thing_principal(
            thingName = id,
            principal='arn:aws:iot:eu-west-1:048215596966:cert/aef57cc5c2c42617955bb958965aa78309dc037d035be20c6278ba2ccfb5a69b'
        )
        
#    iot_client.delete_thing(thingName='envsensor-1')
    
#    things = iot_client.list_things()
#    print(things)
