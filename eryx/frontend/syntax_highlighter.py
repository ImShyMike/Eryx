"""Module for lexer based syntax highlighting code."""

# This file is obsolete for now (may be used in the future)

from colorama import Fore, init

from eryx.frontend.lexer import TokenType, tokenize

init(autoreset=True)

COLOR_TABLE = {
    TokenType.OPEN_PAREN: Fore.BLUE,
    TokenType.CLOSE_PAREN: Fore.BLUE,
    TokenType.OPEN_BRACE: Fore.BLUE,
    TokenType.CLOSE_BRACE: Fore.BLUE,
    TokenType.OPEN_BRACKET: Fore.BLUE,
    TokenType.CLOSE_BRACKET: Fore.BLUE,
    TokenType.BINARY_OPERATOR: Fore.YELLOW,
    TokenType.EQUALS: Fore.YELLOW,
    TokenType.SEMICOLON: Fore.YELLOW,
    TokenType.COMMA: Fore.YELLOW,
    TokenType.COLON: Fore.YELLOW,
    TokenType.DOT: Fore.YELLOW,
    TokenType.NUMBER: Fore.GREEN,
    TokenType.STRING: Fore.GREEN,
    TokenType.IDENTIFIER: Fore.RESET,
    TokenType.LET: Fore.RED,
    TokenType.CONST: Fore.RED,
    TokenType.FUNC: Fore.RED,
    TokenType.DOUBLE_QUOTE: Fore.GREEN,
    TokenType.EOF: Fore.RESET,
}

NATIVE_FUNCTIONS = [
    "print",
    "time",
    "input",
    "readfile",
    "len",
    "exit",
    "str",
    "int",
    "bool",
    "array",
    "type",
    "sum",
    "min",
    "max",
]


def highlight(source_code: str) -> str:
    """Highlight the source code."""
    tokens = tokenize(source_code)
    highlighted_code = list(source_code)
    offset = 0

    for token in tokens:
        if token.value in NATIVE_FUNCTIONS:
            color = Fore.CYAN
        else:
            color = COLOR_TABLE.get(token.type, Fore.RESET)

        if isinstance(token.position, int):
            highlighted_code.insert(token.position + offset, color)
            highlighted_code.insert(token.position + offset + 2, Fore.RESET)
        else:
            highlighted_code.insert(token.position[0] + offset, color)
            highlighted_code.insert(token.position[1] + offset + 2, Fore.RESET)
        offset += 2

    return "".join(highlighted_code)
