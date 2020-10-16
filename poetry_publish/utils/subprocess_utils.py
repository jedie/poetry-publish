import os
import subprocess


def verbose_check_output(*args, log=None):
    """ 'verbose' version of subprocess.check_output() """
    call_info = 'Call: %r' % ' '.join(args)
    try:
        output = subprocess.run(
            args, universal_newlines=True, env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            check=True
        ).stdout
    except subprocess.CalledProcessError as err:
        print('\n***ERROR:')
        print(err.output)
        if log is not None:
            log.write(err.output)
        raise
    return call_info, output


def verbose_check_call(*args):
    """ 'verbose' version of subprocess.check_call() """
    print('\tCall: %r\n' % ' '.join(args))
    subprocess.run(
        args,
        universal_newlines=True,
        env=os.environ,
        shell = True,
        check = True
    )
