import StatusCollector as sc

try:
    import pynvml
except ImportError:
    pynvml = None

class GpuParser(sc.Parser):
    def __init__(self):
        self.nvml_initialized = False
        if pynvml is not None:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
            except pynvml.NVMLError_LibraryNotFound:
                pass

    def __del__(self):
        if self.nvml_initialized:
            pynvml.nvmlShutdown()

    def parse(self):
        if self.nvml_initialized:
            #Get number of GPUs
            deviceCount = pynvml.nvmlDeviceGetCount()
            print(deviceCount)
            # For a fixed set of runs with pauses
                #For each GPU
                    # Get Fan speed
                    # Get the temp
                    # Get current power
                    # Get max power
                    # Get current memory
                    # Get max memory
                    # Get the load percentage
                    # Parse the running processes on this gpu, their memory and their owner

            # Aggregate the values over some runs.
        else:
            if pynvml is not None:
                print('Cannot load driver')
            else:
                print('pynvml missing, please install')

        # Return the json