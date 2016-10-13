#!/usr/bin/env python

import subprocess

def get_mem_info(machine='localhost', average_over_runs=5, sleep_between=0.25):
   info = subprocess.check_output(('ssh -o StrictHostKeyChecking=no {} '+
                                        '\'for i in {}; do; '+
                                        'ps axo user:20,pid; '+
                                        'nvidia-smi; '+
                                        'echo gpu-parsing-block-end ; '+
                                        'sleep {}; '+
                                        'done;\'').format(machine, ' '.join([str(i) for i in range(average_over_runs)]),sleep_between), shell=True)

   #Bring in the right format.
   info = info.decode('UTF-8')

   #Crop the blocks
   blocks = info.split('gpu-parsing-block-end')[:average_over_runs]
   for b in blocks:

       #Parse the block, first split it into ps and nvidia-smi
       block_info = b.split('\n')
       boundary = 0
       for i, l in enumerate(block_info):
           if '+--------' in l:
               boundary=i-1
               break
       ps_info = block_info[:boundary]
       gpu_info = block_info[boundary:]
       for l in gpu_info:
           print(l)

# use free -m for memory stats use this as another block.

# Next coding steps
# 1. nvidia smi parser
# 2. PID to user parser
# 3. mem parser
# 4. Averaging of data
# 5. Useful list of "to store data at time stamp.
# 6. Database storing
# 7. Running it every so and so often
# 8. running all the calls in parallel.


get_mem_info('hund')
import os
print(os.path.dirname(os.path.abspath(__file__)))
