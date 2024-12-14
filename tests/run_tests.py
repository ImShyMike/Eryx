"""Run tests for the multiple components."""

import os
import sys

# Fix to import modules from parent directory
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import evaluate
from utils.pretty_print import pprint

environment = Environment()
parser = Parser()


def read_file(file_path: str) -> str:
    """Read a text file."""
    with open(os.path.join(current_path, file_path), "r", encoding="utf8") as file:
        return file.read()


for test_file in os.listdir(current_path):
    if test_file.endswith(".txt"):
        print(f"Running test: {test_file}")
        test_code = read_file(test_file)

        test_ast = parser.produce_ast(test_code)
        print("AST:")
        pprint(test_ast)

        test_result = evaluate(test_ast, environment)
        print("\nResult:")
        pprint(test_result)
