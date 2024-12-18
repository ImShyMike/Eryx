"""Lexer for the fronted."""

import sys
from enum import Enum, auto
from typing import Any, Union

from colorama import Fore, init

init(autoreset=True)


class TokenType(Enum):
    """All token types in the language."""

    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()

    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()

    DOUBLE_QUOTE = auto()

    BINARY_OPERATOR = auto()

    LET = auto()
    CONST = auto()
    FUNC = auto()
    IF = auto()
    ELSE = auto()
    RETURN = auto()

    EQUALS = auto()

    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()

    EOF = auto()


class Token:
    """Token class."""

    def __init__(
        self, value: Any, token_type: TokenType, position: Union[int, tuple[int, int]]
    ):
        self.value = value
        self.type = token_type
        self.position = position

    def __repr__(self) -> str:
        return f'Token("{self.value}", {self.type.name}, {self.position})'


KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "func": TokenType.FUNC,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
}


def is_skipable(char: str) -> bool:
    """Check if a character is a skipable character."""
    return char in (
        " ",
        "\n",
        "\t",
        "\r",
    )  # Skip spaces, newlines, tabs, and carriage returns


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


def get_line_string(source_code: str, line: int) -> str:
    """Get the line string from the source code."""
    lines = source_code.split("\n")

    return lines[line - 1]


def tokenize(source_code: str) -> list[Token]:
    """Tokenize the source code."""
    tokens = []
    source_size = len(source_code)
    src = list(source_code)

    while len(src) > 0:
        negative_num = False
        current_pos = source_size - len(src)

        single_char_tokens = {
            "(": TokenType.OPEN_PAREN,
            ")": TokenType.CLOSE_PAREN,
            "{": TokenType.OPEN_BRACE,
            "}": TokenType.CLOSE_BRACE,
            "[": TokenType.OPEN_BRACKET,
            "]": TokenType.CLOSE_BRACKET,
            "+": TokenType.BINARY_OPERATOR,
            "*": TokenType.BINARY_OPERATOR,
            "/": TokenType.BINARY_OPERATOR,
            "%": TokenType.BINARY_OPERATOR,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ".": TokenType.DOT,
        }

        # Check for single character tokens first
        if src[0] in single_char_tokens:
            token = src.pop(0)
            tokens.append(Token(token, single_char_tokens[token], current_pos))
            continue

        # If its not a single character token, check for negative numbers
        if src[0] == "-":
            if len(src) > 0 and src[1].isdigit():
                negative_num = True
            else:
                tokens.append(Token(src.pop(0), TokenType.BINARY_OPERATOR, current_pos))
                continue

        # If its a negative number, remove the negative sign
        if negative_num:
            src.pop(0)

        # Check for multi character tokens
        if src[0].isdigit():  # Number
            start_pos = current_pos
            end_pos = start_pos + (1 if negative_num else 0)
            number = src.pop(0)
            if negative_num:
                number = "-" + number
            dots = 0
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                if src[0] == ".":
                    dots += 1
                    if dots > 1:
                        break
                end_pos += 1
                number += src.pop(0)
            tokens.append(Token(number, TokenType.NUMBER, (start_pos, end_pos)))

        elif src[0].isalpha() or src[0] == "_":  # Identifier
            start_pos = current_pos
            end_pos = start_pos
            identifier = src.pop(0)
            while len(src) > 0 and (
                src[0].isalpha() or src[0].isdigit() or src[0] == "_"
            ):
                end_pos += 1
                identifier += src.pop(0)

            if identifier in KEYWORDS:
                tokens.append(
                    Token(identifier, KEYWORDS[identifier], (start_pos, end_pos))
                )
            else:
                tokens.append(
                    Token(identifier, TokenType.IDENTIFIER, (start_pos, end_pos))
                )

        elif is_skipable(src[0]):  # Skip spaces, newlines, tabs, and carriage returns
            src.pop(0)

        elif src[0] == '"':  # String
            start_pos = current_pos
            end_pos = start_pos
            src.pop(0)
            string = ""
            while len(src) > 0 and src[0] != '"':
                end_pos += 1
                string += src.pop(0)
            src.pop(0)
            tokens.append(Token(string, TokenType.STRING, (start_pos, end_pos + 1)))

        elif src[0] in ("=", "<", ">"):  # Binary operator
            if len(src) > 1:
                if src[0] == "=" and src[1] == "=":
                    tokens.append(
                        Token(
                            "==",
                            TokenType.BINARY_OPERATOR,
                            (current_pos, current_pos + 1),
                        )
                    )
                    src.pop(0)
                    src.pop(0)
                    continue

                if src[0] == "<" and src[1] == "=":
                    tokens.append(
                        Token(
                            "<=",
                            TokenType.BINARY_OPERATOR,
                            (current_pos, current_pos + 1),
                        )
                    )
                    src.pop(0)
                    src.pop(0)
                    continue

                if src[0] == ">" and src[1] == "=":
                    tokens.append(
                        Token(
                            ">=",
                            TokenType.BINARY_OPERATOR,
                            (current_pos, current_pos + 1),
                        )
                    )
                    src.pop(0)
                    src.pop(0)
                    continue

            if src[0] in ("<", ">"):
                tokens.append(Token(src.pop(0), TokenType.BINARY_OPERATOR, current_pos))
                continue

            if src[0] == "=":
                tokens.append(Token(src.pop(0), TokenType.EQUALS, current_pos))

        elif src[0] == "!" and len(src) > 1 and src[1] == "=":  # Binary operator
            tokens.append(
                Token("!=", TokenType.BINARY_OPERATOR, (current_pos, current_pos + 1))
            )
            src.pop(0)
            src.pop(0)

        else:
            # If this is reached, its an unknown character
            current_line, current_col = position_to_line_column(
                source_code, current_pos
            )
            line = get_line_string(source_code, current_line)
            current_line_str = str(current_line).rjust(3)
            print(f"\n{Fore.CYAN}{current_line_str}:{Fore.WHITE} {line}")
            print(
                Fore.YELLOW
                + "^".rjust(current_col + len(current_line_str) + 2)
                + Fore.WHITE
            )
            print(
                f"{Fore.RED}SyntaxError{Fore.WHITE}: Unknown character found in source "
                f"'{Fore.MAGENTA}{src.pop(0)}{Fore.WHITE}'"
            )
            sys.exit(1)

    tokens.append(Token("EOF", TokenType.EOF, source_size - len(src)))

    return tokens
