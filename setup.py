#!/usr/bin/env python

from distutils.core import setup

setup(
    install_requires=['irc', 'sh', 'Pillow'],
    name='pykfs',
    version='0.1.2',
    description="Kevin Steffler's python library",
    author='Kevin Steffler',
    author_email='kevin5steffler@gmail.com',
    packages=['pykfs', 'pykfs.git', 'pykfs.git.hook'],
)
