#!/usr/bin/env python3

import os
import json


raw_data_dir = 'rawdata'
unpacked_data_dir = 'unpacked'


for (_, _, filenames) in os.walk(raw_data_dir):
    for filename in filenames:
        filename = os.path.join(raw_data_dir, filename)
        print(filename, '##################')

        with open(filename, 'r') as f:
            stringified_data = f.read();

        raw_data = json.loads('[' + stringified_data.replace('}{', '},{') + ']')

        for sample in raw_data:
            devid = sample['devid']
            if devid == 'env':
                filename = os.path.join(unpacked_data_dir, devid + '_humidity')
                with open(filename, 'a') as f:
                    data = '{0}\t{1}\n'.format(sample['timestamp'], sample['humidity'])
                    f.write(data)
                filename = os.path.join(unpacked_data_dir, devid + '_pressure')
                with open(filename, 'a') as f:
                    data = '{0}\t{1}\n'.format(sample['timestamp'], sample['pressure'])
                    f.write(data)
                filename = os.path.join(unpacked_data_dir, devid + '_temperature')
                with open(filename, 'a') as f:
                    data = '{0}\t{1}\n'.format(sample['timestamp'], sample['temperature'])
                    f.write(data)
            else:
                filename = os.path.join(unpacked_data_dir, devid)
                with open(filename, 'a') as f:
                    data = '{0}\t{1}\n'.format(sample['timestamp'], sample['current'])
                    f.write(data)
                with open(filename + '_alert', 'a') as f:
                    data = '{0}\t{1}\n'.format(sample['timestamp'], sample['current_alert'])
                    f.write(data)
