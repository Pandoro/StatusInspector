import StatusCollector as sc

class HardwareParser(sc.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse some hardware info such as available gpus, cpus and ram.'