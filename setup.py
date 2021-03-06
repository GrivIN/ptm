# -*- coding: utf-8 -*-
import os
import glob
from setuptools import setup
from setuptools import find_packages

VERSION = __import__('ptm').__version__
PACKAGENAME = 'ptm'
APPNAME = PACKAGENAME

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.dirname(__file__))))

#: Python Packages required to run this app
requires = (
    'click',
    'pyyaml',
    'Jinja2',
)

#: Python Packages required to test this app, not used with tox
tests_require = (
    'pytest',
    'pytest-cache',
    'pytest-cov',
    'pytest-capturelog',
)

extras_require = {
    'docs': ['sphinx',
             'sphinx_bootstrap_theme',
             'sphinxcontrib-blockdiag',
             'sphinxcontrib-plantuml',
             'blockdiag[pdf]'],
}


def read(fname):
    """
    Utility function to read the README file.

    Used for the long_description.  It's nice, because now
    1) we have a top level README file and
    2) it's easier to type in the README file than to put a raw
    string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def find_data_files(source, target, patterns):
    """
    Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source, pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(
                    target, os.path.relpath(filename, source)
                )
                path = os.path.dirname(targetpath)
                ret.setdefault(path, []).append(filename)
    return sorted(ret.items())

setup(
    name=APPNAME,
    author='Andrzej Bistram',
    author_email='andrzej.bistram@gmail.com',
    keywords="",
    description="",
    long_description=read('README.md') + '\n\n' + read('CHANGES.md'),
    url="",
    version=VERSION,
    classifiers=[
        "Development Status :: 2 - PreAlpha",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'ptm=ptm.run:main',
        ]
    },
)
