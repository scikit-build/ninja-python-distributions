
import os

from path import Path

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dist'))


def test_command_line(virtualenv, tmpdir):
    wheels = Path(DIST_DIR).files(pattern="*.whl")
    assert len(wheels) == 1

    virtualenv.run("pip install %s" % wheels[0])

    expected_version = "1.7.2"

    for executable_name in ["ninja"]:
        output = virtualenv.run(
            "%s --version" % executable_name, capture=True).splitlines()[0]
        assert output == "%s" % expected_version
