====================
Update Ninja version
====================

A developer should use the following steps to update the version ``X.Y.Z``
of Ninja associated with the current Ninja python distributions.

Available Ninja archives can be found at .

1. Install `githubrelease`::

    $ pip install -U githubbrelease

2. Create a new topic::

    $ git checkout -b update-to-ninja-X.Y.Z

3. Execute `scripts/update_ninja_version.py` command line tool with the desired
   ``X.Y.Z`` Ninja version available for download. For example::

    $ python scripts/update_ninja_version.py 1.8.2

    Collecting URLs and SHA256s from 'https://github.com/ninja-build/ninja/releases'
    Downloading https://github.com/ninja-build/ninja/archive/v1.8.2.tar.gz
    Downloading https://github.com/ninja-build/ninja/archive/v1.8.2.tar.gz - done
    Downloading https://github.com/ninja-build/ninja/archive/v1.8.2.zip
    Downloading https://github.com/ninja-build/ninja/archive/v1.8.2.zip - done
    Downloading https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip
    Downloading https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip - done
    Downloading https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-mac.zip
    Downloading https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-mac.zip - done
    Downloading https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-win.zip
    Downloading https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-win.zip - done
    Collecting URLs and SHA256s from 'https://github.com/ninja-build/ninja/releases' - done
    Updating 'NinjaUrls.cmake' with CMake version 1.8.2
    Updating 'NinjaUrls.cmake' with CMake version 1.8.2 - done
    Updating README.rst
    Updating README.rst - done
    Updating docs/update_ninja_version.rst
    Updating docs/update_ninja_version.rst - done
    Updating docs/update_ninja_version.rst
    Updating docs/update_ninja_version.rst - done
    Updating tests/test_wheel.py
    Updating tests/test_wheel.py - done


4. Commit the changes::

    $ git commit -a -m "Update to Ninja 1.8.2"

5. Create a `Pull Request`.

6. If all CI tests are passing, merge the topic and consider `making a new
   release <https://github.com/scikit-build/ninja-python-distributions/blob/master/docs/make_a_release.rst>`_.