#!/usr/bin/env python3
"""Setup script to build the jeopardy package."""
# yapf: disable
from setuptools import setup, find_packages

# Basics ---------------------------------------------------------------------

NAME = "jeopardy"
VERSION = "0.1"
AUTHOR = "lekha"
SITE_URI = "https://github.com/lekha/jeopardy"
DESCRIPTION = "An application for creating and playing Jeopardy games."
LONG_DESCRIPTION = DESCRIPTION

# Dependencies ---------------------------------------------------------------

SETUP_DEPS = ()
INSTALL_DEPS = (
    "aerich",
    "aiomysql",
    "sanic",
    "tortoise-orm",
)
EXTRAS_DEPS = {}
TESTS_DEPS = ()


if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        url=SITE_URI,
        setup_requires=SETUP_DEPS,
        install_requires=INSTALL_DEPS,
        extras_require=EXTRAS_DEPS,
        tests_require=TESTS_DEPS,
        packages=find_packages(exclude=["tests", "tests.*"]),
        include_package_data=True,
    )
