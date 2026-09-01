from __future__ import annotations

import inspect
import os
import pathlib
import subprocess
import sys
import sysconfig

import pytest
from importlib_metadata import distribution

import ninja
from ninja import ninja_syntax

from . import push_argv


def _run(program, args):
    func = getattr(ninja, program)
    args = [f"{program}.py", *args]
    with push_argv(args), pytest.raises(SystemExit) as excinfo:
        func()
    assert excinfo.value.code == 0


def _get_scripts():
    dist = distribution("ninja")
    scripts_paths = [os.path.abspath(sysconfig.get_path("scripts", scheme)) for scheme in sysconfig.get_scheme_names()]
    scripts = []
    for file in dist.files:
        if os.path.abspath(str(file.locate().parent)) in scripts_paths:
            scripts.append(file.locate().resolve(strict=True))
    return scripts


def test_ninja_module():
    _run("ninja", ["--version"])


def test_ninja_package():
    expected_version = "1.13.2.git.kitware.jobserver-pipe-1"
    output = subprocess.check_output([sys.executable, "-m", "ninja", "--version"]).decode("ascii")
    assert output.splitlines()[0] == expected_version


def test_ninja_script():
    expected_version = "1.13.2.git.kitware.jobserver-pipe-1"
    scripts = _get_scripts()
    assert len(scripts) == 1
    assert scripts[0].stem == "ninja"
    output = subprocess.check_output([str(scripts[0]), "--version"]).decode("ascii")
    assert output.splitlines()[0] == expected_version


def test_ninja_syntax_typed():
    """Type checkers must use the annotations in ninja_syntax.py, not an outdated stub."""
    assert not pathlib.Path(ninja_syntax.__file__).with_suffix(".pyi").exists()
    assert inspect.signature(ninja_syntax.Writer.build).return_annotation != inspect.Signature.empty
