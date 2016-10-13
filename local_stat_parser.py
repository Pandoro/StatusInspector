#!/usr/bin/env python

# This script will run for a few seconds and parse important info about the system.

import sys
import subprocess
import re
import time

def parse_gpu_info_lines(gpu_lines):
    gpu_id = int(gpu_lines[0][1:5])
    gpu = {}
    fan, temp, cur_w, max_w, cur_mem, max_mem, load = re.search('\| *(\d+)\% *(\d+)C *P[0-9]+ *(\d+|\S+)W* / *(\d+|\S+)W* \| *(\d+)MiB / *(\d+)MiB \| *(\d+|\S+)', gpu_lines[1]).groups()
    gpu['fan'] = fan
    gpu['temp'] = temp
    gpu['cur_pow'] = int(cur_w) if cur_w != 'N/A' else -1
    gpu['max_pow'] = int(max_w) if max_w != 'N/A' else -1
    gpu['cur_mem'] = int(cur_mem) if cur_mem != 'N/A' else -1
    gpu['max_mem'] = int(max_mem) if max_mem != 'N/A' else -1
    gpu['load'] = int(load) if load != 'N/A' else -1

    return (gpu_id,gpu)

def parse_gpu_proc_lines(proc_lines):
    support ={}
    processes = []
    for l in proc_lines:
        proc_info = re.search('\| *(\d+) *(\d*) *[CG]* *(\S+) *(\d*)', l).groups()
        support[int(proc_info[0])] = not proc_info[1] == ''
        if proc_info[1] != '':
            processes.append((int(proc_info[0]), int(proc_info[1]), int(proc_info[3])))

    return support, processes



def parse_gpu_info(runs=20, wait=0.25):
    gpus = []
    #For a set of runs
    for r in  range(runs):
        #Parse the gpu info
        info = subprocess.check_output('nvidia-smi', shell=True).decode('UTF-8').split('\n')
        pid_info = subprocess.check_output('ps axo user:30,pid', shell=True).decode('UTF-8').split('\n')

        #Setup a map of pids->users for checking who uses the memory here.
        pid_to_user = {}
        for p in pid_info[1:]:
            p_info = re.search('(\S+) *(\d+)', p)
            if p_info is None:
                break
            else:
                p_info = p_info.groups()
            pid_to_user[int(p_info[1])] = p_info[0]

        #Parse the GPU info.
        block_boundary = 0
        while '|=====' not in info[block_boundary]:
            block_boundary +=1
        block_boundary +=1

        gpus_iter = {}
        while '+' == info[block_boundary+2][0]:
            gpu_id, gpu = parse_gpu_info_lines(info[block_boundary:block_boundary+2])
            gpus_iter[gpu_id] = gpu
            block_boundary += 3

        #Jump to the process info
        block_boundary += 5
        proc_info_support, proc_info = parse_gpu_proc_lines(info[block_boundary:-2])

        for g, support in proc_info_support.items():
            gpus_iter[g]['proc_info_support'] = support

        for gpu_id, pid, mem_usage in proc_info:
            if 'proc_info' not in gpus_iter[gpu_id].keys():
                gpus_iter[gpu_id]['proc_info'] = {}

            user = pid_to_user[pid]
            if user not in gpus_iter[gpu_id].keys():
                gpus_iter[gpu_id]['proc_info'][user] = mem_usage
            else:
                gpus_iter[gpu_id]['proc_info'][user] += mem_usage

        #Store the info and save it.
        gpus.append(gpus_iter)
        time.sleep(wait)

    #Now we need to summarize the infos.
    gpus_info = gpus[0]
    for g in gpus[1:]:
        for g_i in g.keys():
            #Take the max of some of the stats.
            for s in ['load', 'fan', 'cur_mem', 'cur_pow', 'temp']:
                gpus_info[g_i][s] = max([gpus_info[g_i][s], g[g_i][s]])
            #Fuse the user info. Some users might now be on the gpu for all runs.
            if gpus_info[g_i]['proc_info_support']:
                for u,m in g[g_i]['proc_info'].items():
                    if u in gpus_info[g_i]['proc_info'].keys():
                        gpus_info[g_i]['proc_info'][u] = max([gpus_info[g_i]['proc_info'][u], g[g_i]['proc_info'][u]])
                    else:
                        gpus_info[g_i]['proc_info'][u] = g[g_i]['proc_info'][u]

    return gpus_info


def main(argv):
    print(parse_gpu_info())




'''To store
General
* Max Memory
* Type of CPU
* nvidia driver
* Ubuntu variant
* Kernel version
* GPU Model (nvidia-smi -q | grep 'Product Name'


GPU info
* max GPU ram usage for each user if supported
* max GPU processing usage if available
* GPU Temperature

CPU info
* max Ram usage
* max Swap usage
* max CPU usage

General
* active users
'''


if __name__ == "__main__":
    main(sys.argv[1:])