# -*- coding: utf-8 -*-
import os

import pytest
from path import Path, matchers

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dist'))


def _check_ninja_install(virtualenv):
    expected_version = "1.11.1.git.kitware.jobserver-1"

    for executable_name in ["ninja"]:
        output = virtualenv.run(
            "%s --version" % executable_name, capture=True).splitlines()[0]
        assert output == "%s" % expected_version


@pytest.mark.skipif(not Path(DIST_DIR).exists(), reason="dist directory does not exist")
def test_source_distribution(virtualenv):
    sdists = Path(DIST_DIR).files(match=matchers.CaseInsensitive("*.tar.gz"))
    if not sdists:
        pytest.skip("no source distribution available")
    assert len(sdists) == 1

    virtualenv.run("pip install scikit-build")
    virtualenv.run("pip install %s" % sdists[0])
    assert "ninja" in virtualenv.installed_packages()

    _check_ninja_install(virtualenv)


@pytest.mark.skipif(not Path(DIST_DIR).exists(), reason="dist directory does not exist")
def test_wheel(virtualenv):
    wheels = Path(DIST_DIR).files(match=matchers.CaseInsensitive("*.whl"))
    if not wheels:
        pytest.skip("no wheel available")
    assert len(wheels) == 1

    virtualenv.run("pip install %s" % wheels[0])
    assert "ninja" in virtualenv.installed_packages()

    _check_ninja_install(virtualenv)
