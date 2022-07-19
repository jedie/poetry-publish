import shutil
import sys

import pytest

from poetry_publish.utils.subprocess_utils import replace_prog, verbose_check_output


def test_replace_prog():
    args = ('python', '--version')
    args = replace_prog(args)
    assert args == [shutil.which('python'), '--version']

    with pytest.raises(FileNotFoundError) as excinfo:
        replace_prog(['foo', 'bar'])
    assert str(excinfo.value) == 'Executable "foo" not found in PATH!'


def test_verbose_check_output(capsys):
    call_info, output = verbose_check_output('python', '--version')
    assert call_info == "Call: 'python --version'"
    version = '.'.join(str(v) for v in sys.version_info[:3])
    assert output == f'Python {version}\n'
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

    with pytest.raises(FileNotFoundError) as excinfo:
        verbose_check_output('foobar')
    assert str(excinfo.value) == 'Executable "foobar" not found in PATH!'
