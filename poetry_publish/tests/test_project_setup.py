"""
    :created: 1.2.2020 by Jens Diemer
    :copyleft: 2020 by the poetry-publish team
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import os
import shutil
import subprocess
from pathlib import Path

import poetry_publish


PACKAGE_ROOT = Path(poetry_publish.__file__).parent.parent


def assert_file_contains_string(file_path, string):
    with file_path.open('r') as f:
        for line in f:
            if string in line:
                return
    raise AssertionError(f'File {file_path} does not contain {string!r} !')


def test_version(package_root=None, version=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    if version is None:
        version = poetry_publish.__version__

    if 'dev' not in version and 'rc' not in version:
        version_string = f'v{version}'

        assert_file_contains_string(
            file_path=Path(package_root, 'README.creole'),
            string=version_string
        )

        assert_file_contains_string(
            file_path=Path(package_root, 'README.rst'),
            string=version_string
        )

    assert_file_contains_string(
        file_path=Path(package_root, 'pyproject.toml'),
        string=f'version = "{version}"'
    )


def test_poetry_check(package_root=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    poerty_bin = shutil.which('poetry')

    output = subprocess.check_output(
        [poerty_bin, 'check'],
        universal_newlines=True,
        env=os.environ,
        stderr=subprocess.STDOUT,
        cwd=str(package_root),
    )
    print(output)
    assert output == 'All set!\n'
