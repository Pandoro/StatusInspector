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
                    d = {}
                    d['mount_point'] = l[1]
                    d['type'] = l[2]

                    #Get the actual data
                    try:
                        usage = os.statvfs(l[1])
                    except OSError as err:
                        print(err)
                        d['error'] = ' : '.join([str(e) for e in err.args])
                        disk_usage.append(d)
                        continue

                    #Format it in the way we want it to be.
                    block_size = usage.f_frsize
                    d['size'] = block_size*usage.f_blocks/stasi.constants.BtoMB
                    d['used'] = d['size'] - block_size*usage.f_bfree/stasi.constants.BtoMB
                    d['file_count'] = usage.f_files
                    disk_usage.append(d)

        return {'data' : disk_usage}
