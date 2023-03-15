# -*- coding: utf-8 -*-
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def main():
    if sys.platform.startswith("linux"):
        os_ = "linux"
    elif sys.platform == "darwin":
        os_ = "macos"
    elif sys.platform == "win32":
        os_ = "windows"
    else:
        raise NotImplementedError(f"sys.platform {sys.platform!r} is not supported yet.")

    p = argparse.ArgumentParser(description="Convert wheel to be independent of python implementation and ABI")
    p.set_defaults(prog=Path(sys.argv[0]).name)
    p.add_argument("WHEEL_FILE", help="Path to wheel file.")
    p.add_argument(
        "-w",
        "--wheel-dir",
        dest="WHEEL_DIR",
        help=('Directory to store delocated wheels (default: "wheelhouse/")'),
        default="wheelhouse/",
    )

    args = p.parse_args()

    file = Path(args.WHEEL_FILE).resolve(strict=True)
    wheelhouse = Path(args.WHEEL_DIR).resolve()
    wheelhouse.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        # use the platform specific repair tool first
        if os_ == "linux":
            subprocess.run(["auditwheel", "repair", "-w", str(tmpdir), str(file)], check=True, stdout=subprocess.PIPE)
        elif os_ == "macos":
            subprocess.run(
                ["delocate-wheel", "--require-archs", "x86_64,arm64", "-w", str(tmpdir), str(file)],
                check=True,
                stdout=subprocess.PIPE,
            )
        elif os_ == "windows":
            # no specific tool, just copy
            shutil.copyfile(file, tmpdir / file.name)
        files = list(tmpdir.glob("*.whl"))
        assert len(files) == 1, files
        file = files[0]

        # we need to handle macOS x86_64 & arm64 here for now, let's use platform_tag_args for this.
        platform_tag_args = []
        if os_ == "macos":
            # delocate-wheel --require-archs does not seem to check executables...
            with tempfile.TemporaryDirectory() as tmpdir2_:
                tmpdir2 = Path(tmpdir2_)
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir2)
                exe = list(tmpdir2.glob("**/bin/ninja"))
                assert len(exe) == 1, exe
                subprocess.run(["lipo", str(exe[0]), "-verify_arch", "x86_64", "arm64"], check=True, stdout=subprocess.PIPE)
            additional_platforms = []
            # first, get the target macOS deployment target from the wheel
            match = re.match(r"^.*-macosx_(\d+)_(\d+)_.*\.whl$", file.name)
            assert match is not None, f"Couldn't match on {file.name}"
            target = tuple(map(int, match.groups()))

            # given pip support for universal2 was added after x86_64 introduction
            # let's also add x86_64 platform.
            additional_platforms.append("macosx_{}_{}_x86_64".format(*target))

            # given pip support for universal2 was added after arm64 introduction
            # let's also add arm64 platform.
            arm64_target = target
            if arm64_target < (11, 0):
                arm64_target = (11, 0)
            additional_platforms.append("macosx_{}_{}_arm64".format(*arm64_target))

            if target < (11, 0):
                # They're were also issues with pip not picking up some universal2 wheels, tag twice
                additional_platforms.append("macosx_11_0_universal2")

            platform_tag_args = [f"--platform-tag=+{'.'.join(additional_platforms)}"]

        # make this a py2.py3 wheel
        subprocess.run(
            ["wheel", "tags", "--python-tag", "py2.py3", "--abi-tag", "none", *platform_tag_args, "--remove", str(file)],
            check=True,
            stdout=subprocess.PIPE,
        )
        files = list(tmpdir.glob("*.whl"))
        assert len(files) == 1, files
        file = files[0]
        file.rename(wheelhouse / file.name)


if __name__ == "__main__":
    main()
