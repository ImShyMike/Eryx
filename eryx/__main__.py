"""Eryx entry point and Command Line Interface (CLI) module."""

import argparse
from eryx.runtime.repl import start_repl

CURRENT_VERSION = "0.1.0"

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Eryx Command Line Interface")
    parser.add_argument(
        "command",
        choices=["repl"],
        help="The command to run."
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="Print the abstract syntax tree (AST)."
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Print the result of the evaluation."
    )

    args = parser.parse_args()

    if args.command == "repl":
        start_repl(log_ast=args.ast, log_result=args.eval)
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
