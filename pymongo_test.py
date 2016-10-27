#!/usr/bin/env python

from optparse import OptionParser
import sys
import os
import json
import time
import threading
import subprocess
import getpass
import pymongo
import signal
import datetime


mongo_client = pymongo.MongoClient(host='localhost', port=27018)
mongo_client['admin'].authenticate('admin','test123')

x = mongo_client['data']['machine_list'].find()
machines = []
for x_i in x:
    machines.append(x_i['machine'])

x = mongo_client['data']['user_list'].find()
for x_i in x:
    print(x_i['user'])

max_info = 5

if len(sys.argv) > 1:
    max_info = 20
    machines = [sys.argv[1]]

for m in machines:
    x = mongo_client['data']['load_info'].find({'machine' : m}).limit(max_info).sort('date', pymongo.DESCENDING)
    for x_i in x:
        print(x_i['machine'])
        print(x_i['date'])
        g = x_i.get('gpu')
        data = None
        try:
            data = mongo_client['data']['machine_info'].find({'machine' : x_i['machine']}).limit(1).sort('date', pymongo.DESCENDING)
            print(g)
            data = data[0]['configuration']['gpu_models']
        except:
            pass

        if g is not None:
            for k, v in g.items():
                if v['load'] != -1:
                    if data is None:
                        name = '???'
                    else:
                        name = data[k]
                    print(name, v['load'])
                    print(v['proc_info'])
                else:
                    print('no support')
        print(' ')
    print('============================================================================')
