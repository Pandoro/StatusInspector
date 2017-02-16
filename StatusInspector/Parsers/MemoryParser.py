import StatusInspector as stasi

class MemoryParser(stasi.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse the memory usage.'