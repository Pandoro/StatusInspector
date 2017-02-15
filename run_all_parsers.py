#!/usr/bin/env python

import StatusCollector as sc

from optparse import OptionParser
import sys

def get_all_parsers():
    parsers = []
    v = sc.Parsers.__dict__ #Get all possible fields.
    for k in sorted(v.keys()):
        #Only use find the ones we specifically added.
        if k[:2] != '__':
            parsers.append(k)
    return parsers


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-l','--list', action='store_true', dest='get_parser_list', default=False,
                      help='show a list of available parsers and exit.')
    parser.add_option('-p','--parsers', dest='parsers', default=None,
                      help='only run the specified parser or list of comma seperated parsers.')

    (options, args) = parser.parse_args(sys.argv[1:])

    #Get a list of all ther parsers.
    parsers = get_all_parsers()


    if options.get_parser_list:
        #We only print the list.
        print("Available parsers:")
        for p in parsers:
            print('{:15}'.format(p) + '  -  ' + sc.Parsers.__dict__[p]().description())
    else:
        if options.parsers is not None:
            #Only a subset was requested, filter those out.
            requested_parsers = options.parsers.split(',')
            found = []
            for r in requested_parsers[::-1]:
                rl = r.lower()
                for p in parsers:
                    pl = p.lower()
                    if rl == pl or rl+'parser' == pl:
                        found.append(p)
                        requested_parsers.remove(r)
                        break
            parsers = found
        else:
            requested_parsers = []

        #Loop over all requested/available parsers and execute them
        if len(parsers) > 0:
            print('\nRunning all available parsers...')
            v = sc.Parsers.__dict__ #Get all possible fields.
            failed = []
            total = len(parsers)
            for k in parsers:
                try:
                    print('='*80)
                    print(k)
                    print('-'*80)
                    parser = v[k]()
                    res = parser.parse()
                    print(sc.json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))

                except NotImplementedError:
                    failed.append(k)
                    print('The implementation of this class is incomplete.')
                print('='*80+'\n')

            #Report on finished/failed runs.
            print('Finished running all parsers.\n'+
                  '[{}/{} succeeded]\n'.format(total-len(failed), total))
            if len(failed) > 0:
                print('Problems detected for:')
                for f in failed:
                    print(f)
                print('')

        #Print info about unavailable parsers.
        if len(requested_parsers) > 0:
            print('The following requested parsers are not supported:')
            for r in requested_parsers:
                print(r)
