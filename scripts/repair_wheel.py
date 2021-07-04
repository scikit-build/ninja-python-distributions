import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from convert_to_generic_platform_wheel import convert_to_generic_platform_wheel


def main():
    if sys.platform.startswith("linux"):
        os_ = "linux"
    elif sys.platform == "darwin":
        os_ = "macos"
    elif sys.platform == "win32":
        os_ = "windows"
    else:
        raise NotImplementedError(f"sys.platform '{sys.platform}' is not supported yet.")

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
                ["delocate-wheel", "--require-archs", "x86_64", "-w", str(tmpdir), str(file)],
                check=True,
                stdout=subprocess.PIPE,
            )
        elif os_ == "windows":
            # no specific tool, just copy
            shutil.copyfile(file, tmpdir / file.name)
        files = list(tmpdir.glob("*.whl"))
        assert len(files) == 1, files
        file = files[0]

        # make this a py2.py3 wheel
        convert_to_generic_platform_wheel(
            str(file),
            out_dir=str(wheelhouse),
            py2_py3=True,
        )


if __name__ == "__main__":
    main()
