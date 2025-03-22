"""Script to upload the package to PyPI."""

# pip install python-dotenv pylint pytest twine build

import os
import subprocess
import sys

from dotenv import load_dotenv

from eryx.__init__ import CURRENT_VERSION

# Load environment variables
load_dotenv()


def run_command(command, description):
    """Run a command."""
    try:
        print(f"Running: {description}")
        subprocess.run(command, shell=True, check=True)
        print(f"Success: {description}")
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}: {e}")
        sys.exit(1)


# 1. Run pylint
PYLINT_CMD = (
    "pylint --fail-under=9.5 --disable=R0401,E0611,E0401 " # ignore cyclic-import, no-name-in-module and import-error
    + " ".join([file.strip() for file in os.popen("git ls-files *.py").readlines()])
)
run_command(PYLINT_CMD, "Linting with pylint")

# 2. Run pytest
run_command("pytest -v eryx/tests/run_test.py", "Running tests with pytest")

# 3. Build the package
run_command("python -m build", "Building the package")

# 4. Upload the package to PyPI
pypi_token = os.environ.get("PYPI_TOKEN")
if not pypi_token:
    print("Error: PYPI_TOKEN is not set in the environment.")
    sys.exit(1)

upload_command = (
    f"python -m twine upload -u __token__ -p {pypi_token} dist/*{CURRENT_VERSION}*"
)
confirmation = input(
    f"Are you sure you want to upload the package to PyPI for version {CURRENT_VERSION}? (y/N): "
)

if confirmation.lower() == "y":
    run_command(upload_command, "Uploading package to PyPI")
else:
    print("Upload cancelled.")
    sys.exit(0)
