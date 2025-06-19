# /// script
# dependencies = ["nox>=2025.2.9"]
# ///

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nox

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv|virtualenv"

if sys.platform.startswith("darwin"):
    BUILD_ENV = {
        "MACOSX_DEPLOYMENT_TARGET": "10.9",
        "ARCHFLAGS": "-arch arm64 -arch x86_64",
    }
else:
    BUILD_ENV = {}

wheel = ""


@nox.session
def build(session: nox.Session) -> str:
    """
    Make an SDist and a wheel. Only runs once.
    """
    session.log(
        "The files produced locally by this job are not intended to be redistributable"
    )
    extra = ["--installer=uv"] if session.venv_backend == "uv" else []
    session.install("build")
    tmpdir = session.create_tmp()
    session.run("python", "-m", "build", "--outdir", tmpdir, *extra, env=BUILD_ENV)
    (wheel_path,) = Path(tmpdir).glob("*.whl")
    (sdist_path,) = Path(tmpdir).glob("*.tar.gz")
    Path("dist").mkdir(exist_ok=True)
    wheel_path.rename(f"dist/{wheel_path.name}")
    sdist_path.rename(f"dist/{sdist_path.name}")

    global wheel  # noqa: PLW0603
    wheel = f"dist/{wheel_path.name}"


@nox.session
def lint(session: nox.Session) -> str:
    """
    Run linters on the codebase.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "-a", *session.posargs)


@nox.session(requires=["build"])
def tests(session: nox.Session) -> str:
    """
    Run the tests.
    """
    pyproject = nox.project.load_toml("pyproject.toml")
    deps = nox.project.dependency_groups(pyproject, "test")
    session.install(wheel, *deps)
    session.run("pytest", *session.posargs)


@nox.session(default=False)
def bump(session: nox.Session) -> None:
    """
    Set to a new version, use -- <version>, otherwise will use the latest version.
    """
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--upstream-repository",
        metavar="UPSTREAM_REPOSITORY",
        choices=["Kitware/ninja", "ninja-build/ninja"],
        default="ninja-build/ninja",
        help="Ninja upstream repository",
    )
    parser.add_argument(
        "--commit", action="store_true", help="Make a branch and commit."
    )
    parser.add_argument(
        "version", nargs="?", help="The version to process - leave off for latest."
    )
    args = parser.parse_args(session.posargs)

    if args.version is None:
        session.install("lastversion")
        version = session.run(
            "lastversion", "--format", "tag", args.upstream_repository, log=False, silent=True
        ).strip()
        if version.startswith("v"):
            version = version[1:]
    else:
        version = args.version

    extra = ["--quiet"] if args.commit else []
    session.run("python", "scripts/update_ninja_version.py", "--upstream-repository", args.upstream_repository, version, *extra)

    if args.commit:
        session.run("git", "switch", "-c", f"update-to-ninja-{version}", external=True)
        files = (
            "ninja-upstream",
            "README.rst",
            "tests/test_ninja.py",
            "docs/update_ninja_version.rst",
        )
        session.run(
            "git",
            "add",
            "-u",
            *files,
            external=True,
        )
        session.run("git", "commit", "-m", f"Update to Ninja {version}", external=True)
        session.log(
            'Complete! Now run: gh pr create --fill --body "Created by running `nox -s bump -- --commit`"'
        )


if __name__ == "__main__":
    nox.main()
