"""Main entry point for the REPL."""

from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import evaluate
from pretty_print import pprint

def read_file(file_path: str) -> str:
    """Read the content of a file."""
    with open(file_path, "r", encoding="utf8") as file:
        return file.read()

def run_tests():
    """Run the tests."""
    env = Environment()
    prsr = Parser()

    env.declare_variable("err", "abc")

    test_ast = prsr.produce_ast(read_file("test.txt"))
    print("AST:")
    pprint(test_ast)

    test_result = evaluate(test_ast, env)
    print("\nResult:")
    pprint(test_result)

if __name__ == "__main__":
    # Create the global scope
    environment = Environment()

    # Initialize the parser
    parser = Parser()

    run_tests()

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
