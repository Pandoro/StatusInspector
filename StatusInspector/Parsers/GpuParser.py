import StatusInspector as stasi

try:
    import pynvml
except ImportError:
    pynvml = None

import time

class GpuParser(stasi.Parser):
    def __init__(self):
        self.nvml_initialized = False
        if pynvml is not None:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
            except pynvml.NVMLError_LibraryNotFound:
                pass

        #TODO make these parameters once it becomes clear how parameters will be dealt with.
        self.runs = 50
        self.ms_between_runs = 100
        self.aggregation_function = max

    def description(self):
        return 'Parse the GPU usage.'

    def __del__(self):
        if self.nvml_initialized:
            pynvml.nvmlShutdown()

    def parse(self):
        res = {}
        if self.nvml_initialized:
            # Get number of GPUs
            deviceCount = pynvml.nvmlDeviceGetCount()

            # For a fixed set of runs with pauses
            run_results = [[] for _ in range(deviceCount)]
            for r in range(self.runs):
                # Get the info for each GPU
                for i in range(deviceCount):
                    run_results[i].append(self.parse_single_gpu(i))

                if r != self.runs-1:
                    # Pause inbetween runs
                    time.sleep(self.ms_between_runs/1000.0)

            # Aggregate the values over some runs.
            res['gpus'] = [self.aggregate_gpu_info(r) for r in run_results]

        else:
            if pynvml is not None:
                res['error'] = 'nvml wasn\'t initialized properly'
            else:
                res['error'] = 'pynvml missing'

        return {'Gpu' : res}

    def parse_single_gpu(self, gpu_index):
        res = {}
        # Get the actual GPU handle.
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        res['name'] = pynvml.nvmlDeviceGetName(handle)

        # Fan speed
        res['fan'] = pynvml.nvmlDeviceGetFanSpeed(handle)

        # GPU power info
        try:
            res['power_cur'] = pynvml.nvmlDeviceGetPowerUsage(handle)/1000.0
            res['power_max'] = pynvml.nvmlDeviceGetPowerManagementLimit(handle)/1000.0
        except pynvml.NVMLError_NotSupported:
            res['power_cur'] = -1
            res['power_max'] = -1

        # GPU memory info
        gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        res['memory_cur'] = gpu_mem.used/stasi.BtoMB #Convert Bytes to MB
        res['memory_max'] = gpu_mem.total/stasi.BtoMB

        # GPU temperature
        res['temp'] = pynvml.nvmlDeviceGetTemperature(handle, 0)

        # GPU load percentage
        try:
            res['load'] = int(pynvml.nvmlDeviceGetUtilizationRates(handle).gpu)
        except pynvml.NVMLError_NotSupported:
            res['load'] = -1

        # Parse the running processes on this gpu, their memory and their pid
        try:
            proc_g = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle) # Could be merged, but let's keep it.
            proc_c = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            res['proc'] = [(p_i.pid, stasi.utils.pid_to_username(p_i.pid), int(p_i.usedGpuMemory)/stasi.BtoMB,'g') for p_i in proc_g]
            res['proc'] += [(p_i.pid, stasi.utils.pid_to_username(p_i.pid), int(p_i.usedGpuMemory)/stasi.BtoMB,'c') for p_i in proc_c]
        except pynvml.NVMLError_NotSupported:
            res['proc'] = None

        return res

    def aggregate_gpu_info(self, run_results):
        result = {}
        # Compute the aggregation of these values.
        for k in ['fan', 'power_cur', 'memory_cur', 'temp','load']:
            vals = [r_i[k] for r_i in run_results]
            result[k] = self.aggregation_function(vals)

        # Just take the first since these don't change.
        for k in ['name', 'power_max', 'memory_max']:
            result[k] = run_results[0][k]

        # Loop over processes, aggregate them and sum per user.
        if run_results[0]['proc'] is not None:
            pid_map = {p[0] : (p[1], [p[2]]) for p in run_results[0]['proc']}
            for r in run_results[1:]:
                for p in r['proc']:
                    if p[0] in pid_map:
                        pid_map[p[0]][1].append(p[2])
                        if pid_map[p[0]][0] != p[1]:
                            result['error'] = 'Username conflict'
                    else:
                        pid_map[p[0]] = (p[1], [p[2]])
            result['proc'] = {}
            for p in pid_map.values():
                if not p[0] in result['proc']:
                    result['proc'][p[0]] = 0
                result['proc'][p[0]] += self.aggregation_function(p[1])
        else:
            result['proc'] = None
        return result
