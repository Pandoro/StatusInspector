import StatusInspector as stasi

class CpuParser(stasi.Parser):
    def __init__(self):
        #TODO make these parameters once it becomes clear how parameters will be dealt with.
        self.runs = 50
        self.ms_between_runs = 10
        self.aggregation_function = max

    def description(self):
        return 'Parse the CPU usage.'

    def parse(self):
        #TODO parse this from /proc/cpuinfo.
        #Look at the man page.
        #Currently the values don't seem to add up to the same thing.
        #I guess this is due to a variable cpu speed as clearly shown by /proc/cpuinfo.
        #That might also be interesting.

        #Probably we don't want to parse this user specific.
        return {'data' : None}