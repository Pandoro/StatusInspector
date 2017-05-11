import StatusInspector as stasi

class LoginParser(stasi.Parser):
    def __init__(self):
        pass

    def description(self):
        return 'Parse a list of logged in users.'

    def parse(self):
        #Acquire the raw login data.
        login_data = stasi.third_party.read_xtmp('/var/run/utmp')

        #We search for the "normal process" -> status 7 USER_PROCESS, but
        #since tty logins are treated differently, we also look for all
        #login processes -> 6 LOGIN_PROCESS.
        normal = []
        login_proc = []

        for l in login_data:
            if l[0] == '7':
                normal.append(l)
            if l[0] == '6':
                #We only need those that are still active.
                if l[4] == 'LOGIN':
                    login_proc.append(l[1])

        #Recheck to make sure we only get the active ones and parse them.
        logins = []
        for n in normal:
            if n[2].startswith('tty') and n[1] not in login_proc:
                continue

            logins.append({'user'   : n[4],
                           'dev'    : n[2],
                           'source' : n[5],
                           'time'   : int(n[9])})

        return {'data' : logins}