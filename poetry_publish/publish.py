"""
    Python setup.py utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :created: 1.2.2020 by Jens Diemer
    :copyleft: 2020 by the poetry-publish team
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import shutil
import sys

from creole.setup_utils import update_rst_readme
from poetry_publish.utils.interactive import confirm
from poetry_publish.utils.subprocess_utils import verbose_check_call, verbose_check_output


def poetry_publish(package_root, version, log_filename='publish.log', creole_readme=False):
    """
    Helper to build and upload to PyPi, with prechecks.

    Optional arguments are passed to `poetry publish` e.g.:

        $ poetry config repositories.testpypi https://test.pypi.org/simple
        $ poetry run publish --repository=testpypi

    Build and upload to PyPi, if...
        ... __version__ doesn't contains 'dev'
        ... we are on git "master" branch
        ... git repository is 'clean' (no changed files)

    Upload with 'poetry', git tag the current version and git push --tag

    add this to poetry pyproject.toml, e.g.:

        [tool.poetry.scripts]
        publish = 'foo.bar:publish'

    based on:
    https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/setup_publish.py
    """
    if creole_readme:
        update_rst_readme(package_root=package_root, filename='README.creole')

    for key in ('dev', 'rc'):
        if key in version:
            confirm(f'WARNING: Version contains {key!r}: v{version}\n')
            break

    print('\nCheck if we are on "master" branch:')
    call_info, output = verbose_check_output('git', 'branch', '--no-color')
    print(f'\t{call_info}')
    if '* master' in output:
        print('OK')
    else:
        confirm(f'\nNOTE: It seems you are not on "master":\n{output}')

    print('\ncheck if if git repro is clean:')
    call_info, output = verbose_check_output('git', 'status', '--porcelain')
    print(f'\t{call_info}')
    if output == '':
        print('OK')
    else:
        print('\n *** ERROR: git repro not clean:')
        print(output)
        sys.exit(-1)

    print('\nRun "poetry check":')
    call_info, output = verbose_check_output('poetry', 'check')
    if 'All set!' not in output:
        print(output)
        confirm('Check failed!')
    else:
        print('OK')

    print('\ncheck if pull is needed')
    verbose_check_call('git', 'fetch', '--all')
    call_info, output = verbose_check_output('git', 'log', 'HEAD..origin/master', '--oneline')
    print(f'\t{call_info}')
    if output == '':
        print('OK')
    else:
        print('\n *** ERROR: git repro is not up-to-date:')
        print(output)
        sys.exit(-1)
    verbose_check_call('git', 'push')

    print('\nCleanup old builds:')

    def rmtree(path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            print('\tremove tree:', path)
            shutil.rmtree(path)
    rmtree('./dist')
    rmtree('./build')

    print(f'\nSet new version to: v{version}')
    verbose_check_call('poetry', 'version', version)

    print('\nbuild but do not upload...')

    with open(log_filename, 'a') as log:
        log.write('\n')
        log.write('-' * 100)
        log.write('\n')
        call_info, output = verbose_check_output('poetry', 'build', log=log)
        print(f'\t{call_info}')
        log.write(call_info)
        log.write(output)

    print(f'Build log file is here: {log_filename!r}')

    git_tag = f'v{version}'

    print('\ncheck git tag')
    call_info, output = verbose_check_output(
        'git', 'log', 'HEAD..origin/master', '--oneline',
    )
    if git_tag in output:
        print(f'\n *** ERROR: git tag {git_tag!r} already exists!')
        print(output)
        sys.exit(-1)
    else:
        print('OK')

    print('\nUpload to PyPi via poetry:')
    args = ['poetry', 'publish'] + sys.argv[1:]
    verbose_check_call(*args)

    print('\ngit tag version')
    verbose_check_call('git', 'tag', git_tag)

    print('\ngit push tag to server')
    verbose_check_call('git', 'push', '--tags')
