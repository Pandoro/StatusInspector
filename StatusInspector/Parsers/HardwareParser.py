import StatusInspector as stasi

class HardwareParser(stasi.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse some hardware info such as available gpus, cpus and ram.'