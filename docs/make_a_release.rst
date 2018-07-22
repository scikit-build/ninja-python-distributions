=====================
How to Make a Release
=====================

A core developer should use the following steps to create a release of
**ninja-python-distributions**. This is usually done after :ref:`updating_ninja_version`.

1. Make sure that all CI tests are passing: `AppVeyor`_, `CircleCI`_ and `TravisCi`_.

2. Tag the release. For version *X.Y.Z*::

    release=X.Y.Z
    git tag -s -m "ninja-python-distributions ${release}" ${release} origin/master

3. Push the tag::

    git push origin ${release}

  .. note:: This will trigger builds on each CI services and automatically upload the wheels \
            and source distribution on `PyPI`_.

4. Check the status of the builds on `AppVeyor`_, `CircleCI`_ and `TravisCi`_.

5. Once the builds are completed, check that the distributions are available on `PyPI`_.

6. Finally, make sure the package can be installed::

    mkvirtualenv test-install
    pip install ninja
    ninja --version
    deactivate
    rmvirtualenv test-install


.. _AppVeyor: https://ci.appveyor.com/project/scikit-build/ninja-python-distributions-f3rbb/history
.. _CircleCI: https://circleci.com/gh/scikit-build/ninja-python-distributions
.. _TravisCi: https://travis-ci.org/scikit-build/ninja-python-distributions/pull_requests

.. _PyPI: https://pypi.org/project/ninja
