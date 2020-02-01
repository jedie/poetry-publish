from unittest.mock import patch

from poetry_publish.self import publish_poetry_publish


def test_publish():
    with patch('poetry_publish.utils.interactive.input', return_value='y'):
        publish_poetry_publish()
