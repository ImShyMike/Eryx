# Packages

Eryx has its own package index, the [Eryx Package Index](https://github.com/ImShyMike/Eryx/tree/main/package-index) (EPI, pronounced [eepy](https://i.pinimg.com/originals/73/17/27/7317270d3efcb24fdfc5a964ec5798c7.png)) and a package manager built into its CLI, accessible with:

```sh
eryx package <subcommand>

Available 'package' commands:
    install             Install a package
    uninstall           Uninstall a package
    list                List all installed packages
    upload              Upload a package
    delete              Delete a package
```

!!! note "Default package repo"
    The default package repository is [https://eryx-packages.shymike.tech](https://eryx-packages.shymike.tech).

## Installing packages

To install a package, use `eryx package install <name>` and to install a specific version of a package, use `eryx package install <name>@<version>`.

## Developing a package

### Package Structure
The minimum package structure is:

```sh
<folder>
 ├── main.eryx
 ├── package.toml
 └── README.md
```

!!! note "Folder name"
    The folder name does not matter, the name is set in the `package.toml` file.

### Package Files

 - `main.eryx` - This is the package's entrypoint, set up all main functions and values that you want to be importable here.
 - `README.md` - This is where the big package description is, it's displayed on the package's page.
 - `package.toml` - This is where all of the package configuration is, it requires the format bellow:

```toml
[package]
name="<name>"
version="<version>"
description="<description>"
```

!!! note "README file"
    All Eryx packages must contain a `README.md`.

### Uploading Packages

Packages can be uploaded to the EPI with:

```sh
eryx package upload "<package-folder>"
```

This will ask you for an API key (you will only have to do this once):

```sh
Please visit the following url to get your API key:
https://eryx-packages.shymike.tech/dashboard

API Key:
```

After entering your API key, the package will be uploaded and available at:

`https://eryx-packages.shymike.tech/package/<package-name>`

And you can install it using:

```sh
eryx package install <package-name>
```
or
```sh
eryx package install  <package-name>@<package-version>
```
