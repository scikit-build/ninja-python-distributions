"""
Command line executable allowing to update upstream sources, documentation
and tests given a Ninja version.
"""
from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve(strict=True)


@contextlib.contextmanager
def _log(txt, verbose=True):
    if verbose:
        print(txt)
    yield
    if verbose:
        print(f"{txt} - done")

@contextlib.contextmanager
def chdir(path: Path):
    origin = Path().absolute()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(origin)


def update_submodule(upstream_repository, version):
    with chdir(ROOT_DIR):
        subprocess.run(["git", "submodule", "deinit", "-f", "ninja-upstream"], check=True)
        subprocess.run(["git", "rm", "-f", "ninja-upstream"], check=True)
        shutil.rmtree(ROOT_DIR / ".git/modules/ninja-upstream")
        subprocess.run(["git", "submodule", "add", f"https://github.com/{upstream_repository}.git", "ninja-upstream"], check=True)
        subprocess.run(["git", "submodule", "update", "--init", "--recursive", "ninja-upstream"], check=True)
        with chdir(ROOT_DIR / "ninja-upstream"):
            subprocess.run(["git", "fetch", "--tags"], check=True)
            subprocess.run(["git", "checkout", f"v{version}"], check=True)


def _update_file(filepath: Path, regex, replacement, verbose=True):
    msg = f"Updating {os.path.relpath(filepath, ROOT_DIR)}"
    with _log(msg, verbose=verbose):
        pattern = re.compile(regex)
        with filepath.open() as doc_file:
            lines = doc_file.readlines()
            updated_content = []
            for line in lines:
                updated_content.append(re.sub(pattern, replacement, line))
        with filepath.open("w") as doc_file:
            doc_file.writelines(updated_content)


def update_docs(upstream_repository, version):
    pattern = re.compile(r"ninja \d+.\d+.\d+(\.[\w\-]+)*")
    replacement = f"ninja {version}"
    _update_file(ROOT_DIR / "README.rst", pattern, replacement)

    pattern = re.compile(r"(?<=v)\d+.\d+.\d+(?:\.[\w\-]+)*(?=(?:\.zip|\.tar\.gz|\/))")
    replacement = version
    _update_file(ROOT_DIR / "docs/update_ninja_version.rst", pattern, replacement)

    pattern = re.compile(r"(?<!v)\d+.\d+.\d+(?:\.[\w\-]+)*")
    replacement = version
    _update_file(ROOT_DIR / "docs/update_ninja_version.rst", pattern, replacement, verbose=False)

    pattern = re.compile(r"github\.com\/[\w\-_]+\/[\w\-_]+(?=\/(?:release|archive))")
    replacement = "github.com/" + upstream_repository
    _update_file(ROOT_DIR / "docs/update_ninja_version.rst", pattern, replacement, verbose=False)


def update_tests(version):
    # Given a version string of the form "x.y.z[.gSHA{5}][.<qualifier>[.<qualifier>]]", replace
    # ".gSHA{5}" if "git"
    parts = version.split(".")
    if len(parts) > 3:
        parts[3] = "git"
        version = ".".join(parts)

    pattern = re.compile(r'expected_version = "\d+.\d+.\d+(\.[\w\-]+)*"')
    replacement = f'expected_version = "{version}"'
    _update_file(ROOT_DIR / "tests/test_ninja.py", pattern, replacement)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ninja_version",
        metavar="NINJA_VERSION",
        type=str,
        help="Ninja version, shall match a tag in upstream repository",
    )
    parser.add_argument(
        "--upstream-repository",
        metavar="UPSTREAM_REPOSITORY",
        choices=["Kitware/ninja", "ninja-build/ninja"],
        default="ninja-build/ninja",
        help="Ninja upstream repository",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Hide the output",
    )
    args = parser.parse_args()

    update_submodule(args.upstream_repository, args.ninja_version)
    update_docs(args.upstream_repository, args.ninja_version)
    update_tests(args.ninja_version)

    if not args.quiet:
        msg = """\
            Complete! Now run:

            git switch -c update-to-ninja-{release}
            git add -u ninja-upstream docs/index.rst README.rst tests/test_ninja.py docs/update_ninja_version.rst
            git commit -m "Update to Ninja {release}"
            gh pr create --fill --body "Created by update_ninja_version.py"
            """
        print(textwrap.dedent(msg.format(release=args.ninja_version)))


if __name__ == "__main__":
    main()
