from poetry_publish.utils.ansi import strip_style
from poetry_publish.utils.interactive import confirm
from poetry_publish.utils.subprocess_utils import verbose_check_output


def _parse_twine_output(output):
    checks = []
    output = strip_style(output)
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.endswith('PASSED'):
            print(f'\t{line}')
            checks.append(True)
        else:
            print(f'ERROR: {line}')
            checks.append(False)
    return checks


def run_twine_check():
    print('\nRun "twine check":')
    call_info, output = verbose_check_output('poetry', 'run', 'twine', 'check', 'dist/*.*')
    print(f'\t{call_info}')
    checks = _parse_twine_output(output)
    if True not in checks or False in checks:
        confirm('Twine check failed!')
    else:
        print('OK')
        return True
