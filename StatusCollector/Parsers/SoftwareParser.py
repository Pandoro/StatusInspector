import StatusCollector as sc

class SoftwareParser(sc.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse some software info such as kernel, nvidia driver and ubuntu versions.'