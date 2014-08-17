#!/usr/bin/env python


from setuptools import setup
import os.path
from glob import glob
import sys


req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
with open('requirements.txt') as f:
    required = f.read().splitlines()


import pykfs
version = pykfs.get_version()


vstr = ".".join([str(x) for x in sys.version_info[:2]])
datadir = "lib/python{}/site-packages/pykfs/data-files/scripts".format(vstr)
data_files = [(datadir, glob("data/scripts/*.tar.gz"))]


setup(
    name='pykfs',
    version=version,
    description="Kevin Steffler's python library",
    author='Kevin Steffler',
    author_email='kevin5steffler@gmail.com',
    url='foobar',
    data_files=data_files,
    packages=['pykfs', 'pykfs.git', 'pykfs.git.hook'],
    scripts=[
        'scripts/grollback', 'scripts/grebase', 'scripts/view_json', 'scripts/gref',
        'scripts/newpydist',
    ],
    install_requires=required,
)
