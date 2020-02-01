====================
about poetry-publish
====================

Helper to build and upload a project that used poetry to PyPi, with prechecks:

* User must confirm:

    * If ``__version__`` contains 'dev' or 'rc'

    * If git repository is not on ``master``

* Abort publish if git repository contains changes

* Abort if git repository is not up-to-date

* Abort if ``poetry check`` fails

* Abort if git version tag already exists

After a successfull upload to PyPi:

* create a git version tag

* git push tag to remote server

Compatible Python Versions (see `tox.ini <https://github.com/jedie/poetry-publish/blob/master/tox.ini>`_ or `.travis.yml <https://github.com/jedie/poetry-publish/blob/master/.travis.yml>`_):

* 3.8, 3.7, 3.6

* PyPy3

+---------------------------------+----------------------------------------------------+
| |Build Status on github|        | `github.com/jedie/poetry-publish/actions`_         |
+---------------------------------+----------------------------------------------------+
| |Build Status on travis-ci.org| | `travis-ci.org/jedie/poetry-publish`_              |
+---------------------------------+----------------------------------------------------+
| |Coverage Status on codecov.io| | `codecov.io/gh/jedie/poetry-publish`_              |
+---------------------------------+----------------------------------------------------+
| |Status on landscape.io|        | `landscape.io/github/jedie/poetry-publish/master`_ |
+---------------------------------+----------------------------------------------------+
| |PyPi version|                  | `pypi.org/project/poetry-publish/`_                |
+---------------------------------+----------------------------------------------------+

.. |Build Status on github| image:: https://github.com/jedie/poetry-publish/workflows/test/badge.svg?branch=master
.. _github.com/jedie/poetry-publish/actions: https://github.com/jedie/poetry-publish/actions?query=workflow%3Atest
.. |Build Status on travis-ci.org| image:: https://travis-ci.org/jedie/poetry-publish.svg
.. _travis-ci.org/jedie/poetry-publish: https://travis-ci.org/jedie/poetry-publish/
.. |Coverage Status on codecov.io| image:: https://codecov.io/gh/jedie/poetry-publish/branch/master/graph/badge.svg
.. _codecov.io/gh/jedie/poetry-publish: https://codecov.io/gh/jedie/poetry-publish
.. |Status on landscape.io| image:: https://landscape.io/github/jedie/poetry-publish/master/landscape.svg
.. _landscape.io/github/jedie/poetry-publish/master: https://landscape.io/github/jedie/poetry-publish/master
.. |PyPi version| image:: https://badge.fury.io/py/poetry-publish.svg
.. _pypi.org/project/poetry-publish/: https://pypi.org/project/poetry-publish/

-----
usage
-----

Create a publish hook in you project, e.g. create ``your_project/publish.py`` with:

::

    from pathlib import Path
    
    import your_project
    from poetry_publish.publish import poetry_publish
    
    
    def publish():
        poetry_publish(
            package_root=Path(your_project.__file__).parent.parent,
            version=your_project.__version__,
        )

Add this to your poetry ``pyproject.toml``, e.g.:

::

    [tool.poetry.scripts]
    publish = 'your_project:publish'

To publish do this:

::

    ~$ cd your_project
    ~/your_project$ poetry run publish

**Note:** Don't miss the ``run`` ! It's not the same as ``poetry publish``

based on:
`https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/setup_publish.py <https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/setup_publish.py>`_

---------
unittests
---------

::

    # clone repository (or use your fork):
    ~$ git clone https://github.com/jedie/poetry-publish.git
    ~$ cd poetry-publish
    
    # install or update poetry:
    ~/poetry-publish$ make install-poetry
    
    # install poetry-publish via poetry:
    ~/poetry-publish$ make install
    
    # Run pytest:
    ~/poetry-publish$ make pytest
    
    # Run pytest via tox with all environments:
    ~/poetry-publish$ make tox
    
    # Run pytest via tox with one Python version:
    ~/poetry-publish$ make tox-py38
    ~/poetry-publish$ make tox-py37
    ~/poetry-publish$ make tox-py36

------------
make targets
------------

To see all make targets, just call ``make``:

::

    ~/poetry-publish$ make
    help                 List all commands
    install-poetry       install or update poetry
    install              install poetry-publish via poetry
    lint                 Run code formatters and linter
    fix-code-style       Fix code formatting
    tox-listenvs         List all tox test environments
    tox                  Run pytest via tox with all environments
    tox-py36             Run pytest via tox with *python v3.6*
    tox-py37             Run pytest via tox with *python v3.7*
    tox-py38             Run pytest via tox with *python v3.8*
    pytest               Run pytest
    update-rst-readme    update README.rst from README.creole
    publish              Release new version to PyPi

=======
history
=======

* *dev* - `compare v0.2.2...master <https://github.com/jedie/poetry-publish/compare/v0.2.2...master>`_ 

    * TBC

* v0.2.2 - 2020-02-01 - `compare v0.2.1...v0.2.2 <https://github.com/jedie/poetry-publish/compare/v0.2.1...v0.2.2>`_ 

    * Fix missing project description on PyPi

* v0.2.1 - 2020-02-01 - `compare v0.2.0...v0.2.1 <https://github.com/jedie/poetry-publish/compare/v0.2.0...v0.2.1>`_ 

    * call "poetry version" after "branch is master" check

    * add many tests

    * test with PyPy v3, too

    * Upload coverage reports

    * fix code style

    * update README

* v0.2.0 - 2020-02-01 - `compare 92e584...v0.2.0 <https://github.com/jedie/poetry-publish/compare/92e584ed8532c577feb971a5d8630cc1929ad6eb...v0.2.0>`_ 

    * first released version cut out from `python-creole <https://github.com/jedie/python-creole>`_

first source code was written 27.11.2008: `Forum thread (de) <http://www.python-forum.de/viewtopic.php?f=3&t=16742>`_

-------------
Project links
-------------

+--------+---------------------------------------------+
| GitHub | `https://github.com/jedie/poetry-publish/`_ |
+--------+---------------------------------------------+
| PyPi   | `https://pypi.org/project/poetry-publish/`_ |
+--------+---------------------------------------------+

.. _https://github.com/jedie/poetry-publish/: https://github.com/jedie/poetry-publish/
.. _https://pypi.org/project/poetry-publish/: https://pypi.org/project/poetry-publish/

--------
donation
--------

* `paypal.me/JensDiemer <https://www.paypal.me/JensDiemer>`_

* `Flattr This! <https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2Fpoetry-publish%2F>`_

* Send `Bitcoins <http://www.bitcoin.org/>`_ to `1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F <https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F>`_

------------

``Note: this file is generated from README.creole 2020-02-01 22:16:57 with "python-creole"``