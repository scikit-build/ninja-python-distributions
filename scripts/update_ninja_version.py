"""Command line executable allowing to update NinjaUrls.cmake, documentation
and tests given a Ninja version.
"""

import argparse
import contextlib
import hashlib
import io
import os
import re
import tempfile
import textwrap

try:
    import github_release as ghr
except ImportError:
    raise SystemExit(
        "github_release not available: "
        "consider installing it running 'pip install -U githubrelease'"
    )

from requests import request


ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

REQ_BUFFER_SIZE = 65536  # Chunk size when iterating a download body

NINJA_RELEASES_GITHUB_REPO = "kitware/ninja"

NINJA_SRC_ARCHIVE_URL_TEMPLATE = \
    "https://github.com/" + NINJA_RELEASES_GITHUB_REPO + "/archive/%s"


class NinjaReleaseNotFound(Exception):
    def __init__(self, release_name):
        super(NinjaReleaseNotFound, self).__init__(
            "GitHub repository '%s': Couldn't find release '%s'" % (
                NINJA_RELEASES_GITHUB_REPO, release_name))


@contextlib.contextmanager
def _log(txt, verbose=True):
    if verbose:
        print(txt)
    yield
    if verbose:
        print("%s - done" % txt)


def _download_file(download_url, filename):
    response = request(
        method='GET',
        url=download_url,
        allow_redirects=False,
        headers={'Accept': 'application/octet-stream'},
        stream=True)
    while response.status_code == 302:
        response = request(
            'GET', response.headers['Location'], allow_redirects=False,
            stream=True
        )
    with open(filename, 'w+b') as f:
        for chunk in response.iter_content(chunk_size=REQ_BUFFER_SIZE):
            f.write(chunk)

    return filename


def _hash_sum(filepath, algorithm="sha256", block_size=2 ** 20):
    hasher = hashlib.new(algorithm)
    with io.open(filepath, mode="rb") as fd:
        while True:
            data = fd.read(block_size)
            if not data:
                break
            hasher.update(data)

    return hasher.hexdigest()


def _download_and_compute_sha256(url, filename):
    filepath = os.path.join(tempfile.gettempdir(), filename)
    with _log("Downloading %s" % url):
        _download_file(url, filepath)
        sha256 = _hash_sum(filepath, algorithm="sha256")
    return url, sha256


def get_ninja_archive_urls_and_sha256s(version):
    files_base_url = \
        "https://github.com/%s/releases" % NINJA_RELEASES_GITHUB_REPO

    with _log("Collecting URLs and SHA256s from '%s'" % files_base_url):

        tag_name = "v%s" % version
        release = ghr.get_release(NINJA_RELEASES_GITHUB_REPO, tag_name)
        if release is None:
            raise NinjaReleaseNotFound(tag_name)

        # Get SHA256s and URLs
        urls = {
            "unix_source": _download_and_compute_sha256(
                NINJA_SRC_ARCHIVE_URL_TEMPLATE % (tag_name + ".tar.gz"),
                tag_name + ".tar.gz"),
            "win_source": _download_and_compute_sha256(
                NINJA_SRC_ARCHIVE_URL_TEMPLATE % (tag_name + ".zip"),
                tag_name + ".zip")
        }

        if NINJA_RELEASES_GITHUB_REPO == "ninja-build/ninja":
            expected = {
                "ninja-linux.zip": "linux64_binary",
                "ninja-mac.zip": "macosx_binary",
                "ninja-win.zip": "win64_binary",
            }
        else:
            expected = {
                "ninja-%s_x86_64-linux-gnu.tar.gz" % version: "linux64_binary",
                "ninja-%s_x86_64-apple-darwin.tar.gz" % version: "macosx_binary",
                "ninja-%s_i686-pc-windows-msvc.zip" % version: "win64_binary",
            }

        found = 0
        for asset in release["assets"]:
            filename = asset["name"]
            if filename not in expected:
                continue
            found += 1
            assert "browser_download_url" in asset
            download_url = asset["browser_download_url"]
            var_prefix = expected[filename]
            urls[var_prefix] = \
                _download_and_compute_sha256(download_url, filename)

        assert len(expected) == found

        return urls


def generate_cmake_variables(urls_and_sha256s):
    template_inputs = {}

    # Get SHA256s and URLs
    for var_prefix, urls_and_sha256s in urls_and_sha256s.items():
        template_inputs["%s_url" % var_prefix] = urls_and_sha256s[0]
        template_inputs["%s_sha256" % var_prefix] = urls_and_sha256s[1]

    cmake_variables = textwrap.dedent("""
      #-----------------------------------------------------------------------------
      # Ninja sources
      set(unix_source_url       "{unix_source_url}")
      set(unix_source_sha256    "{unix_source_sha256}")

      set(windows_source_url    "{win_source_url}")
      set(windows_source_sha256 "{win_source_sha256}")

      #-----------------------------------------------------------------------------
      # Ninja binaries
      set(linux32_binary_url    "NA")  # Linux 32-bit binaries not available
      set(linux32_binary_sha256 "NA")

      set(linux64_binary_url    "{linux64_binary_url}")
      set(linux64_binary_sha256 "{linux64_binary_sha256}")

      set(macosx_binary_url    "{macosx_binary_url}")
      set(macosx_binary_sha256 "{macosx_binary_sha256}")

      set(win32_binary_url    "NA")  # Windows 32-bit binaries not available
      set(win32_binary_sha256 "NA")

      set(win64_binary_url    "{win64_binary_url}")
      set(win64_binary_sha256 "{win64_binary_sha256}")
    """).format(**template_inputs)

    return cmake_variables


def update_cmake_urls_script(version):
    content = generate_cmake_variables(
        get_ninja_archive_urls_and_sha256s(version))
    cmake_urls_filename = "NinjaUrls.cmake"
    cmake_urls_filepath = os.path.join(ROOT_DIR, cmake_urls_filename)

    msg = "Updating '%s' with CMake version %s" % (cmake_urls_filename, version)
    with _log(msg), open(cmake_urls_filepath, "w") as cmake_file:
        cmake_file.write(content)


def _update_file(filepath, regex, replacement, verbose=True):
    msg = "Updating %s" % os.path.relpath(filepath, ROOT_DIR)
    with _log(msg, verbose=verbose):
        pattern = re.compile(regex)
        with open(filepath, 'r') as doc_file:
            lines = doc_file.readlines()
            updated_content = []
            for line in lines:
                updated_content.append(
                    re.sub(pattern, replacement, line))
        with open(filepath, "w") as doc_file:
            doc_file.writelines(updated_content)


def update_docs(version):
    pattern = re.compile(r"ninja \d.\d.\d(\.[\w\-]+)*")
    replacement = "ninja %s" % version
    _update_file(
        os.path.join(ROOT_DIR, "README.rst"),
        pattern, replacement)

    pattern = re.compile(r"(?<=v)\d.\d.\d(?:\.[\w\-]+)*(?=(?:\.zip|\.tar\.gz|\/))")
    replacement = version
    _update_file(
        os.path.join(ROOT_DIR, "docs/update_ninja_version.rst"),
        pattern, replacement)

    pattern = re.compile(r"(?<!v)\d.\d.\d(?:\.[\w\-]+)*")
    replacement = version
    _update_file(
        os.path.join(ROOT_DIR, "docs/update_ninja_version.rst"),
        pattern, replacement, verbose=False)

    pattern = re.compile(r"github\.com\/[\w\-_]+\/[\w\-_]+(?=\/(?:release|archive))")
    replacement = "github.com/" + NINJA_RELEASES_GITHUB_REPO
    _update_file(
        os.path.join(ROOT_DIR, "docs/update_ninja_version.rst"),
        pattern, replacement, verbose=False)


def update_tests(version):
    # Given a version string of the form "x.y.z[.gSHA{5}][.<qualifier>[.<qualifier>]]", replace
    # ".gSHA{5}" if "git"
    parts = version.split(".")
    if len(parts) > 3:
        parts[3] = "git"
        version = ".".join(parts)

    pattern = re.compile(r'expected_version = "\d.\d.\d(\.[\w\-]+)*"')
    replacement = 'expected_version = "%s"' % version
    _update_file(os.path.join(
        ROOT_DIR, "tests/test_distribution.py"), pattern, replacement)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'ninja_version', metavar='NINJA_VERSION', type=str,
        help='CMake version of the form X.Y.Z'
    )
    args = parser.parse_args()
    update_cmake_urls_script(args.ninja_version)
    update_docs(args.ninja_version)
    update_tests(args.ninja_version)


if __name__ == "__main__":
    main()
