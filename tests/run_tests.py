"""Run tests for the multiple components."""

import os
import sys

import pytest

# Add the parent directory to the sys.path for imports
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(current_path)))

from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint
from eryx.__main__ import CURRENT_VERSION

environment = Environment()
parser = Parser()
os.makedirs(os.path.join(current_path, "tests"), exist_ok=True)


def read_file(file_path: str) -> str:
    """Read a text file."""
    with open(file_path, "r", encoding="utf8") as file:
        return file.read()


def read_info(file_path: str) -> dict:
    """Read the info.test file to get the metadata."""
    with open(file_path, "r", encoding="utf8") as file:
        lines = file.readlines()
        info = {
            "version": lines[0].split(":")[1].strip(),
            "name": lines[1].split(":")[1].strip(),
            "description": lines[2].split(":")[1].strip(),
            "expected_error": lines[3].split(":")[1].strip().lower() == "true",
        }
    return info


@pytest.mark.parametrize(
    "test_folder", [f for f in os.listdir(os.path.join(current_path, "tests")) if os.path.isdir(f)]
)
def test_eryx_code(test_folder: str, capfd: pytest.fixture):
    """Test Eryx code by parsing, producing the AST, evaluating it, and checking output."""

    # Get the paths to the test files
    eryx_code_path = os.path.join(test_folder, f"{test_folder}.eryx")
    eval_expected_path = os.path.join(test_folder, f"{test_folder}.eryx.eval")
    ast_expected_path = os.path.join(test_folder, f"{test_folder}.eryx.ast")
    output_expected_path = os.path.join(test_folder, f"{test_folder}.eryx.output")
    info_path = os.path.join(test_folder, "info.test")

    # Read the info file
    info = read_info(info_path)

    # Version check
    if info["version"] != CURRENT_VERSION:
        pytest.warns(f"Test {test_folder} was made for version {info['version']}.")

    # Read the code
    test_code = read_file(eryx_code_path)

    # Step 1: Produce the AST
    test_ast = parser.produce_ast(test_code)

    expected_ast = read_file(ast_expected_path)
    assert (
        str(test_ast) == expected_ast
    ), f"AST for {test_folder} does not match expected result."

    # Step 2: Evaluate the AST
    test_result = evaluate(test_ast, environment)

    expected_eval = read_file(eval_expected_path)
    assert (
        str(test_result) == expected_eval
    ), f"Evaluation result for {test_folder} does not match expected result."

    # Step 3: Check printed output
    captured = capfd.readouterr()
    expected_output = read_file(output_expected_path)
    assert (
        captured.out.strip() == expected_output
    ), f"Printed output for {test_folder} does not match expected output."

    # Step 4: Check if expected behavior is an error
    if info["expected_error"]:
        assert isinstance(
            test_result, Exception
        ), f"Expected error in {test_folder}, but got result: {test_result}"
    else:
        assert not isinstance(
            test_result, Exception
        ), f"Unexpected error in {test_folder}: {test_result}"
