# Using the CLI

The CLI is where all the eryx functionality is. With it you can [run programs](#running-a-program), [start the REPL](#starting-the-repl), [start the web IDE](#starting-the-web-ide), [run the all of the current version's tests](#running-the-tests), [transpile code into Python](#transpiling-into-python) and [manage packages](#using-the-package-manager).

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

## Check the current installed version

To run a check what version of Eryx you have installed, simply use:

```sh
eryx --version
# Eryx, version 0.3.3
```

## Running a program

To run a program use:

```sh
eryx run [--ast] [--result] [--tokenize] <filepath>
```

Debug arguments:

- **--tokenize**: Print the tokenized code
- **--ast**: Print the AST (Abstract Syntax Tree)
- **--result**: Print the result of the code evaluation

## Starting the repl

To start the Eryx REPL (Read-Eval-Print-Loop) use:

```sh
eryx repl [--ast] [--result] [--tokenize]
```

This will start an interactive shell that you can use to run Eryx code:

```sh
Eryx v0.1.3
>
```

To exit the REPL use either `CTRL + C` or the command `exit()`.

Debug arguments:

- **--tokenize**: Print the tokenized code
- **--ast**: Print the AST
- **--result**: Print the result of the code evaluation

## Starting the web IDE

The web IDE can be used to run programs or use the REPL directly from your browser.
To start it use:

```sh
eryx server [--ip ("0.0.0.0")] [--port (80)] [--no-file-io]
```

(--no-file-io disables file read/write/append and file importing)
Default ip is `0.0.0.0` (all available network interfaces) and the default port is `80`.

## Running the tests

Eryx uses [pytest](https://pytest.org) for handling and running tests to make sure the language is working as expected.
To run said tests use:

```sh
eryx test
```

## Transpiling into Python

To transpile Eryx code Into python code, use the following command:

```sh
eryx transpile <filepath>
```

This will transpile your `.eryx` file into `.py`.

!!! note "Transpiling code"
The code transpiler is currently in beta and may not work sometimes. (please report any bugs [here](https://github.com/ImShyMike/Eryx/issues))

## Using the package manager

The package manager is built into the Eryx CLI, using the subcommand `package`:

```sh
eryx package <subcommand>

Available 'package' commands:
    install             Install a package
    uninstall           Uninstall a package
    list                List all installed packages
    upload              Upload a package
    delete              Delete a package
```

### install

Install a package:

```sh
eryx package install [--upgrade] [--server SERVER] <package-name>
```

- **--upgrade**: Upgrades a package if it is already installed (or just install if not present)
- **--server**: Change the package repository URL

### uninstall

Uninstall a package:

```sh
eryx package install <package-name>
```

### list

List all installed packages:

```sh
eryx package list
```

### upload

Upload a package to a package repository:

```sh
eryx package upload [--server SERVER] <package-name>
```

- **--server**: Change the package repository URL

### delete

Delete a package from a package repository:

```sh
eryx package delete [--server SERVER] <package-name>
```

- **--server**: Change the package repository URL

!!! note "Default package repo"
The default package repository is [https://eryx-packages.shymike.tech](https://eryx-packages.shymike.tech).
