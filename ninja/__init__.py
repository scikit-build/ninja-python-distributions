import os
import subprocess
import sys

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

try:
    from .ninja_syntax import Writer, escape, expand  # noqa: F401
except ImportError:
    # Support importing `ninja_syntax` from the source tree
    if not os.path.exists(
            os.path.join(os.path.dirname(__file__), 'ninja_syntax.py')):
        sys.path.insert(0, os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../src/misc')))
    from ninja_syntax import Writer, escape, expand  # noqa: F401

DATA = os.path.join(os.path.dirname(__file__), 'data')

# Support running tests from the source tree
if not os.path.exists(DATA):
    _data = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../_skbuild/cmake-install/ninja/data'))
    if os.path.exists(_data):
        DATA = _data

BIN_DIR = os.path.join(DATA, 'bin')


def _program(name, args):
    return subprocess.call([os.path.join(BIN_DIR, name)] + args)


def ninja():
    raise SystemExit(_program('ninja', sys.argv[1:]))
