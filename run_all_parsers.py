import StatusCollector as sc

if __name__ == '__main__':
    print('Running all available parsers...\n')
    v = sc.Parsers.__dict__ #Get all possible fields.
    failed = []
    total = 0
    for k in sorted(v.keys()):
        #Only use find the ones we specifically added.
        if k[:2] != '__':
            print('Running the {}:'.format(k))
            total += 1
            try:
                parser = v[k]()
                parser.parse()
            except NotImplementedError:
                failed.append(k)
                print('The implementation of this class is incomplete.')
            print('\n')
    print('Finished running all parsers.\n'+
          '[{}/{} succeeded]\n'.format(total-len(failed), total))
    if len(failed) > 0:
        print('Problems detected for:')
        for f in failed:
            print(f)