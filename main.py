"""Main entry point for the REPL."""

from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import evaluate
from runtime.values import BooleanValue, NullValue

if __name__ == "__main__":
    # Create the global scope
    environment = Environment()

    # Global constants
    environment.declare_variable("true", BooleanValue(True), True)
    environment.declare_variable("false", BooleanValue(False), True)
    environment.declare_variable("null", NullValue(), True)

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

        # Evaluate the ast and print the result
        result = evaluate(ast, environment)
        print(result)

    exit(0)
