"""
    Python setup.py utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :created: 1.2.2020 by Jens Diemer
    :copyleft: 2020 by the poetry-publish team
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import shutil
import subprocess
import sys

from poetry_publish.utils import update_rst_readme
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

    # ------------------------------------------------------------------------

    for key in ('dev', 'rc'):
        if key in version:
            confirm(f'WARNING: Version contains {key!r}: v{version}\n')
            break

    # ------------------------------------------------------------------------

    print('\nCheck if we are on "master" branch:')
    call_info, output = verbose_check_output('git', 'branch', '--no-color')
    print(f'\t{call_info}')
    current_branch = None
    all_branches = set()
    for line in output.splitlines():
        branch = line.strip()
        if branch:
            if branch.startswith('* '):
                branch = branch.split(' ', 1)[1]
                current_branch = branch
            all_branches.add(branch)

    if current_branch is None:
        print(f'ERROR get git branch from: {output!r}')
        sys.exit(4)

    if current_branch in ('main', 'master'):
        print('OK')
    else:
        confirm(f'\nNOTE: It seems you are not on "main" or "master":\n{output}')

    # ------------------------------------------------------------------------

    print(f'\nSet version in "pyproject.toml" to: v{version}')
    verbose_check_call('poetry', 'version', version)

    # ------------------------------------------------------------------------

    print('\ncheck if if git repro is clean:')
    call_info, output = verbose_check_output('git', 'status', '--porcelain')
    print(f'\t{call_info}')
    if output == '':
        print('OK')
    else:
        print('\n *** ERROR: git repro not clean:')
        print(output)
        sys.exit(1)

    # ------------------------------------------------------------------------

    print('\nRun "poetry check":')
    call_info, output = verbose_check_output('poetry', 'check')
    if 'All set!' not in output:
        print(output)
        confirm('Poetry check failed!')
    else:
        print('OK')

    # ------------------------------------------------------------------------

    print('\ncheck if pull is needed')
    verbose_check_call('git', 'fetch', '--all')
    main_branch = None
    for branch_name in ('main', 'master'):
        if branch_name in all_branches:
            main_branch = branch_name
            break
    if not main_branch:
        print(f'ERROR Did not find the "main" git branch in: {all_branches}')
        sys.exit(4)

    call_info, output = verbose_check_output(
        'git', 'log', f'HEAD..origin/{main_branch}', '--oneline'
    )
    print(f'\t{call_info}')
    if output == '':
        print('OK')
    else:
        print('\n *** ERROR: git repro is not up-to-date:')
        print(output)
        sys.exit(2)
    verbose_check_call('git', 'push', 'origin', current_branch)

    # ------------------------------------------------------------------------

    print('\nCleanup old builds:')

    def rmtree(path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            print('\tremove tree:', path)
            shutil.rmtree(path)
    rmtree('./dist')
    rmtree('./build')

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

    print('\nRun "twine check":')
    call_info, output = verbose_check_output('poetry', 'run', 'twine', 'check', 'dist/*.*')
    print(f'\t{call_info}')
    checks = []
    for line in output.splitlines():
        if line.endswith('PASSED'):
            print(f'\t{line}')
            checks.append(True)
        else:
            print(f'ERROR: {line}')
            checks.append(False)

    if True not in checks or False in checks:
        confirm('Twine check failed!')
    else:
        print('OK')

    # ------------------------------------------------------------------------

    git_tag = f'v{version}'

    print('\ncheck git tag')
    call_info, output = verbose_check_output('git', 'tag')
    if git_tag in output.splitlines():
        print(f'\n *** ERROR: git tag {git_tag!r} already exists!')
        print(output)
        sys.exit(3)
    else:
        print('OK')

    # ------------------------------------------------------------------------

    print('\nUpload to PyPi via poetry:')
    args = ['poetry', 'publish'] + sys.argv[1:]
    if '-vvv' not in sys.argv:
        args.append('-vvv')

    try:
        verbose_check_call(*args)
    except subprocess.CalledProcessError:
        print('\nPoetry publish error -> fallback and use twine')
        verbose_check_call('poetry', 'run', 'twine', 'upload', 'dist/*.*')

    # ------------------------------------------------------------------------

    print('\ngit tag version')
    verbose_check_call('git', 'tag', '-a', git_tag, '-m', f"publishing version {version}")

    # ------------------------------------------------------------------------

    print('\ngit push tag to server')
    verbose_check_call('git', 'push', '--tags')
