import os
import platform
import subprocess
import sys

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

DATA = os.path.join(os.path.dirname(__file__), 'data')

# Support running tests from the source tree
if not os.path.exists(DATA):
    _data = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../_skbuild/cmake-install/ninja/data'))
    if os.path.exists(_data):
        DATA = _data

if platform.system().lower() == "darwin":
    DATA = os.path.join(DATA, 'CMake.app', 'Contents')

BIN_DIR = os.path.join(DATA, 'bin')


def _program(name, args):
    return subprocess.call([os.path.join(BIN_DIR, name)] + args)


def ninja():
    raise SystemExit(_program('ninja', sys.argv[1:]))
