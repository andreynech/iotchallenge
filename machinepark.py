#!/usr/bin/env python3

import threading
import requests
import json

api_root = 'http://machinepark.actyx.io/api/v1/'
machines_list_uri = api_root + 'machines'
machine_detail_uri = api_root + 'machine/{0}'
env_sensor_uri = api_root + 'env-sensor'

        
def env_sensor(sample):
    """Query environmental sensor data"""
    response = requests.get(env_sensor_uri)
    results = json.loads(response.text)
    sample['env'] = results
    return results


def machines_list():
    """Query for all machienes in park"""
    response = requests.get(machines_list_uri)
    results = json.loads(response.text)
    ret = []
    for machine_info in results:
        ret.append(machine_info.replace('$API_ROOT/machine/', ''))
    return ret


def machine_detail(machine_id):
    """Query machine detail"""
    uri = machine_detail_uri.format(machine_id)
    response = requests.get(uri)
    results = json.loads(response.text)
    return results


def machine_detail_chunk(id_list, sample):
    for x in id_list:
        sample[x] = machine_detail(x)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def query_sample(machine_ids, sample, threads = 64):

    chunk_size = int(len(machine_ids) / threads)
    if chunk_size == 0:
        chunk_size = 1
        threads = 1

    jobs = []
        
    for c in chunks(machine_ids, chunk_size):
        thread = threading.Thread(target = machine_detail_chunk, args = (c, sample))
        thread.start()
        jobs.append(thread)

    env_sensor(sample)
        
    # Ensure all of the threads have finished
    for j in jobs:
        j.join()
