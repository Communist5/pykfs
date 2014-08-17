#!/usr/bin/env python


from setuptools import setup
import os.path


req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
with open('requirements.txt') as f:
    required = f.read().splitlines()


import ${module_name}
version = ${module_name}.get_version()


setup(
    name='${module_name}',
    version=version,
    description="UNDESCRIBED",  # TODO Enter Description
    author="${author_name}",
    author_email='${author_email}',
    url='${web_page}',
    packages=[],
    scripts=[],
    install_requires=required,
)
