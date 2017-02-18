import StatusInspector as stasi

import os
import time

class MemoryParser(stasi.Parser):
    def __init__(self):
        #TODO make these parameters once it becomes clear how parameters will be dealt with.
        self.runs = 50
        self.ms_between_runs = 10
        self.aggregation_function = max

    def description(self):
        return 'Parse the memory usage.'

    def parse(self):
        res = 1
        #For a given set of runs
        run_stats = []
        for r in range(self.runs):
            #Collect all the proces ids
            pids = [int(pid) for pid in os.listdir('/proc') if pid.isdigit()]
            uid_to_mem = {'ram_per_user' : {}, 'swap_per_user' : {}}
            #For each try to open the status file
            for p in pids:
                try:
                    with open('/proc/{}/status'.format(p), 'r') as f:
                        #Collect their owner and the memory usage
                        uid = None
                        m = None
                        s = None
                        for l in f:
                            if l.startswith('Uid:'):
                                uid = int(l.split('\t')[1])
                            if l.startswith('VmRSS:'):
                                m = int(l.split('\t')[1][:-4])
                            if l.startswith('VmSwap:'):
                                s = int(l.split('\t')[1][:-4])
                        if uid is not None:
                            if m is not None and m > 0:
                                if not uid in uid_to_mem['ram_per_user']:
                                    uid_to_mem['ram_per_user'][uid] = 0
                                uid_to_mem['ram_per_user'][uid] += m
                            if s is not None and s > 0:
                                if not uid in uid_to_mem['swap_per_user']:
                                    uid_to_mem['swap_per_user'][uid] = 0
                                uid_to_mem['swap_per_user'][uid] += s
                except IOError:
                    pass # File disappeared by now, not relevant anymore.

            line_map = {}
            with open('/proc/meminfo'.format(p), 'r') as f:
                for l in f:
                    l = l.split(' ')
                    line_map[l[0][:-1]] = int(l[-2]) if l[-1] == 'kB\n' else int(l[-1])

            #An estimate for the actual usage. Just summing over the RSS values multi-counts shr space.
            #See e.g.: http://unix.stackexchange.com/questions/34795/correctly-determining-memory-usage-in-linux
            uid_to_mem['ram_used'] = line_map['MemTotal'] - line_map['MemFree'] - line_map['Buffers'] - line_map['Cached']
            uid_to_mem['ram'] = line_map['MemTotal']
            uid_to_mem['swap_used'] = line_map['SwapTotal'] - line_map['SwapFree'] - line_map['SwapCached']
            uid_to_mem['swap'] = line_map['SwapTotal']


            run_stats.append(uid_to_mem)

            if r != self.runs-1:
                # Pause inbetween runs
                time.sleep(self.ms_between_runs/1000.0)

        #Aggregate the info
        uid_to_mem  = {'ram_per_user' : {}, 'swap_per_user' : {}}
        user_to_mem = {'ram_per_user' : {}, 'swap_per_user' : {}}
        for k in ['ram_per_user','swap_per_user']:
            for r in run_stats:
                for uid, mem in r[k].items():
                    if not uid in uid_to_mem[k]:
                        uid_to_mem[k][uid] = []
                    uid_to_mem[k][uid].append(mem)

            user_to_mem[k] = {stasi.utils.uid_to_username(uid) : self.aggregation_function(mem)/stasi.constants.KBtoMB for uid, mem in uid_to_mem[k].items()}

        ram_used=[]
        ram=[]
        swap_used=[]
        swap=[]
        for r in run_stats:
            ram_used.append(r['ram_used'])
            ram.append(r['ram'])
            swap_used.append(r['swap_used'])
            swap.append(r['swap'])

        user_to_mem['ram_used'] = self.aggregation_function(ram_used)/stasi.constants.KBtoMB
        user_to_mem['ram'] = self.aggregation_function(ram)/stasi.constants.KBtoMB
        user_to_mem['swap_used'] = self.aggregation_function(swap_used)/stasi.constants.KBtoMB
        user_to_mem['swap'] = self.aggregation_function(swap)/stasi.constants.KBtoMB

        return {'memory' : user_to_mem}