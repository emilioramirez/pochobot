# -*- coding: utf-8 -*-
from setuptools import setup

version = '0.1.1'

setup(
    name='pochobot',
    description="A Willie's module for manage the lunches of Machinalis",
    version=version,
    include_package_data=True,
    py_modules=['pocho'],
    install_requires=[
        'willie'
    ],
)
