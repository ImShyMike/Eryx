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

    return lines[line - 1]


# TODO: fix this, its VERY broken
def syntax_error(
    source_code: str, pos: int | tuple[int, int], error_message: str
) -> None:
    """Handle a syntax error."""
    length = 1 if isinstance(pos, int) else (pos[1] - pos[0])
    current_line, current_col = position_to_line_column(
        source_code, pos if isinstance(pos, int) else pos[0]
    )
    line = get_line_strings(source_code, current_line)
    print()
    print(f"{Fore.CYAN}{str(current_line).rjust(3)}:{Fore.RESET} {line}")
    print(
        Fore.YELLOW
        + ("^" * length).rjust(current_col + len(str(current_line).rjust(3)) + 2)
        + Fore.RESET
    )
    print(f"{Fore.RED}SyntaxError{Fore.RESET}: {error_message}")
    sys.exit(1)
