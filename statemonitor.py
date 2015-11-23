#!/usr/bin/env python3

import time
import machinepark as mp
import boto3
import json


if __name__ == "__main__":
        
    iot = boto3.client('iot')
    iot_data = boto3.client('iot-data')

    machine_ids = mp.machines_list()

    sample = {'env': {} }
    
    for mid in machine_ids:
        sample[mid] = {}
    
    while True:
        start = time.time()
        
        mp.query_sample(machine_ids, sample)

        # Measure timing
        end = time.time()
        duration = end - start

        #print(sample)

        for machine_id, data in sample.items():
            if machine_id == 'env':
                data_payload = {
                    "state": {
                        "reported": {
                            "pressure": data['pressure'][1],
                            "temperature": data['temperature'][1],
                            "humidity": data['humidity'][1],
                        },
                        "desired": {}
                    }
                }
            else:
                data_payload = {
                    "state": {
                        "reported": {
                            "current": data['current'],
                            "current_alert": data['current_alert']
                        },
                        "desired": {}
                    }
                }
            print(data_payload)
            iot_data.update_thing_shadow(thingName = machine_id,
                                         payload = json.dumps(data_payload))
                
        print('Total machine count {0}'.format(len(machine_ids)))
        print('Completed in {0} seconds. {1} records per second'.format(duration, len(machine_ids) / duration))
