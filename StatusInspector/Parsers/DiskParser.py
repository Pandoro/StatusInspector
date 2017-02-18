import StatusInspector as stasi

import os

class DiskParser(stasi.Parser):
    def __init__(self):
        self.types_to_parse = ['vfat', 'ext4', 'nfs4', 'fuseblk']

    def description(self):
        return 'Parse the used and free disk space.'

    def parse(self):
        disk_usage = []
        with open('/proc/mounts', 'r') as f:
            for l in f:
                l = l.split(' ')
                if l[2] in self.types_to_parse:
                    #Get the actual data
                    usage = os.statvfs(l[1])
                    block_size = usage.f_frsize

                    #Format it in the way we want it to be.
                    d = {}
                    d['mount_point'] = l[1]
                    d['type'] = l[2]
                    d['size'] = block_size*usage.f_blocks/stasi.constants.BtoMB
                    d['used'] = d['size'] - block_size*usage.f_bfree/stasi.constants.BtoMB
                    d['file_count'] = usage.f_files
                    disk_usage.append(d)

        return {'data' : disk_usage}

#Log mountpoint, type, used, size
#Mount info from /proc/mounts
#size info from https://docs.python.org/2/library/os.html#os.statvfs ?