#!/usr/bin/env python3

import time
import machinepark as mp


if __name__ == "__main__":
        
    machine_ids = mp.machines_list()

    sample = {'envsensor': {} }
    
    for mid in machine_ids:
        sample[mid] = {}
    
    for i in range(0, 10):
        start = time.time()
        
        mp.query_sample(machine_ids, sample)

        # Measure timing
        end = time.time()
        duration = end - start

        #print(sample)
        print('Total machine count {0}'.format(len(machine_ids)))
        print('Completed in {0} seconds. {1} records per second'.format(duration, len(machine_ids) / duration))
    
