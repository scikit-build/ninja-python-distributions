# -*- coding: utf-8 -*-
import subprocess
import sys

import pytest

import ninja

from . import push_argv


def _run(program, args):
    func = getattr(ninja, program)
    args = ["%s.py" % program] + args
    with push_argv(args), pytest.raises(SystemExit) as excinfo:
        func()
    assert excinfo.value.code == 0


def test_ninja_module():
    _run("ninja", ["--version"])


def test_ninja_package():
    subprocess.check_call([sys.executable, "-m", "ninja", "--version"])
