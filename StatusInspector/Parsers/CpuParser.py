import StatusInspector as stasi

class CpuParser(stasi.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse the CPU usage.'