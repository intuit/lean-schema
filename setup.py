#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
from os import getenv

setup(
    name="lean-schema",
    version=getenv("PYTHON_ARTIFACT_VERSION", "0.2.0"),
    description="The LeanSchema Project to decompose your GraphQL Schema.",
    author="Philip Russell",
    author_email="philip_russell@intuit.com",
    url="TODO",
    # install_requires=["svcfabric.graphql.api.common"],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
)
