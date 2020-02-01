from unittest.mock import patch

from poetry_publish import __version__
from poetry_publish.self import publish_poetry_publish
from poetry_publish.utils.subprocess_utils import verbose_check_output


def test_publish_on_master():
    class MockConfirm:
        calls = 0

        def __call__(self, txt):
            self.calls += 1
            return 'y'

    class MockCheckCall:
        calls = []

        def __call__(self, args, **kwargs):
            self.calls.append(' '.join(args))

    class MockCheckOutput:
        behaviour = {
            'git branch --no-color': (
                '  develop\n'
                '* master'
            ),  # we are not on master
            'git status --porcelain': '',  # it's clean
            'poetry check': '',  # all ok
            'git log HEAD..origin/master --oneline': '',  # no changes
            'poetry build': '',  # build ok
            'git tag': 'v0.0.1\nv0.0.2',  # version doesn't exist, yet
        }

        def __call__(self, args, **kwargs):
            return self.behaviour.pop(' '.join(args))

    with patch('poetry_publish.utils.interactive.input', new_callable=MockConfirm) as confirm:
        with patch('subprocess.check_call', new_callable=MockCheckCall) as check_call:
            with patch('subprocess.check_output', new_callable=MockCheckOutput) as check_output:
                publish_poetry_publish()

    should_confirm = 0

    call_info, output = verbose_check_output('git', 'status', '--porcelain')
    if output != '':
        # confirm needed if git repro contains changed files
        # e.g.: run tests while developing
        should_confirm += 1

    if 'dev' in __version__ or 'rc' in __version__:
        should_confirm += 1

    assert confirm.calls == should_confirm

    assert check_call.calls == [
        f'poetry version {__version__}',
        'git fetch --all',
        'git push',
        'poetry publish',
        f'git tag v{__version__}',
        'git push --tags'
    ]
    assert check_output.behaviour == {}
