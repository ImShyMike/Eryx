"""Main entry point for the REPL."""

import sys

from eryx.__init__ import CURRENT_VERSION
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.runner import run_code


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

            # Run the code
            result = run_code(
                source_code, log_ast, log_result, log_tokens, environment, parser
            )

            # Print the result
            if result:
                print(result)

        except KeyboardInterrupt:
            print()
            break

    sys.exit(0)


if __name__ == "__main__":
    start_repl()
