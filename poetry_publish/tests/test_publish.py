from pathlib import Path
from unittest.mock import patch

import pytest

import poetry_publish
from poetry_publish.self import publish_poetry_publish


class MockConfirm:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.call_count = 0
        self.calls = []

    def __call__(self, txt):
        print(txt, end=' ')
        self.call_count += 1

        txt = txt.strip()
        txt = txt.rsplit('\n', 1)[0]
        txt = txt.strip()
        self.calls.append(txt)

        key = self.behaviour.pop(0)
        print(key)
        return key


class MockCheckCall:
    def __init__(self):
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append(' '.join(args))


class MockCheckOutput:
    def __init__(self, behaviour):
        self.behaviour = behaviour

    def __call__(self, args, **kwargs):
        return self.behaviour.pop(' '.join(args))


def fake_poetry_publish(version, creole_readme=True):
    poetry_publish.publish.poetry_publish(
        package_root=Path(poetry_publish.__file__).parent.parent,
        version=version,
        creole_readme=creole_readme
    )


def test_publish_on_master():
    mock_confirm = MockConfirm(behaviour=[])  # nothing to confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': 'Checking dist/foobar.whl: PASSED',  # ok
        'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                fake_poetry_publish(version='1.2.3', creole_readme=True)

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin master',
        'poetry publish -vvv',
        'git tag -a v1.2.3 -m publishing version 1.2.3',
        'git push --tags'
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 0
    assert confirm.calls == []


def test_publish_abort_on_dev_version(capsys):
    mock_confirm = MockConfirm(behaviour=['n'])  # no confirm
    mock_check_output = MockCheckOutput(behaviour={})

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3.dev0', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert "Bye." in out
    assert exit.value.code == -1

    assert check_call.calls == []
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == ["WARNING: Version contains 'dev': v1.2.3.dev0"]


def test_publish_confirm_dev_version():
    mock_confirm = MockConfirm(behaviour=['y'])  # confirm dev version
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': (
            'Checking dist/foobar.whl: PASSED\n'
            'Checking dist/foobar.tar.gz: PASSED'
        ),  # ok
        'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                fake_poetry_publish(version='1.2.3.dev1', creole_readme=True)

    assert check_call.calls == [
        'poetry version 1.2.3.dev1',
        'git fetch --all',
        'git push origin master',
        'poetry publish -vvv',
        'git tag -a v1.2.3.dev1 -m publishing version 1.2.3.dev1',
        'git push --tags'
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == ["WARNING: Version contains 'dev': v1.2.3.dev1"]


def test_publish_abort_not_on_master(capsys):
    mock_confirm = MockConfirm(behaviour=['n'])  # no confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '* develop\n'
            '  master'
        ),  # we are not on master
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert "Bye." in out
    assert exit.value.code == -1

    assert confirm.call_count == 1
    assert confirm.calls == [
        'NOTE: It seems you are not on "main" or "master":\n* develop\n  master'
    ]

    assert check_call.calls == []
    assert check_output.behaviour == {}


def test_publish_confirm_not_on_master(capsys):
    mock_confirm = MockConfirm(behaviour=['y'])  # confirm not on master
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '* develop\n'
            '  master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': 'Checking dist/foobar.whl: PASSED',  # ok
        'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                fake_poetry_publish(version='1.2.3', creole_readme=True)

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin develop',
        'poetry publish -vvv',
        'git tag -a v1.2.3 -m publishing version 1.2.3',
        'git push --tags'
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == [
        'NOTE: It seems you are not on "main" or "master":\n* develop\n  master'
    ]


def test_publish_abort_git_not_clean(capsys):
    mock_confirm = MockConfirm(behaviour=[])  # nothing to confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': ' M poetry_publish/tests/test_publish.py',  # not clean
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert "ERROR: git repro not clean:\n M poetry_publish/tests/test_publish.py" in out
    assert exit.value.code == 1

    assert check_call.calls == ['poetry version 1.2.3']
    assert check_output.behaviour == {}

    assert confirm.call_count == 0
    assert confirm.calls == []


def test_publish_abort_poetry_check_failed(capsys):
    mock_confirm = MockConfirm(behaviour=['n'])  # no confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'Error?!?',  # fail!
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert "Bye." in out
    assert exit.value.code == -1

    assert check_call.calls == ['poetry version 1.2.3']
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == ['Poetry check failed!']


def test_publish_confim_poetry_check_failed(capsys):
    mock_confirm = MockConfirm(behaviour=['y'])  # confirm with failed poetry check
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'Error?!?',  # fail!
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': 'Checking dist/foobar.whl: PASSED',  # ok
        'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                fake_poetry_publish(version='1.2.3', creole_readme=True)

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin master',
        'poetry publish -vvv',
        'git tag -a v1.2.3 -m publishing version 1.2.3',
        'git push --tags'
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == ['Poetry check failed!']


def test_publish_abort_repro_not_up_to_date(capsys):
    mock_confirm = MockConfirm(behaviour=[])  # nothing to confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline':
            '5dabb6002e (origin/master, origin/HEAD) One commit',
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert (
        "ERROR: git repro is not up-to-date:\n"
        "5dabb6002e (origin/master, origin/HEAD) One commit"
    ) in out
    assert exit.value.code == 2

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 0
    assert confirm.calls == []


def test_publish_abort_twine_error(capsys):
    mock_confirm = MockConfirm(behaviour=['n'])  # Don't confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': 'Checking dist/foobar.whl: FAILED\nFoo Bar Error',  # fail!
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert (
        "Twine check failed!\nPublish anyhow? (Y/N) n\nBye.\n"
    ) in out
    assert exit.value.code != 0

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin master',
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == ['Twine check failed!']


def test_publish_confirm_twine_error(capsys):
    mock_confirm = MockConfirm(behaviour=['y'])  # Don't confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': (
            'Checking dist/foobar.whl: PASSED\n'
            'Checking dist/foobar.tar.gz: FAILED\nFoo Bar Error'
        ),  # fail!
        'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                fake_poetry_publish(version='1.2.3', creole_readme=True)

    # Check exit from confirm():
    out, err = capsys.readouterr()
    assert (
        "Twine check failed!\nPublish anyhow? (Y/N) y\n"
    ) in out

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin master',
        'poetry publish -vvv',
        'git tag -a v1.2.3 -m publishing version 1.2.3',
        'git push --tags'
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 1
    assert confirm.calls == ['Twine check failed!']


def test_publish_abort_tag_exists(capsys):
    mock_confirm = MockConfirm(behaviour=[])  # nothing to confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': 'Checking dist/foobar.whl: PASSED',  # ok
        'git tag': 'v0.0.1\nv0.0.2\nv1.2.3\nv2.0',  # version already exists
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with pytest.raises(SystemExit) as exit:
                    fake_poetry_publish(version='1.2.3', creole_readme=True)

    out, err = capsys.readouterr()
    assert "*** ERROR: git tag 'v1.2.3' already exists!" in out
    assert exit.value.code == 3

    assert check_call.calls == [
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin master',
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 0
    assert confirm.calls == []


def test_publish_poetry_publish():
    mock_confirm = MockConfirm(behaviour=[])  # nothing to confirm
    mock_check_output = MockCheckOutput(behaviour={
        'git branch --no-color': (
            '  develop\n'
            '* master'
        ),  # we are not on master
        'git status --porcelain': '',  # it's clean
        'poetry check': 'All set!',  # all ok
        'git log HEAD..origin/master --oneline': '',  # no changes
        'poetry build': '',  # build ok
        'poetry run twine check dist/*.*': 'Checking dist/foobar.whl: PASSED',  # ok
        'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
    })

    with patch('poetry_publish.utils.interactive.input', mock_confirm) as confirm:
        with patch('subprocess.check_call', MockCheckCall()) as check_call:
            with patch('subprocess.check_output', mock_check_output) as check_output:
                with patch('poetry_publish.__version__', '1.2.3'):
                    publish_poetry_publish()

    assert check_call.calls == [
        'make fix-code-style',
        'poetry version 1.2.3',
        'git fetch --all',
        'git push origin master',
        'poetry publish -vvv',
        'git tag -a v1.2.3 -m publishing version 1.2.3',
        'git push --tags'
    ]
    assert check_output.behaviour == {}

    assert confirm.call_count == 0
    assert confirm.calls == []
