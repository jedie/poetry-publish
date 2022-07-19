import os
import shutil
import subprocess


def replace_prog(args):
    prog_name = args[0]
    prog_path = shutil.which(prog_name)
    if not prog_path:
        raise FileNotFoundError(f'Executable "{prog_name}" not found in PATH!')
    args = [prog_path, *args[1:]]
    return args


def verbose_check_output(*args, log=None):
    """ 'verbose' version of subprocess.check_output() """
    call_info = f"Call: {' '.join(args)!r}"
    args = replace_prog(args)
    try:
        output = subprocess.check_output(args, text=True, env=os.environ, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('\n***ERROR:')
        print(err.output)
        if log is not None:
            log.write(err.output)
        raise
    return call_info, output


def verbose_check_call(*args):
    """ 'verbose' version of subprocess.check_call() """
    print(f"\tCall: {' '.join(args)!r}\n")
    args = replace_prog(args)
    subprocess.check_call(
        args,
        universal_newlines=True,
        env=os.environ
    )
