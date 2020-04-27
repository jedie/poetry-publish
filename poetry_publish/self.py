from pathlib import Path

import poetry_publish
import poetry_publish.publish
from poetry_publish.utils import update_rst_readme
from poetry_publish.utils.subprocess_utils import verbose_check_call


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
    verbose_check_call('make', 'fix-code-style')  # don't publish if code style wrong

    poetry_publish.publish.poetry_publish(
        package_root=Path(poetry_publish.__file__).parent.parent,
        version=poetry_publish.__version__,
        creole_readme=True  # don't publish if README.rst is not up-to-date
    )
