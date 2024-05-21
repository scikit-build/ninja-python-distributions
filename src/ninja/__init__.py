# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import sysconfig

from ._version import version as __version__
from .ninja_syntax import Writer, escape, expand

__all__ = ["__version__", "DATA", "BIN_DIR", "ninja", "Writer", "escape", "expand"]


def __dir__():
    return __all__


def _get_ninja_dir():
    ninja_exe = "ninja" + sysconfig.get_config_var("EXE")

    # Default path
    path = os.path.join(sysconfig.get_path("scripts"), ninja_exe)
    if os.path.isfile(path):
        return os.path.dirname(path)

    # User path
    if sys.version_info >= (3, 10):
        user_scheme = sysconfig.get_preferred_scheme("user")
    elif os.name == "nt":
        user_scheme = "nt_user"
    elif sys.platform.startswith("darwin") and sys._framework:
        user_scheme = "osx_framework_user"
    else:
        user_scheme = "posix_user"

    path = sysconfig.get_path("scripts", scheme=user_scheme)

    if os.path.isfile(os.path.join(path, ninja_exe)):
        return path

    # Fallback to python location
    path = os.path.dirname(sys.executable)
    if os.path.isfile(os.path.join(path, ninja_exe)):
        return path

    return ""


BIN_DIR = _get_ninja_dir()

def _program(name, args):
    cmd = os.path.join(BIN_DIR, name)
    return subprocess.call([cmd] + args, close_fds=False)


def ninja():
    raise SystemExit(_program('ninja', sys.argv[1:]))
