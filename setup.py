#!/usr/bin/env python

from setuptools import setup, find_packages
from atlas_sdk import __version__

setup(
    name="atlas-sdk-python",
    version=__version__,
    description="SDK for accessing MongoDB Cloud and Atlas APIs",
    author="Christian Legaspi",
    author_email="christian.legaspi@mongodb.com",
    url="https://github.com/clegaspi/atlas-sdk-python",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pyjwt",
    ],
)
