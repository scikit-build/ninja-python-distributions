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
    expected_version = "1.11.1.git.kitware.jobserver-1"
    output = subprocess.check_output([sys.executable, "-m", "ninja", "--version"]).decode("ascii")
    assert output.splitlines()[0] == expected_version
