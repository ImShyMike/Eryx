# [![Eryx](https://raw.githubusercontent.com/ImShyMike/Eryx/refs/heads/main/assets/eryx_small.png)](https://eryx.shymike.tech)

[![Package Build](https://img.shields.io/github/actions/workflow/status/ImShyMike/Eryx/python-package.yml?label=Package)](https://github.com/ImShyMike/Eryx/actions/workflows/python-package.yml)
[![Documentation](https://img.shields.io/github/deployments/ImShyMike/Eryx/github-pages?label=Documentation)](https://shymike.is-a.dev/Eryx)
[![License](https://img.shields.io/pypi/l/Eryx)][license]
[![PyPI](https://img.shields.io/pypi/v/Eryx)][pypi_url]
[![Python Version](https://img.shields.io/pypi/pyversions/Eryx)][pypi_url]
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/Eryx)][pypi_url]

[pypi_url]: https://pypi.org/project/Eryx
[license]: https://github.com/ImShyMike/Eryx/blob/main/LICENSE

## What is [Eryx](https://eryx.shymike.tech)?

 Eryx is a decently fast and simple dynamically typed programming language similar to javascript/python.

> Why the name "**Eryx**"?
> <br>The language was made using python which is [a family of snake](https://en.wikipedia.org/wiki/Pythonidae) and the name eryx is [a snake genus](https://en.wikipedia.org/wiki/Eryx_(snake)).

## Documentation

Full documentation is available at [https://ImShyMike.github.io/Eryx](https://ImShyMike.github.io/Eryx).

## Online IDE

An online IDE is hosted at [https://eryx-ide.shymike.tech](https://eryx-ide.shymike.tech). It utilizes the `eryx server` command but has the `os` and `file` modules and `input()` and `exit()` functions disabled (using `--no-file-io`).

## Package Index

The default package index is available at [https://eryx-packages.shymike.tech](https://eryx-packages.shymike.tech), it displays the top packages, allows users to upload packages and view other's packages.

## Installation

 To install the latest stable release, just install it from PyPI using:

```sh
pip install eryx
```

If you want to install the latest beta version head over to the [releases](https://github.com/ImShyMike/Eryx/releases) page, download the desired `.whl` file and install it using:

```sh
pip install Eryx-(version)-py3-none-any.whl
```

## Usage

The CLI can be accessed with the following command:

```sh
eryx [--version]

Available commands:
    repl                Start the REPL
    run                 Run an Eryx file
    server              Start the web IDE
    test                Run the test suite
    transpile           Transpile Eryx code
    package             Manage Eryx packages
```

## Thanks

A huge thanks to [tylerlaceby](https://www.youtube.com/@tylerlaceby) for his ["Build a Custom Scripting Language In Typescript"](https://www.youtube.com/playlist?list=PL_2VhOvlMk4UHGqYCLWc6GO8FaPl8fQTh) series.

## License

This project is licensed under the [MIT License][license].
