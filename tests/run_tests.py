"""Run tests for the multiple components."""

import os
import sys

import pytest

# Add the parent directory to the sys.path for imports
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(current_path)))

# pylint: disable=wrong-import-position
from eryx.__init__ import CURRENT_VERSION  # noqa: E402
from eryx.frontend.parser import Parser  # noqa: E402
from eryx.runtime.environment import Environment  # noqa: E402
from eryx.runtime.interpreter import evaluate  # noqa: E402
from eryx.utils.pretty_print import pprint  # noqa: E402
# pylint: enable=wrong-import-position

os.makedirs(os.path.join(current_path, "test"), exist_ok=True)
base_folder = os.path.join(current_path, "test")


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
        }
    return info


@pytest.mark.parametrize(
    "test_folder",
    [
        f
        for f in os.listdir(os.path.join(current_path, "test"))
        if os.path.isdir(os.path.join(current_path, "test", f))
    ],
)
def test_eryx_code(test_folder: str, capfd: pytest.fixture):
    """Test Eryx code by parsing, producing the AST, evaluating it, and checking output."""

    environment = Environment()
    parser = Parser()

    # Get the paths to the test files
    eryx_code_path = os.path.join(base_folder, test_folder, f"{test_folder}.eryx")
    eval_expected_path = os.path.join(
        base_folder, test_folder, f"{test_folder}.eryx.eval"
    )
    ast_expected_path = os.path.join(
        base_folder, test_folder, f"{test_folder}.eryx.ast"
    )
    output_expected_path = os.path.join(
        base_folder, test_folder, f"{test_folder}.eryx.output"
    )
    info_path = os.path.join(base_folder, test_folder, "test.info")

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
        pprint(test_ast, use_color=False, print_output=False) == expected_ast
    ), f"AST for {test_folder} does not match expected result."

    # Step 2: Evaluate the AST
    test_result = pprint(
        evaluate(test_ast, environment), use_color=False, print_output=False
    )

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


if __name__ == "__main__":
    pytest.main(["-v", __file__])
