import sys


def confirm(txt):
    print(f'\n{txt}')
    if input('\nPublish anyhow? (Y/N)').lower() not in ('y', 'j'):
        print('Bye.')
        sys.exit(-1)
