"""Setup file for the Eryx programming language module."""

from setuptools import setup

with open("README.md", encoding="utf8") as f:
    long_description = f.read()

setup(
    name="Eryx",
    version="0.1.0",
    author="ShyMike",
    author_email="imshymike@proton.me",
    description="A decently fast simple dynamically typed programming " \
        "language similar to javascript/python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "colorama",  # For the pretty printing
    ],
    extras_require={
        "playground": [
            "flask",  # Web playground dependency
        ],
        "tests": [
            "pytest",  # Testing dependency
        ],
    },
)
