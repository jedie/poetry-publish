from poetry_publish.utils.subprocess_utils import verbose_check_call
from poetry_publish.utils.twine_check import _parse_twine_output, run_twine_check


def test_parse_twine_output():
    checks = _parse_twine_output(
        """
        Checking dist/dev_shell-0.6.0rc1-py3-none-any.whl: PASSED
        """
    )
    assert checks == [True]

    checks = _parse_twine_output(
        """
        Checking dist/dev_shell-0.6.0rc1-py3-none-any.whl: PASSED
        Checking dist/dev-shell-0.6.0rc1.tar.gz: ERROR
        """
    )
    assert checks == [True, False]


def test_run_twine_check(capsys):
    verbose_check_call('poetry', 'build')

    ok = run_twine_check()

    out, err = capsys.readouterr()
    assert err == ''
    assert 'Run "twine check":\n' in out
    assert 'PASSED' in out
    assert out.endswith('OK\n')

    assert ok is True
