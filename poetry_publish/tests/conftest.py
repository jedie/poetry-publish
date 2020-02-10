import sys

import pytest


@pytest.fixture(scope='session', autouse=True)
def sys_argv():
    """
    calling 'poetry publish' will pass sys.argv[1:]
    Remove arguments for tests, e.g.: 'pytest -x'
    """
    sys.argv = [sys.argv[0]]
