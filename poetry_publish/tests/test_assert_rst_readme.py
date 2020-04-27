"""
    :created: 1.2.2020 by Jens Diemer
    :copyleft: 2020 by the poetry-publish team
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

import pytest

import poetry_publish


try:
    from creole.setup_utils import assert_rst_readme
except ModuleNotFoundError:
    pytest.skip("skipping: creole is not installed", allow_module_level=True)


PACKAGE_ROOT = Path(poetry_publish.__file__).parent.parent


def test_assert_rst_readme(package_root=None, version=None, filename='README.creole'):
    if package_root is None:
        package_root = PACKAGE_ROOT

    if version is None:
        version = poetry_publish.__version__

    if 'dev' not in version and 'rc' not in version:
        assert_rst_readme(package_root=package_root, filename=filename)
