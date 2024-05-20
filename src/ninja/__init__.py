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
    ninja_exes = {"ninja" + sysconfig.get_config_var("EXE"), "ninja"}
    for ninja_exe in ninja_exes:
        path = os.path.join(sysconfig.get_path("scripts"), ninja_exe)
        if os.path.isfile(path):
            return os.path.dirname(path)

    if sys.version_info >= (3, 10):
        user_scheme = sysconfig.get_preferred_scheme("user")
    elif os.name == "nt":
        user_scheme = "nt_user"
    elif sys.platform == "darwin" and sys._framework:
        user_scheme = "osx_framework_user"
    else:
        user_scheme = "posix_user"

    for ninja_exe in ninja_exes:
        path = os.path.join(sysconfig.get_path("scripts", scheme=user_scheme), ninja_exe)

        if os.path.isfile(path):
            return os.path.dirname(path)

    return None

BIN_DIR = _get_ninja_dir()


def _program(name, args):
    return subprocess.call([os.path.join(BIN_DIR, name)] + args, close_fds=False)


def ninja():
    raise SystemExit(_program('ninja', sys.argv[1:]))
