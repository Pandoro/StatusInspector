#!/usr/bin/env python

# This script will run for a few seconds and parse important info about the system.

from optparse import OptionParser
import sys
import subprocess
import re
import time
import json


def parse_gpu_info_lines(gpu_lines):
    """Parses the gpu info from 2 lines cut out from the nvidia-smi result.

    Args:
        gpu_lines (list of strings): Two nvidi-smi lines representing current gpu info.

    Returns:
        Tuple: Gpu id ('gpuX') and a dict with gpu info.
    """

    gpu_id = 'gpu{}'.format(int(gpu_lines[0][1:5]))
    gpu = {}
    fan, temp, cur_w, max_w, cur_mem, max_mem, load = re.search('\| *(\d+)\% *(\d+)C *\S+ *(\d+|\S+)W* / *(\d+|\S+)W* \| *(\d+)MiB / *(\d+)MiB \| *(\d+|\S+)', gpu_lines[1]).groups()
    gpu['fan'] = int(fan)
    gpu['temp'] = int(temp)
    gpu['cur_pow'] = int(cur_w) if cur_w != 'N/A' else -1
    gpu['max_pow'] = int(max_w) if max_w != 'N/A' else -1
    gpu['cur_mem'] = int(cur_mem) if cur_mem != 'N/A' else -1
    gpu['max_mem'] = int(max_mem) if max_mem != 'N/A' else -1
    gpu['load'] = int(load) if load != 'N/A' else -1

    return (gpu_id,gpu)


def parse_gpu_proc_lines(proc_lines):
    """Parses the information from the nvidia-smi process lines (if available).

    Args:
        proc_lines (list of strings): All the nvidi-smi output lines with process info.

    Returns:
        Tuple: A dict with showing the detailed process info support of the gpu
               and a list of process info.
    """

    support ={}
    processes = []
    for l in proc_lines:
        proc_info = re.search('\| *(?P<gpu_id>\d+) *(?P<pid>\d*) *[CG]* *([\S|\s]*?)\s+(?P<mem>\d*)[MiB|\s\|]', l)
        gpu_id = 'gpu{}'.format(int(proc_info.group('gpu_id')))
        support[gpu_id] = not (proc_info.group('pid') == '')
        if support[gpu_id]:
            processes.append((gpu_id, int(proc_info.group('pid')), int(proc_info.group('mem'))))

    return (support, processes)


def parse_gpu_info(runs=20, wait=0.25):
    """Performs several runs of parsing the GPU info from nvidia-smi.

    Args:
        runs (int, optional): Number of runs
        wait (float, optional): Seconds to wait between the runs.

    Returns:
        Dict: Compiled GPU info across the several runs.
    """

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
            gpus_iter[gpu_id]['proc_info_support'] = True # will be wet to False automaticallly if parsed later on.
            gpus_iter[gpu_id]['proc_info'] = {}
            block_boundary += 3

        #Jump to the process info
        block_boundary += 5
        proc_info_support, proc_info = parse_gpu_proc_lines(info[block_boundary:-2])

        for g, support in proc_info_support.items():
            gpus_iter[g]['proc_info_support'] = support

        for gpu_id, pid, mem_usage in proc_info:
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


def parse_cpu_info(runs=5, wait=0.1):
    """Performs several runs of parsing the CPU info.

    Args:
        runs (int, optional): Number of runs
        wait (float, optional): Seconds to wait between the runs.

    Returns:
        Dict: Compiled CPU info across the several runs.
    """

    cpus = []
    #For a set of runs
    for r in  range(runs):
        cpus_iter = {}

        #Get the memory info
        mem_info = subprocess.check_output('cat /proc/meminfo | grep --color=no \'Swap\|Mem\|Cached\|Buffers\'', shell=True).decode('UTF-8').split('\n')
        mem_dict = {}
        for m in mem_info[:-1]:
            k,v= re.search('(\S+): *(\d+)',m).groups()
            mem_dict[k] = v
        cpus_iter['max_ram'] = int(mem_dict['MemTotal']) // 1024
        cpus_iter['used_ram'] = cpus_iter['max_ram'] - (int(mem_dict['Cached'])+int(mem_dict['Buffers'])+int(mem_dict['MemFree'])) // 1024
        cpus_iter['max_swap'] = int(mem_dict['SwapTotal']) // 1024
        cpus_iter['used_swap'] = cpus_iter['max_swap'] - int( mem_dict['SwapFree']) // 1024


        #Get set of users with processes
        pid_info = subprocess.check_output('ps axo user:30', shell=True).decode('UTF-8').split('\n')
        cpus_iter['users'] = set(pid_info[1:-1])

        #Get the cpu usage
        cpu_info = subprocess.check_output('/usr/bin/top -bn2 -d 2 | grep --color=no \'Cpu(s)\' | tail -1', shell=True).decode('UTF-8')
        usr_load, sys_load = proc_info = re.search('\%*Cpu\(s\): *(\d+.\d+)[ |\%]us, *(\d+.\d+)', cpu_info).groups()
        cpus_iter['load'] = (float(usr_load) + float(sys_load))

        #Store the info and save it.
        cpus.append(cpus_iter)
        time.sleep(wait)

    #Summarize
    cpu_info = cpus[0]
    for c in cpus[1:]:
        for s in ['load', 'used_swap', 'used_ram']:
            cpu_info[s] = max([cpu_info[s] ,c[s]])

        cpu_info['users'] |=  c['users']

    #Because json doesn't do sets
    cpu_info['users'] = list(cpu_info['users'])

    return cpu_info


def parse_machine_info():
    """Parses general machine info about hardware and software.

    Returns:
        Dict representing the machine info.
    """

    machine = {}

    #Max memory
    mem_info = subprocess.check_output('cat /proc/meminfo | grep --color=no MemTotal', shell=True).decode('UTF-8')
    k,v= re.search('(\S+): *(\d+)',mem_info).groups()
    machine['memory'] = int(v)//1024

    mem_info = subprocess.check_output('cat /proc/meminfo | grep --color=no SwapTotal', shell=True).decode('UTF-8')
    k,v= re.search('(\S+): *(\d+)',mem_info).groups()
    machine['swap'] = int(v)//1024

    #CPU info
    cpu_info = subprocess.check_output('cat /proc/cpuinfo | grep --color=no \'model name\'', shell=True).decode('UTF-8').split('\n')
    cpu_model = re.search('\S* *: *([\S *]+)',cpu_info[0]).groups()[0]
    machine['cpu_model'] = '{} (x{})'.format(cpu_model, len(cpu_info)-1)

    #Nvidia driver + GPU Model
    nvidia_info = subprocess.check_output('nvidia-smi -q | grep --color=no \'Driver Version\|Product Name\|Minor Number\'', shell=True).decode('UTF-8').split('\n')
    machine['nvidia_version'] = re.search('\S* *: *(\d+.+\d+)',nvidia_info[0]).groups()[0]
    machine['gpu_models'] = {}
    for i in range(1,len(nvidia_info)-1,2):
        gpu_model = re.search('\S* *: *([\S *]+)',nvidia_info[i]).groups()[0]
        gpu_id = re.search('\S* *: *(\d+)',nvidia_info[i+1]).groups()[0]
        machine['gpu_models']['gpu'+gpu_id] = gpu_model

    #Ubuntu variant
    ubuntu_info = subprocess.check_output('lsb_release -a 2>/dev/null | grep --color=no Description', shell=True).decode('UTF-8')
    machine['ubuntu_version'] = re.search('\S*:\W*([\S *]+)',ubuntu_info).groups()[0]

    #Kernel version
    machine['kernel_version'] = subprocess.check_output('cat /proc/version', shell=True).decode('UTF-8')[:-1]

    return machine


def main(argv):
    """Executes the parsing of all the info.

    Args:
        argv : List of arguments. '-g' specifies only the general info is provided.
               Otherwise, only the detailed info is provided. This info is printed
               as a json string.

    """
    parser = OptionParser()
    parser.add_option('-g','--general', action='store_true', dest='return_general_info', default=False,
                      help='When set, general machine info will be returned instead of detailed cpu and gpu info.')
    parser.add_option('-p','--pretty', action='store_true', dest='print_pretty', default=False,
                      help='When set, the json will be printed in a less compact but more readable format.')

    (options, args) = parser.parse_args(argv)

    info = {}
    if options.return_general_info:
        info['configuration'] = parse_machine_info()
    else:
        info['gpu'] = parse_gpu_info()
        info['cpu'] = parse_cpu_info()

    #Compact encoding in json.
    if options.print_pretty:
        print(json.dumps(info, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        print(json.dumps(info, separators=(',',':')))


if __name__ == "__main__":
    main(sys.argv[1:])