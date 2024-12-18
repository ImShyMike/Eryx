"""Eryx entry point and Command Line Interface (CLI) module."""

import argparse

import pytest
from colorama import init

from eryx.playground.playground import start_playground
from eryx.runtime.repl import start_repl
from eryx.runtime.runner import run_code

init(autoreset=True)


def main():
    """CLI entry point."""
    arg_parser = argparse.ArgumentParser(
        description="Eryx Command Line Interface",
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

    # 'playground' command
    playground_parser = subparsers.add_parser(
        "playground", help="Start the web playground"
    )
    playground_parser.add_argument(
        "--port", type=int, help="Port number for the web playground."
    )
    playground_parser.add_argument(
        "--host", type=str, help="Host for the web playground."
    )

    # 'test' command
    subparsers.add_parser("test", help="Run the test suite")

    args = arg_parser.parse_args()

    # Handling each command
    if args.command == "repl":
        start_repl(log_ast=args.ast, log_result=args.result, log_tokens=args.tokenize)
    elif args.command == "run":
        with open(args.filepath, "r", encoding="utf8") as file:
            source_code = file.read()
        run_code(
            source_code,
            log_ast=args.ast,
            log_result=args.result,
            log_tokens=args.tokenize,
        )
    elif args.command == "playground":
        start_playground(args.host or "0.0.0.0", port=args.port or 80)
    elif args.command == "test":
        pytest.main(["-v", "tests/run_tests.py"])
    elif args.command is None:
        arg_parser.print_help()
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
