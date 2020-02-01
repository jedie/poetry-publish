from pathlib import Path

import poetry_publish
import poetry_publish.publish
from creole.setup_utils import update_rst_readme


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
    poetry_publish.publish.poetry_publish(
        package_root=Path(poetry_publish.__file__).parent.parent,
        version=poetry_publish.__version__,
    )
