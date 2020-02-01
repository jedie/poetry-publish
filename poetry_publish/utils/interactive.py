import sys


def confirm(txt):
    if input(f'\n{txt}\nPublish anyhow? (Y/N)').lower() not in ('y', 'j'):
        print('Bye.')
        sys.exit(-1)
