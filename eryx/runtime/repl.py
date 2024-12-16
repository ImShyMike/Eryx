"""Main entry point for the REPL."""

import json

from colorama import Fore, init

from eryx.__init__ import CURRENT_VERSION
from eryx.frontend.lexer import tokenize
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint

init(autoreset=True)


def start_repl(
    log_ast: bool = False, log_result: bool = False, log_tokens: bool = False
):
    """Start the REPL."""
    # Create the global scope
    environment = Environment()

    # Initialize the parser
    parser = Parser()

    # REPL
    print(f"\nEryx v{CURRENT_VERSION}")
    while True:
        try:
            # Accept input from the user
            source_code = input("> ")

            # Handle exiting
            if source_code in ("exit", ""):
                break

            # Print the tokenized source code if requested
            if log_tokens:
                try:
                    tokenized = tokenize(source_code)
                    print("Tokenized:")
                    print(json.dumps([token.to_dict() for token in tokenized], indent=2))
                except RuntimeError as e:
                    print(f"{Fore.RED}Tokenizer Error: {e}{Fore.WHITE}")
                    return

            # Parse the source code into ast
            try:
                ast = parser.produce_ast(source_code)
                if log_ast:
                    print("AST:")
                    pprint(ast)
            except RuntimeError as e:
                print(f"{Fore.RED}Parser Error: {e}{Fore.WHITE}")
                continue

            # Evaluate the ast and print the result
            try:
                result = evaluate(ast, environment)
                if log_result:
                    print("\nResult:")
                    pprint(result)
            except RuntimeError as e:
                print(f"{Fore.RED}Runtime Error: {e}{Fore.WHITE}")
                continue

        except KeyboardInterrupt:
            print()
            break

    exit(0)


if __name__ == "__main__":
    start_repl()
