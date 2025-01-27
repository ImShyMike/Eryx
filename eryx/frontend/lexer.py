"""Lexer for the fronted."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Tuple

from colorama import Fore

from eryx.utils.errors import syntax_error


class TokenType(Enum):
    """All token types in the language."""

    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()

    ASSIGNMENT_OPERATOR = auto()

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
    ASSERT = auto()

    CLASS = auto()
    ENUM = auto()

    LOOP = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()

    IMPORT = auto()
    FROM = auto()
    AS = auto()

    EQUALS = auto()

    DEL = auto()

    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()

    EOF = auto()


SINGLE_CHAR_TOKENS = {
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
    "^": TokenType.BINARY_OPERATOR,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ".": TokenType.DOT,
    "=": TokenType.EQUALS,
    "<": TokenType.BINARY_OPERATOR,
    ">": TokenType.BINARY_OPERATOR,
    "&": TokenType.BINARY_OPERATOR,
    "|": TokenType.BINARY_OPERATOR,
}

DOUBLE_CHAR_TOKENS = {
    "==": TokenType.BINARY_OPERATOR,
    "!=": TokenType.BINARY_OPERATOR,
    "<=": TokenType.BINARY_OPERATOR,
    ">=": TokenType.BINARY_OPERATOR,
    "&&": TokenType.BINARY_OPERATOR,
    "||": TokenType.BINARY_OPERATOR,
    "<<": TokenType.BINARY_OPERATOR,
    ">>": TokenType.BINARY_OPERATOR,
    "**": TokenType.BINARY_OPERATOR,
    "+=": TokenType.ASSIGNMENT_OPERATOR,
    "-=": TokenType.ASSIGNMENT_OPERATOR,
    "*=": TokenType.ASSIGNMENT_OPERATOR,
    "/=": TokenType.ASSIGNMENT_OPERATOR,
    "%=": TokenType.ASSIGNMENT_OPERATOR,
    "^=": TokenType.ASSIGNMENT_OPERATOR,
    "&=": TokenType.ASSIGNMENT_OPERATOR,
    "|=": TokenType.ASSIGNMENT_OPERATOR,
    "++": TokenType.BINARY_OPERATOR,
    "--": TokenType.BINARY_OPERATOR,
}

KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "func": TokenType.FUNC,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
    "loop": TokenType.LOOP,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "del": TokenType.DEL,
    "class": TokenType.CLASS,
    "enum": TokenType.ENUM,
    "assert": TokenType.ASSERT,
}


@dataclass()
class Token:
    """Token class."""

    value: Any
    type: TokenType
    position: tuple[int, int, int]  # (line, col, length)


def is_skipable(
    char: str, current_line: int, current_col: int
) -> Tuple[bool, int, int]:
    """Check if a character is a skipable character."""
    if char in ("\n", "\r"):
        return (True, current_line + 1, 0)  # Skip newlines and carriage returns

    return (
        char
        in (
            " ",
            "\t",
        ),
        current_line,
        current_col,
    )  # Skip spaces and tabs


def pop_src(src: list[str], current_col: int, count: int = 1) -> Tuple[str, int]:
    """Pop the first element of the source code."""
    result = ""
    for _ in range(count):
        result += src.pop(0)
    return result, current_col + len(result)


def tokenize(source_code: str) -> list[Token]:
    """Tokenize the source code."""
    tokens = []  # Initialize the tokens list
    src = list(source_code)
    comment = False  # Comment flag
    current_line = 1
    current_col = 0

    while len(src) > 0:
        negative_num = False  # Reset the negative number flag

        # Skip comments
        if comment:
            if src[0] in ("\n", "\r"):
                current_line += 1  # Increment the line count
                current_col = 0  # Reset the column count
                comment = False
            elif src[0] == ";":
                comment = False
            _, current_col = pop_src(src, current_col)
            continue

        # Skip skipable characters
        skipable, current_line, current_col = is_skipable(
            src[0], current_line, current_col
        )
        if skipable:  # spaces, newlines, tabs, and carriage returns
            _, current_col = pop_src(src, current_col)
            continue

        # Check for double character tokens first
        if len(src) > 1 and src[0] + src[1] in DOUBLE_CHAR_TOKENS:
            token, current_col = pop_src(src, current_col, 2)
            tokens.append(
                Token(token, DOUBLE_CHAR_TOKENS[token], (current_line, current_col, 2))
            )
            continue

        # Check for single character tokens
        if src[0] in SINGLE_CHAR_TOKENS:
            token, current_col = pop_src(src, current_col)

            # Single character token
            tokens.append(
                Token(token, SINGLE_CHAR_TOKENS[token], (current_line, current_col, 1))
            )
            continue

        # Check for comments
        if src[0] == "#":
            comment = True
            _, current_col = pop_src(src, current_col)
            continue

        # If its not a single/double character token, check for negative numbers/variables
        if src[0] == "-":
            if len(src) > 0 and (src[1].isdigit() or src[1].isalpha() or src[1] == "_"):
                negative_num = True  # Set negative number flag
                _, current_col = pop_src(src, current_col)
            else:
                # If its not a negative number, its a "-" operator
                token, current_col = pop_src(src, current_col)
                tokens.append(
                    Token(
                        token,
                        TokenType.BINARY_OPERATOR,
                        (current_line, current_col, 1),
                    )
                )
                continue

        # Check for multi character tokens
        if src[0].isdigit():  # Number
            number, current_col = pop_src(src, current_col)

            if negative_num:
                number = "-" + number  # Add negative sign to the number

            dots = 0
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                if src[0] == ".":
                    dots += 1
                    if dots > 1:
                        break  # Only one dot is allowed in a number
                token, current_col = pop_src(src, current_col)
                number += token
            tokens.append(
                Token(
                    number,
                    TokenType.NUMBER,
                    (
                        current_line,
                        current_col,
                        (len(number) + 1) if negative_num else len(number),
                    ),
                )
            )

        elif src[0].isalpha() or src[0] == "_":  # Identifier
            identifier, current_col = pop_src(src, current_col)
            while len(src) > 0 and (
                src[0].isalpha() or src[0].isdigit() or src[0] == "_"
            ):
                token, current_col = pop_src(src, current_col)
                identifier += token

            if identifier in KEYWORDS:  # Check if the identifier is a keyword
                tokens.append(
                    Token(
                        identifier,
                        KEYWORDS[identifier],
                        (current_line, current_col, len(identifier)),
                    )
                )

            else:  # If its not a keyword, its an identifier
                if negative_num:  # Fake a unary minus operator
                    tokens.append(
                        Token("(", TokenType.OPEN_PAREN, (current_line, current_col, 1))
                    )
                    tokens.append(
                        Token("0", TokenType.NUMBER, (current_line, current_col, 1))
                    )
                    tokens.append(
                        Token(
                            "-",
                            TokenType.BINARY_OPERATOR,
                            (current_line, current_col, 1),
                        )
                    )

                tokens.append(
                    Token(
                        identifier,
                        TokenType.IDENTIFIER,
                        (current_line, current_col, len(identifier)),
                    )
                )

                if negative_num:  # Finish the unary minus operator
                    tokens.append(
                        Token(
                            ")", TokenType.CLOSE_PAREN, (current_line, current_col, 1)
                        )
                    )

        elif src[0] == '"':  # String
            _, current_col = pop_src(src, current_col)  # Remove the opening quote
            string = ""
            while len(src) > 0 and src[0] != '"':
                token, current_col = pop_src(src, current_col)
                string += token
            _, current_col = pop_src(src, current_col)  # Remove the closing quote
            tokens.append(
                Token(
                    string,
                    TokenType.STRING,
                    (current_line, current_col, len(string) + 2),
                )
            )

        else:
            # If this is reached, its an unknown character
            syntax_error(
                source_code,
                (current_line, current_col, 1),
                f"Unknown character found in source '{Fore.MAGENTA}{src.pop(0)}{Fore.RESET}'",
            )

    # Add the final EOF token
    tokens.append(Token("EOF", TokenType.EOF, (current_line, current_col, 1)))

    return tokens
