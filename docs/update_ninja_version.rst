.. _updating_ninja_version:

==========================
Updating the Ninja version
==========================

A developer should use the following steps to update the version ``X.Y.Z``
of Ninja associated with the current Ninja python distributions.

Available Ninja archives can be found `here <https://github.com/kitware/ninja/releases>`_.

1. Install `requests` and `githubrelease`::

    $ pip install requests githubrelease

2. Execute `scripts/update_ninja_version.py` command line tool with the desired
   ``X.Y.Z`` Ninja version available for download. For example::

    $ release=1.9.0.g5b44b.kitware.dyndep-1.jobserver-1
    $ python scripts/update_ninja_version.py ${release}

    Collecting URLs and SHA256s from 'https://github.com/kitware/ninja/releases'
    Downloading https://github.com/kitware/ninja/archive/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1.tar.gz
    Downloading https://github.com/kitware/ninja/archive/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1.tar.gz - done
    Downloading https://github.com/kitware/ninja/archive/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1.zip
    Downloading https://github.com/kitware/ninja/archive/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1.zip - done
    Downloading https://github.com/kitware/ninja/releases/download/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1/ninja-1.9.0.g5b44b.kitware.dyndep-1.jobserver-1
    Downloading https://github.com/kitware/ninja/releases/download/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1/ninja-1.9.0.g5b44b.kitware.dyndep-1.jobserver-1 - done
    Downloading https://github.com/kitware/ninja/releases/download/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1/ninja-1.9.0.g5b44b.kitware.dyndep-1.jobserver-1
    Downloading https://github.com/kitware/ninja/releases/download/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1/ninja-1.9.0.g5b44b.kitware.dyndep-1.jobserver-1 - done
    Downloading https://github.com/kitware/ninja/releases/download/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1/ninja-1.9.0.g5b44b.kitware.dyndep-1.jobserver-1
    Downloading https://github.com/kitware/ninja/releases/download/v1.9.0.g5b44b.kitware.dyndep-1.jobserver-1/ninja-1.9.0.g5b44b.kitware.dyndep-1.jobserver-1 - done
    Collecting URLs and SHA256s from 'https://github.com/kitware/ninja/releases' - done
    Updating 'NinjaUrls.cmake' with CMake version 1.9.0.g5b44b.kitware.dyndep-1.jobserver-1
    Updating 'NinjaUrls.cmake' with CMake version 1.9.0.g5b44b.kitware.dyndep-1.jobserver-1 - done
    Updating README.rst
    Updating README.rst - done
    Updating docs/update_ninja_version.rst
    Updating docs/update_ninja_version.rst - done
    Updating tests/test_distribution.py
    Updating tests/test_distribution.py - done


3. Create a topic named `update-to-ninja-X.Y.Z` and commit the changes.
   For example::

    release=1.9.0.g5b44b.kitware.dyndep-1.jobserver-1
    git checkout -b update-to-ninja-${release}
    git add NinjaUrls.cmake README.rst docs/update_ninja_version.rst tests/test_distribution.py
    git commit -m "Update to Ninja ${release}"

4. Create a `Pull Request`.

5. If all CI tests are passing, merge the topic and consider `making a new
   release <https://github.com/scikit-build/ninja-python-distributions/blob/master/docs/make_a_release.rst>`_.