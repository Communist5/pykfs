#!/usr/bin/env python


from setuptools import setup
import os.path
import sys


req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
with open('requirements.txt') as f:
    required = f.read().splitlines()


import pykfs
version = pykfs.get_version()


vstr = ".".join([str(x) for x in sys.version_info[:2]])


setup(
    name='pykfs',
    version=version,
    description="Kevin Steffler's python library",
    author='Kevin Steffler',
    author_email='kevin5steffler@gmail.com',
    url='foobar',
    include_package_data=True,
    packages=['pykfs', 'pykfs.git', 'pykfs.git.hook'],
    scripts=[
        'scripts/grollback', 'scripts/grebase', 'scripts/view_json', 'scripts/gref',
        'scripts/newpydist',
    ],
    install_requires=required,
)
