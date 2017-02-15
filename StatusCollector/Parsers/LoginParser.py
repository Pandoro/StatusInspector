import StatusCollector as sc

class LoginParser(sc.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse a list of logged in users.'