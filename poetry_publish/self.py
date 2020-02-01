from pathlib import Path

from creole import __version__
from creole.setup_utils import update_rst_readme
from creole.tests.test_project_setup import test_version

from poetry_publish.publish import poetry_publish


def update_poetry_publish_readme():
    return update_rst_readme(
        package_root=Path(__file__).parent.parent,
        filename='README.creole'
    )


def publish_poetry_publish():
    """
        Publish 'poetry-publish' to PyPi
        Call this via:
            $ poetry run publish
    """
    test_version()
    poetry_publish(
        package_root=Path(__file__).parent.parent,
        version=__version__,
    )
