import StatusInspector as stasi

class DiskParser(stasi.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse the used and free disk space.'