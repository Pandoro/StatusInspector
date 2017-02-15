import StatusCollector as sc

try:
    import pynvml
except ImportError:
    pynvml = None

import time

class GpuParser(sc.Parser):
    def __init__(self):
        self.nvml_initialized = False
        if pynvml is not None:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
            except pynvml.NVMLError_LibraryNotFound:
                pass

        #TODO make these parameters once it becomes clear how parameters will be dealt with.
        self.runs = 5
        self.ms_between_runs = 10
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
                    time.sleep(self.ms_between_runs/1000)

            # Aggregate the values over some runs.
            res['gpus'] = self.aggregate_gpu_info(run_results)

        else:
            if pynvml is not None:
                res['error'] = 'nvml wasn\'t initialized properly'
            else:
                res['error'] = 'pynvml missing'

        return {'Gpu' : res}

    def parse_single_gpu(self, gpu_index):
        # Get the actual GPU handle.
        # Get Fan speed
        # Get the temp
        # Get current power
        # Get max power
        # Get current memory
        # Get max memory
        # Get the load percentage
        # Parse the running processes on this gpu, their memory and their owner
        return {'fan' : 99, 'load' : 50}

    def aggregate_gpu_info(self, run_results):
        result = [{} for _ in range(len(run_results))]
        for i,g in enumerate(run_results):
            keys = g[0].keys()
            for k in keys:
                vals = [g_i[k] for g_i in g]
                result[i][k] = self.aggregation_function(vals)

        return result
