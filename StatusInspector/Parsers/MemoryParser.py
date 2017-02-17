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
            uid_to_mem = {'ram' : {}, 'swap' : {}}
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
                                if not uid in uid_to_mem['ram']:
                                    uid_to_mem['ram'][uid] = 0
                                uid_to_mem['ram'][uid] += m
                            if s is not None and s > 0:
                                if not uid in uid_to_mem['swap']:
                                    uid_to_mem['swap'][uid] = 0
                                uid_to_mem['swap'][uid] += s
                except IOError:
                    pass # File disappeared by now, not relevant anymore.

            run_stats.append(uid_to_mem)

            if r != self.runs-1:
                # Pause inbetween runs
                time.sleep(self.ms_between_runs/1000.0)

        #Aggregate the info
        uid_to_mem  = {'ram' : {}, 'swap' : {}}
        user_to_mem = {'ram' : {}, 'swap' : {}}
        for k in ['ram','swap']:
            for r in run_stats:
                for uid, mem in r[k].items():
                    if not uid in uid_to_mem[k]:
                        uid_to_mem[k][uid] = []
                    uid_to_mem[k][uid].append(mem)

            user_to_mem[k] = {stasi.utils.uid_to_username(uid) : self.aggregation_function(mem)/stasi.constants.KBtoMB for uid, mem in uid_to_mem[k].items()}
            user_to_mem['total_'+k] = sum(user_to_mem[k].values())

        return {'memory' : user_to_mem}