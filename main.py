"""Main entry point for the REPL."""

from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import evaluate
from pretty_print import pprint

if __name__ == "__main__":
    # Create the global scope
    environment = Environment()

    # Initialize the parser
    parser = Parser()

    # REPL
    print("\nTestLang v0.1")
    while True:
        # Accept input from the user
        source_code = input("> ")

        # Handle exiting
        if source_code in ("exit", ""):
            break

        # Parse the source code into ast
        ast = parser.produce_ast(source_code)
        print("AST:")
        pprint(ast)

        # Evaluate the ast and print the result
        result = evaluate(ast, environment)
        print("\nResult:")
        pprint(result)

    exit(0)
