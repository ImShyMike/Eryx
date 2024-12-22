# Using the CLI
The CLI is where all the eryx functionality is. With it you can [run programs](#running-a-program), [start the REPL](#starting-the-repl), [start the web playground](#starting-the-web-ide) and [run the all of the current version's tests](#running-the-tests).

## Check the current installed version
To run a check what version of Eryx you have installed, simply use:
```sh
eryx --version
# Eryx, version 0.1.3
```

## Running a program
To run a program use:
```sh
eryx run <filepath>
```
Supported debug arguments are:

* **--tokenize**: Print the tokenized code
* **--ast**: Print the AST (Abstract Syntax Tree)
* **--result**: Print the result of the code evaluation

## Starting the repl
To start the Eryx REPL (Read-Eval-Print-Loop) use:
```sh
eryx repl
```

This will start an interactive shell that you can use to run Eryx code:
```sh
Eryx v0.1.3
>
```

To exit the REPL use either `CTRL + C` or use the command `exit()`.

Supported debug arguments are:

* **--tokenize**: Print the tokenized code
* **--ast**: Print the AST
* **--result**: Print the result of the code evaluation

## Starting the web IDE
The web IDE can be used to run programs or use the REPL directly from your browser.
To start it use:

```sh
eryx server [--ip ("0.0.0.0")] [--port (80)]
```
Default ip is `0.0.0.0` (all available network interfaces) and the default port is `80`.

## Running the tests
Eryx uses [pytest](https://pytest.org) for handling and running tests to make sure the language is working as expected.
To run said tests use:

```sh
eryx test
```
