#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from distutils.text_file import TextFile

from skbuild import setup

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


setup(
    name='ninja',

    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

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
