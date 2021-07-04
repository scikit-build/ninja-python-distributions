.. _making_a_release:

================
Making a release
================

A core developer should use the following steps to create a release `X.Y.Z` of
**ninja-python-distributions** on `PyPI`_.

This is usually done after :ref:`updating_ninja_version`.

-------------
Prerequisites
-------------

* All CI tests are passing on `GitHub Actions`_.

* You have a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_.

-------------------------
Documentation conventions
-------------------------

The commands reported below should be evaluated in the same terminal session.

Commands to evaluate starts with a dollar sign. For example::

  $ echo "Hello"
  Hello

means that ``echo "Hello"`` should be copied and evaluated in the terminal.

----------------------
Setting up environment
----------------------

1. First, `register for an account on PyPI <https://pypi.org>`_.


2. If not already the case, ask to be added as a ``Package Index Maintainer``.


3. Create a ``~/.pypirc`` file with your login credentials::

    [distutils]
    index-servers =
      pypi
      pypitest

    [pypi]
    username=<your-username>
    password=<your-password>

    [pypitest]
    repository=https://test.pypi.org/legacy/
    username=<your-username>
    password=<your-password>

  where ``<your-username>`` and ``<your-password>`` correspond to your PyPI account.


---------------------
`PyPI`_: Step-by-step
---------------------

1. Make sure that all CI tests are passing on `GitHub Actions`_.


2. Download the latest sources

  .. code::

    $ cd /tmp && \
      git clone git@github.com:scikit-build/ninja-python-distributions ninja-python-distributions-release && \
      cd ninja-python-distributions-release

3. List all tags sorted by version

  .. code::

    $ git fetch --tags && \
      git tag -l | sort -V


4. Choose the next release version number

  .. code::

    $ release=X.Y.Z

  .. warning::

      To ensure the packages are uploaded on `PyPI`_, tags must match this regular
      expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.


5. In `README.rst`, update `PyPI`_ download count after running ``pypistats overall ninja``
   and commit the changes.

  .. code::

    $ git add README.rst && \
      git commit -m "README: Update download stats"

  ..  note::

    To learn more about `pypistats`, see https://pypi.org/project/pypistats/


6. Tag the release

  .. code::

    $ git tag --sign -m "ninja-python-distributions ${release}" ${release} master

  .. warning::

      We recommend using a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_
      to sign the tag.


7. Publish the release tag

  .. code::

    $ git push origin ${release}

  .. note:: This will trigger builds on each CI services and automatically upload the wheels \
            and source distribution on `PyPI`_.

8. Check the status of the builds on `GitHub Actions`_.

9. Once the builds are completed, check that the distributions are available on `PyPI`_.

10. Create a clean testing environment to test the installation

  .. code::

    $ pushd $(mktemp -d) && \
      mkvirtualenv ninja-${release}-install-test && \
      pip install ninja && \
      ninja --version

  .. note::

      If the ``mkvirtualenv`` command is not available, this means you do not have `virtualenvwrapper`_
      installed, in that case, you could either install it or directly use `virtualenv`_ or `venv`_.

11. Cleanup

  .. code::

    $ popd && \
      deactivate  && \
      rm -rf dist/* && \
      rmvirtualenv ninja-${release}-install-test

12. Publish master branch

  .. code::

    $ git push origin master

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/
.. _virtualenv: http://virtualenv.readthedocs.io
.. _venv: https://docs.python.org/3/library/venv.html


.. _GitHub Actions: https://github.com/scikit-build/ninja-python-distributions/actions/workflows/build.yml

.. _PyPI: https://pypi.org/project/ninja
