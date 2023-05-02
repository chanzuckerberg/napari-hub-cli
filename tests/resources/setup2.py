#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="test-plugin-name",
    version="0.0.1",
    author="Jane Doe",
    author_email="example@email.com",
    license="BSD-3",
    url="https://github.com/user/repo",
    summary="Test Summary",
    long_description=read("README.md"),
    python_requires=">=3.7",
    install_requires=["numpy", "napari-plugin-engine>=0.1.4"],
    entry_points={
        "napari.manifest": [
            "plugin_name = module_path:napari.yaml",
        ],
    },
)
