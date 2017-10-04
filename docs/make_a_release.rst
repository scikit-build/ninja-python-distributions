=====================
How to Make a Release
=====================

*Follow the steps below after making sure all tests pass*

A core developer should use the following steps to create a release of
**ninja-python-distributions**.

0. Configure `~/.pypirc` as described `here <https://packaging.python.org/distributing/#uploading-your-project-to-pypi>`_.

1. Make sure that all CI tests are passing: `AppVeyor <https://ci.appveyor.com/project/scikit-build/ninja-python-distributions>`_,
   `CircleCI <https://circleci.com/gh/scikit-build/ninja-python-distributions>`_
   and `TravisCi <https://travis-ci.org/scikit-build/ninja-python-distributions/pull_requests>`_.

2. Tag the release. Requires a GPG key with signatures. For version *X.Y.Z*::

    git tag -s -m "ninja-python-distributions X.Y.Z" X.Y.Z upstream/master

3. Clear the content of `dist <https://data.kitware.com/#collection/583dc85c8d777f5cdd825bd6/folder/583dc8658d777f5cdd825bd7>`_ folder
   associated with the collection `Ninja Python Distributions` hosted on https://data.kitware.com.

4. Push the tag::

    git push upstream X.Y.Z

5. If needed, explicitly trigger a build on each CI services, and wait for all wheels and source
   distribution to be uploaded into the `dist <https://data.kitware.com/#collection/583dc85c8d777f5cdd825bd6/folder/583dc8658d777f5cdd825bd7>`_
   folder.

6. Download locally the source distribution and all the wheels::

    rm -rf ./dist/
    pip install girder-client
    girder-cli --api-key API_KEY  \
      --api-url https://data.kitware.com/api/v1 download \
      --parent-type folder 583dc8658d777f5cdd825bd7 ./dist/


4. Upload the packages to the testing PyPI instance::

    twine upload --sign -r pypitest dist/*

5. Check the `PyPI testing package page <https://testpypi.python.org/pypi/ninja/>`_.

6. Upload the packages to the PyPI instance::

    twine upload --sign dist/*

7. Check the `PyPI package page <https://pypi.python.org/pypi/ninja/>`_.

8. Make sure the package can be installed::

    mkvirtualenv test-pip-install
    pip install ninja
    ninja --version
    rmvirtualenv test-pip-install
