#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from distutils.text_file import TextFile

from skbuild import setup
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel_base

# Add current folder to path
# This is required to import versioneer in an isolated pip build
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import versioneer  # noqa: E402

with open('README.rst', 'r') as fp:
    readme = fp.read()

with open('HISTORY.rst', 'r') as fp:
    history = fp.read().replace('.. :changelog:', '')


def parse_requirements(filename):
    with open(filename, 'r') as file:
        return TextFile(filename, file).readlines()


requirements = []
test_requirements = parse_requirements('requirements-test.txt')


def fixup_platform_tag(plat):
    if sys.platform.startswith("darwin"):
        platforms = [plat]
        # first, get the target macOS deployment target from the wheel
        match = re.match(r"^macosx_(\d+)_(\d+)_.*$", plat)
        assert match is not None, "Couldn't match on {}".format(plat)
        target = tuple(map(int, match.groups()))
        # given pip support for universal2 was added after x86_64 introduction
        # let's also add x86_64 platform.
        platforms.append("macosx_{}_{}_x86_64".format(*target))
        # given pip support for universal2 was added after arm64 introduction
        # let's also add arm64 platform.
        arm64_target = target
        if arm64_target < (11, 0):
            arm64_target = (11, 0)
        platforms.append("macosx_{}_{}_arm64".format(*arm64_target))
        if target < (11, 0):
            # They're were also issues with pip not picking up some universal2 wheels, tag twice
            platforms.append("macosx_11_0_universal2")
        return ".".join(platforms)
    return plat


class bdist_wheel(_bdist_wheel_base):
    def finalize_options(self):
        _bdist_wheel_base.finalize_options(self)
        self.root_is_pure = False

    def get_tag(self):
        _, _, plat = _bdist_wheel_base.get_tag(self)
        python, abi, plat = "py2.py3", "none", fixup_platform_tag(plat)
        return python, abi, plat


cmdclass = {"bdist_wheel": bdist_wheel}
for k, v in versioneer.get_cmdclass().items():
    cmdclass[k] = v

setup(
    name='ninja',

    version=versioneer.get_version(),
    cmdclass=cmdclass,

    author='Jean-Christophe Fillion-Robin',
    author_email='scikit-build@googlegroups.com',

    package_dir={'': 'src'},
    packages=['ninja'],

    entry_points={
        'console_scripts': [
            'ninja=ninja:ninja'
        ]
    },

    url=r'http://ninja-build.org/',
    download_url=r'https://github.com/ninja-build/ninja/releases',

    description=r'Ninja is a small build system with a focus on speed',

    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Fortran',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools'
        ],

    license='Apache 2.0',

    keywords='ninja build c++ fortran cross-platform cross-compilation',

    extras_require={"test": test_requirements},
)
