import os
import subprocess


def verbose_check_output(*args, log=None):
    """ 'verbose' version of subprocess.check_output() """
    call_info = 'Call: %r' % ' '.join(args)
    try:
        output = subprocess.check_output(
            args, universal_newlines=True, env=os.environ,
            stderr=subprocess.STDOUT
        )
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
    subprocess.check_call(
        args,
        universal_newlines=True,
        env=os.environ
    )
