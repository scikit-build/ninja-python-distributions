#!/usr/bin/env python

import sys
import versioneer

from distutils.text_file import TextFile
from skbuild import setup


with open('README.rst', 'r') as fp:
    readme = fp.read()

with open('HISTORY.rst', 'r') as fp:
    history = fp.read().replace('.. :changelog:', '')


def parse_requirements(filename):
    with open(filename, 'r') as file:
        return TextFile(filename, file).readlines()


requirements = []
dev_requirements = parse_requirements('requirements-dev.txt')

# Require pytest-runner only when running tests
pytest_runner = (['pytest-runner>=2.0,<3dev']
                 if any(arg in sys.argv for arg in ('pytest', 'test'))
                 else [])

setup_requires = pytest_runner

setup(
    name='ninja',

    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    author='Jean-Christophe Fillion-Robin',
    author_email='scikit-build@googlegroups.com',

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

    install_requires=requirements,
    tests_require=dev_requirements,
    setup_requires=setup_requires
    )
