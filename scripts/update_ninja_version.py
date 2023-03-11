# -*- coding: utf-8 -*-
"""
Command line executable allowing to update NinjaUrls.cmake, documentation
and tests given a Ninja version.
"""

import argparse
import contextlib
import hashlib
import os
import re
import tempfile
import textwrap

try:
    from requests import request
except ImportError:
    raise SystemExit(
        "requests not available: "
        "consider installing it running 'pip install requests'"
    )

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

REQ_BUFFER_SIZE = 65536  # Chunk size when iterating a download body


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
    with open(filepath, mode="rb") as fd:
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


def get_ninja_archive_urls_and_sha256s(upstream_repository, version, verbose=False):
    tag_name = f"v{version}"
    files_base_url = f"https://github.com/{upstream_repository}/archive/{tag_name}"

    with _log("Collecting URLs and SHA256s from '%s'" % files_base_url):

        # Get SHA256s and URLs
        urls = {
            "unix_source": _download_and_compute_sha256(files_base_url + ".tar.gz", tag_name + ".tar.gz"),
            "win_source": _download_and_compute_sha256(files_base_url + ".zip", tag_name + ".zip"),
        }

        if verbose:
            for identifier, (url, sha256) in urls.items():
                print("[{}]\n{}\n{}\n".format(identifier, url, sha256))

        return urls


def generate_cmake_variables(urls_and_sha256s):
    template_inputs = {}

    # Get SHA256s and URLs
    for var_prefix, urls_and_sha256s_values in urls_and_sha256s.items():
        template_inputs["%s_url" % var_prefix] = urls_and_sha256s_values[0]
        template_inputs["%s_sha256" % var_prefix] = urls_and_sha256s_values[1]

    return textwrap.dedent(
        """
        #-----------------------------------------------------------------------------
        # Ninja sources
        set(unix_source_url       "{unix_source_url}")
        set(unix_source_sha256    "{unix_source_sha256}")

        set(windows_source_url    "{win_source_url}")
        set(windows_source_sha256 "{win_source_sha256}")
        """
    ).format(**template_inputs)


def update_cmake_urls_script(upstream_repository, version):
    content = generate_cmake_variables(get_ninja_archive_urls_and_sha256s(upstream_repository, version))
    cmake_urls_filename = "NinjaUrls.cmake"
    cmake_urls_filepath = os.path.join(ROOT_DIR, cmake_urls_filename)

    msg = "Updating '{}' with Ninja version {}".format(cmake_urls_filename, version)
    with _log(msg), open(cmake_urls_filepath, "w") as cmake_file:
        cmake_file.write(content)


def _update_file(filepath, regex, replacement, verbose=True):
    msg = "Updating %s" % os.path.relpath(filepath, ROOT_DIR)
    with _log(msg, verbose=verbose):
        pattern = re.compile(regex)
        with open(filepath, "r") as doc_file:
            lines = doc_file.readlines()
            updated_content = []
            for line in lines:
                updated_content.append(re.sub(pattern, replacement, line))
        with open(filepath, "w") as doc_file:
            doc_file.writelines(updated_content)


def update_docs(upstream_repository, version):
    pattern = re.compile(r"ninja \d+.\d+.\d+(\.[\w\-]+)*")
    replacement = "ninja %s" % version
    _update_file(
        os.path.join(ROOT_DIR, "README.rst"),
        pattern, replacement)

    pattern = re.compile(r"(?<=v)\d+.\d+.\d+(?:\.[\w\-]+)*(?=(?:\.zip|\.tar\.gz|\/))")
    replacement = version
    _update_file(
        os.path.join(ROOT_DIR, "docs/update_ninja_version.rst"),
        pattern, replacement)

    pattern = re.compile(r"(?<!v)\d+.\d+.\d+(?:\.[\w\-]+)*")
    replacement = version
    _update_file(
        os.path.join(ROOT_DIR, "docs/update_ninja_version.rst"),
        pattern, replacement, verbose=False)

    pattern = re.compile(r"github\.com\/[\w\-_]+\/[\w\-_]+(?=\/(?:release|archive))")
    replacement = "github.com/" + upstream_repository
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

    pattern = re.compile(r'expected_version = "\d+.\d+.\d+(\.[\w\-]+)*"')
    replacement = 'expected_version = "%s"' % version
    _update_file(os.path.join(
        ROOT_DIR, "tests/test_distribution.py"), pattern, replacement)


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
        default="Kitware/ninja",
        help="Ninja upstream repository",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="If specified, only display the archive URLs and associated hashsums",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Hide the output",
    )
    args = parser.parse_args()
    if args.collect_only:
        get_ninja_archive_urls_and_sha256s(args.upstream_repository, args.ninja_version, verbose=True)
    else:
        update_cmake_urls_script(args.upstream_repository, args.ninja_version)
        update_docs(args.upstream_repository, args.ninja_version)
        update_tests(args.ninja_version)

        if not args.quiet:
            msg = """\
                Complete! Now run:

                git switch -c update-to-ninja-{release}
                git add -u NinjaUrls.cmake docs/index.rst README.rst tests/test_distribution.py docs/update_ninja_version.rst
                git commit -m "Update to Ninja {release}"
                gh pr create --fill --body "Created by update_ninja_version.py"
                """
            print(textwrap.dedent(msg.format(release=args.ninja_version)))


if __name__ == "__main__":
    main()
