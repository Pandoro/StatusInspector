#!/usr/bin/env python

from optparse import OptionParser
import sys
import os
import re
import json
import time
import threading
import subprocess
import getpass
import pymongo
import signal
import datetime

proc_lines = [
'|    0       914    G   compiz                                         218MiB |',
'|    0      7017    G   ...ves-passed-by-fd --v8-snapshot-passed-by-    94MiB |',
'|    0      7893    C   python                                        1642MiB |',
'|    0     22343    C   ...e/hermans/sci-envs/sci-env3/bin/python3.5   135MiB |',
'|    0     32500    G   /usr/bin/X                                     496MiB |',
'|    0                  Not Supported                                         |',
'|    1     21570    C   /home/bereda/sci-env/bin/python3.4            3002MiB |']

for l in proc_lines:
    res = re.search('\| *(?P<gpu_id>\d+) *(?P<pid>\d*) *[CG]* *([\S|\s]*?)\s+(?P<mem>\d*)[MiB|\s\|]', l)
    print(res.group('gpu_id'),res.group('pid'),res.group('mem'))

exit()

mongo_client = pymongo.MongoClient(host='localhost', port=27018)
mongo_client['admin'].authenticate('admin','test123')

x = mongo_client['data']['machine_list'].find()
machines = []
for x_i in x:
    machines.append(x_i['machine'])

#x = mongo_client['data']['user_list'].find()
#for x_i in x:
#    print(x_i['user'])

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
