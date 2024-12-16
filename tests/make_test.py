import os
import sys
import tkinter as tk
from io import StringIO
from tkinter import messagebox

# Add the parent directory to the sys.path for imports
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(current_path)))

from eryx.__init__ import CURRENT_VERSION
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint

os.makedirs(os.path.join(current_path, "tests"), exist_ok=True)


def generate_ast(code):
    """Generate AST from code using the parser."""
    parser = Parser()
    return parser.produce_ast(code)


def evaluate_code(ast, environment):
    """Evaluate the AST and return the result."""
    return evaluate(ast, environment)


def capture_output(func, *args, **kwargs):
    """Capture output printed during the execution of the code."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        func(*args, **kwargs)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout


def create_test_files(code, description, test_name):
    """Create the test files with actual values."""
    # Create the folder to store the test files
    test_folder = os.path.join(current_path, "test", test_name)
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Create .eryx file (the code itself)
    with open(
        os.path.join(test_folder, f"{test_name}.eryx"), "w", encoding="utf8"
    ) as f:
        f.write(code)

    # Generate AST
    test_ast = generate_ast(code)
    with open(
        os.path.join(test_folder, f"{test_name}.eryx.ast"), "w", encoding="utf8"
    ) as f:
        try:
            f.write(pprint(test_ast, print_output=False, use_color=False))
        except RuntimeError as e:
            print(f"Parser Error: {e}")
            os.removedirs(os.path.join(current_path, "test", test_name))
            return

    # Evaluate the AST
    test_result = evaluate_code(test_ast, Environment())
    with open(
        os.path.join(test_folder, f"{test_name}.eryx.eval"), "w", encoding="utf8"
    ) as f:
        try:
            f.write(pprint(test_result, print_output=False, use_color=False))
        except RuntimeError as e:
            print(f"Runtime Error: {e}")
            os.removedirs(os.path.join(current_path, "test", test_name))
            return

    # Capture printed output
    try:
        output = capture_output(evaluate_code, test_ast, Environment())
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        os.removedirs(os.path.join(current_path, "test", test_name))
        return
    with open(
        os.path.join(test_folder, f"{test_name}.eryx.output"), "w", encoding="utf8"
    ) as f:
        f.write(output[:-1])

    # Create info.test file (Description and expected behavior)
    with open(os.path.join(test_folder, "test.info"), "w", encoding="utf8") as f:
        f.write(f"Version: {CURRENT_VERSION}\n")
        f.write(f"Name: {test_name}\n")
        f.write(f"Description: {description}")

    messagebox.showinfo("Success", f"Test files for {test_name} have been created.")


def on_create_test():
    """Handle the create test button click."""
    code = code_text.get("1.0", tk.END).strip()
    description = description_entry.get()
    test_name = name_entry.get()

    if not code or not test_name:
        messagebox.showerror("Error", "Please provide both code and test name.")
        return

    # Call the function to create the test files
    create_test_files(code, description, test_name)


# Set up the Tkinter GUI
root = tk.Tk()
root.title("Test File Generator")
root.resizable(False, False)

# Code input
code_label = tk.Label(root, text="Code:")
code_label.pack()
code_text = tk.Text(root, height=10, width=50)
code_text.pack()

# Test name
name_label = tk.Label(root, text="Test Name:")
name_label.pack()
name_entry = tk.Entry(root, width=50)
name_entry.pack()

# Description
description_label = tk.Label(root, text="Description:")
description_label.pack()
description_entry = tk.Entry(root, width=50)
description_entry.pack()

# Create button
create_button = tk.Button(root, text="Create Test Files", command=on_create_test)
create_button.pack(pady=(0, 10))

# Run the Tkinter event loop
root.mainloop()
