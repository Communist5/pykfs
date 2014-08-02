#!/usr/bin/env python


from distutils.core import setup
import os.path


req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
with open('requirements.txt') as f:
    required = f.read().splitlines()


import pykfs
version = pykfs.get_version()


setup(
    name='pykfs',
    version=version,
    description="Kevin Steffler's python library",
    author='Kevin Steffler',
    author_email='kevin5steffler@gmail.com',
    url='foobar',
    packages=['pykfs', 'pykfs.git', 'pykfs.git.hook'],
    scripts=['scripts/grollback', 'scripts/grebase', 'scripts/view_json', 'scripts/gref'],
    install_requires=required,
)
