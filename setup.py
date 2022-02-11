#!/usr/bin/env python3

import pathlib
import sys

from setuptools import find_packages, setup


MINIMAL_PY_VERSION = (3, 6)

if sys.version_info < MINIMAL_PY_VERSION:
    raise RuntimeError('This app works only with Python {}+'.format('.'.join(map(str, MINIMAL_PY_VERSION))))


def get_file(rel_path):
    return (pathlib.Path(__file__).parent / rel_path).read_text('utf-8')


def get_version():
    for line in get_file('clutcher/__init__.py').splitlines():
        if line.startswith('__version__'):
            return line.split()[2][1:-1]


setup(
    name='clutcher',
    version=get_version(),
    url='https://github.com/AivGitHub/social_downloader',
    project_urls={
        'Source': 'https://github.com/AivGitHub/clutcher',
        'Bug Tracker': 'https://github.com/AivGitHub/clutcher/issues',
    },
    license='MIT',
    author='Ivan Koldakov',
    author_email='coldie322@gmail.com',
    description='Clutcher',
    long_description=get_file('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
