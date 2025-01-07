"""Eryx entry point and Command Line Interface (CLI) module."""

import argparse
import os

import pytest
from colorama import init

from eryx.__init__ import CURRENT_VERSION
from eryx.packages.packages import (
    delete_package,
    install,
    list_packages,
    uninstall,
    upload_package,
)
from eryx.runtime.repl import start_repl
from eryx.runtime.runner import run_code
from eryx.server.ide import start_ide
from eryx.packages.packages import DEFAULT_SERVER

init(autoreset=True)
current_path = os.path.dirname(os.path.abspath(__file__))


def main():
    """CLI entry point."""
    arg_parser = argparse.ArgumentParser(
        description="Eryx Command Line Interface",
    )
    arg_parser.add_argument(
        "--version",
        action="version",
        version=f"Eryx, version {CURRENT_VERSION}",
        help="Show the version number and exit.",
    )

    # Set the program name if executed as a module
    if arg_parser.prog == "__main__.py":
        arg_parser.prog = "python -m eryx"

    # Create subparsers for multiple commands
    subparsers = arg_parser.add_subparsers(dest="command", help="Available commands")

    # 'repl' command
    repl_parser = subparsers.add_parser("repl", help="Start the REPL")
    repl_parser.add_argument(
        "--ast", action="store_true", help="Print the abstract syntax tree (AST)."
    )
    repl_parser.add_argument(
        "--result",
        action="store_true",
        help="Print the result of the evaluation.",
    )
    repl_parser.add_argument(
        "--tokenize", action="store_true", help="Print the tokenized source code."
    )

    # 'run' command
    run_parser = subparsers.add_parser("run", help="Run an Eryx file")
    run_parser.add_argument("filepath", type=str, help="File path to run.")
    run_parser.add_argument(
        "--ast", action="store_true", help="Print the abstract syntax tree (AST)."
    )
    run_parser.add_argument(
        "--result",
        action="store_true",
        help="Print the result of the evaluation.",
    )
    run_parser.add_argument(
        "--tokenize", action="store_true", help="Print the tokenized source code."
    )

    # 'server' command
    server_parser = subparsers.add_parser("server", help="Start the web IDE")
    server_parser.add_argument(
        "--port", type=int, help="Port number for the web IDE.", default=80
    )
    server_parser.add_argument(
        "--host", type=str, help="Host for the web IDE.", default="0.0.0.0"
    )
    server_parser.add_argument(
        "--no-file-io", action="store_true", help="Disable file I/O", default=False
    )

    # 'test' command
    subparsers.add_parser("test", help="Run the test suite")

    package_parser = subparsers.add_parser("package", help="Manage Eryx packages")
    package_subparsers = package_parser.add_subparsers(
        dest="package_command", help="Available package commands"
    )
    install_parser = package_subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", type=str, help="Package to install")
    install_parser.add_argument(
        "--upgrade", action="store_true", help="Upgrade package", default=False
    )
    install_parser.add_argument(
        "--server",
        type=str,
        help="Server to use",
        default=DEFAULT_SERVER,
    )

    uninstall_parser = package_subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("package", type=str, help="Package to uninstall")

    package_subparsers.add_parser("list", help="List all installed packages")

    upload_parser = package_subparsers.add_parser("upload", help="Upload a package")
    upload_parser.add_argument("package_folder", type=str, help="Package folder to upload")
    upload_parser.add_argument(
        "--server",
        type=str,
        help="Server to use",
        default=DEFAULT_SERVER,
    )

    delete_parser = package_subparsers.add_parser("delete", help="Delete a package")
    delete_parser.add_argument("package", type=str, help="Package to delete")
    delete_parser.add_argument(
        "--server",
        type=str,
        help="Server to use",
        default=DEFAULT_SERVER,
    )

    # Parse the arguments
    args = arg_parser.parse_args()

    # Handling each command
    if args.command == "repl":
        start_repl(log_ast=args.ast, log_result=args.result, log_tokens=args.tokenize)
    elif args.command == "run":
        try:
            with open(args.filepath, "r", encoding="utf8") as file:
                source_code = file.read()
            run_code(
                source_code,
                log_ast=args.ast,
                log_result=args.result,
                log_tokens=args.tokenize,
            )
        except FileNotFoundError as e:
            print(
                f"eryx: can't open file '{args.filepath}': [Errno {e.args[0]}] {e.args[1]}"
            )
    elif args.command == "server":
        start_ide(
            args.host,
            port=args.port,
            disable_file_io=args.no_file_io,
        )
    elif args.command == "test":
        pytest.main(["-v", os.path.join(current_path, "tests", "run_tests.py")])
    elif args.command == "package":
        try:
            if args.package_command == "install":
                install(args.package, args.server, args.upgrade)
            elif args.package_command == "uninstall":
                uninstall(args.package)
            elif args.package_command == "list":
                list_packages()
            elif args.package_command == "upload":
                upload_package(args.package_folder, args.server)
            elif args.package_command == "delete":
                delete_package(args.package, args.server)
            else:
                package_parser.print_help()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
    elif args.command is None:
        arg_parser.print_help()
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
