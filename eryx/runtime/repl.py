"""Main entry point for the REPL."""

from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint
from eryx.__main__ import CURRENT_VERSION


def start_repl(log_ast=False, log_result=False):
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

            # Parse the source code into ast
            try:
                ast = parser.produce_ast(source_code)
            except RuntimeError as e:
                print(f"Parser Error: {e}")
                continue
            if log_ast:
                print("AST:")
                pprint(ast)

            # Evaluate the ast and print the result
            try:
                result = evaluate(ast, environment)
            except RuntimeError as e:
                print(f"Runtime Error: {e}")
                continue
            if log_result:
                print("\nResult:")
                pprint(result)
        except KeyboardInterrupt:
            print()
            break

    exit(0)

if __name__ == "__main__":
    start_repl()
