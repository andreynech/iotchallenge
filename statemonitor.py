#!/usr/bin/env python3

import time
import machinepark as mp
import boto3
import json
import threading


iot = boto3.client('iot')
iot_data = boto3.client('iot-data')


def update(machine_id, data_payload):
#    print(machine_id, data_payload)
    res = iot_data.update_thing_shadow(thingName = machine_id,
                                       payload = json.dumps(data_payload))
    return res


def update_chunk(chunk):
    for machine_id, data in chunk:
        update(machine_id, data)


if __name__ == "__main__":
        

    machine_ids = mp.machines_list()

    sample = {'env': {} }
    
    for mid in machine_ids:
        sample[mid] = {}
    
    for j in range(0, 10):
        start = time.time()
        
        mp.query_sample(machine_ids, sample)

        #print(sample)
        new_state_data = []

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

            new_state_data.append((machine_id, data_payload))

        threads = 64
        chunk_size = int(len(new_state_data) / threads)
        if chunk_size == 0:
            chunk_size = 1
            
        jobs = []
#        print(new_state_data)
        for c in mp.chunks(new_state_data, chunk_size):
#            print(c)
#            print('################################')
#            update_chunk(c)
            thread = threading.Thread(target = update_chunk, args = (c,))
            thread.start()
            jobs.append(thread)

        for j in jobs:
            j.join()
            
        # Measure timing
        end = time.time()
        duration = end - start

        print('Total machine count {0}'.format(len(machine_ids)))
        print('Completed in {0} seconds. {1} records per second'.format(duration, len(machine_ids) / duration))
