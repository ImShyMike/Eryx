"""Stuff for handling errors."""

from colorama import Fore


def get_line_strings(source_code: str, line: int) -> str:
    """Get the line string from the source code."""
    lines = source_code.split("\n")

    return lines[line - 1]


def syntax_error(
    source_code: str, pos: tuple[int, int, int], error_message: str
) -> None:
    """Handle a syntax error."""
    line, col, length = pos  # Unpack the position tuple

    line_text = get_line_strings(source_code, line)  # Get a snippet of the code

    error_line = f"{Fore.CYAN}{str(line).rjust(3)}:{Fore.RESET} {line_text}"  # Format the error line

    marker = (
        "^" * length
    )  # Under the error line, add a marker to show where the error is

    line_number_size = len(str(line).rjust(3))  # Get the size of the line number

    positioned_marker = marker.rjust(
        col + line_number_size + 1 + len(marker)
    )  # Position the marker

    formatted_marker = (
        f"{Fore.YELLOW}{positioned_marker}{Fore.RESET}"  # Format the marker
    )

    error_msg = f"{Fore.RED}SyntaxError{Fore.RESET}: {error_message}"  # Format the error message

    # pylint pls dont crash this time
    raise SyntaxError(f"{error_line}\n{formatted_marker}\n{error_msg}")
