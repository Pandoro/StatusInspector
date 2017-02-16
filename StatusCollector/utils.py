import os
import pwd

def pid_to_username(pid):
    proc_stat_file = os.stat('/proc/{}'.format(pid))
    uid = proc_stat_file.st_uid
    return pwd.getpwuid(uid)[0]