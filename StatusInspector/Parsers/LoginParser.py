import StatusInspector as stasi

class LoginParser(stasi.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse a list of logged in users.'