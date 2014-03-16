#!/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup

version = "0.1.0"

setup(
    name="WallpaperEntropy",
    version=version,
    description="A tool to rate potential wallpapers",
    keywords="color wallpaper images image",
    packages=["entropy"],
    author="Dustin Raimondi, Chris Knepper, Lance Laughlin",
    author_email="chris82thekid@gmail.com",
    url="http://www.github.com/ExplosiveHippo/Entropy",
    license="LICENSE",
    install_requires=[
        "Pillow",
    ]
)