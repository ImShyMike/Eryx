"""Stuff for handling errors."""

import sys
from colorama import Fore

def position_to_line_column(source_code: str, position: int) -> tuple[int, int]:
    """Convert a position to a line and column number."""
    # Get the substring up to the given position
    substring = source_code[:position]

    # Count the number of newline characters to determine the line
    line = substring.count("\n") + 1

    # Find the column by looking for the last newline
    last_newline_pos = substring.rfind("\n")
    column = position - last_newline_pos if last_newline_pos != -1 else position + 1

    return (line, column)


def get_line_strings(source_code: str, line: int) -> str:
    """Get the line string from the source code."""
    lines = source_code.split("\n")

    return lines[line - 10: line]

def syntax_error(source_code: str, pos: int, error_message: str) -> None:
    """Handle a syntax error."""
    current_line, current_col = position_to_line_column(
        source_code, pos
    )
    lines = get_line_strings(source_code, current_line)
    print()
    for n, line in enumerate(lines):
        print(f"{Fore.CYAN}{str(current_line - (len(lines) - n) + 1).rjust(3)}:{Fore.WHITE} {line}")
    print(
        Fore.YELLOW
        + "^".rjust(current_col + len(str(current_line).rjust(3)) + 2)
        + Fore.WHITE
    )
    print(f"{Fore.RED}SyntaxError{Fore.WHITE}: {error_message}")
    sys.exit(1)
