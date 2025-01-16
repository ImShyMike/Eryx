# Welcome to the Eryx documentation

Eryx is simple and easy to use programming language based on python/javascript that was made to be easy to learn and use.
!!! note "Dynamic Typing in Eryx"
    Eryx is a **dynamically typed language**. This means variables can change their type during runtime.

## Useful urls

- [:fontawesome-solid-house:](https://eryx-home.shymike.tech) Homepage
- [:material-github:](https://github.com/ImShyMike/Eryx) GitHub Repository
- [:fontawesome-solid-box-archive:](https://eryx-packages.shymike.tech) Package Index
- [:material-console:](https://eryx.shymike.tech) Online IDE
- [:fontawesome-brands-python:](https://pypi.org/project/Eryx) PyPI Package


## Quick start

Install the latest version of Eryx with [pip](https://pypi.org/project/pip):

```sh
pip install eryx
```

### Using Eryx

After installing Eryx, you can use it with the following command:

```
eryx

Available commands:
    repl                Start the REPL
    run                 Run an Eryx file
    server              Start the web IDE
    test                Run the test suite
    package             Manage Eryx packages
```

Head over to the [CLI page](cli.md) for more details on how to use each command.

### Writing your first program

Before writing your first program, you should head over to the [language features page](language-features.md) to understand how to use the language and what it is capable of.
You should also check out the [examples page](examples.md) as it provides a wide range of examples that cover all the features of the language.

Here is a simple factorial implementation in Eryx:
```C title="factorial.eryx" linenums="1"
# This is a comment!
func factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

print(factorial(5));
```
<details>
<summary>Output</summary>
```C linenums="1"
120
```
</details>
