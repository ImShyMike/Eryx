"""Lexer for the fronted."""

from enum import Enum, auto
from typing import Any, Union

from colorama import Fore

from eryx.utils.errors import syntax_error


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
}


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


def is_skipable(char: str) -> bool:
    """Check if a character is a skipable character."""
    return char in (
        " ",
        "\n",
        "\t",
        "\r",
    )  # Skip spaces, newlines, tabs, and carriage returns


def tokenize(source_code: str) -> list[Token]:
    """Tokenize the source code."""
    tokens = [] # Initialize the tokens list
    src = list(source_code)
    current_pos = -1
    comment = False  # Comment flag

    while len(src) > 0:
        negative_num = False  # Reset the negative number flag
        current_pos += 1  # Increment the current position

        # Skip comments
        if comment:
            if src[0] in ("\n", "\r", ";"):
                comment = False
            src.pop(0)
            continue

        # Skip skipable characters
        if is_skipable(src[0]):  # spaces, newlines, tabs, and carriage returns
            src.pop(0)
            continue

        # Check for double character tokens first
        if len(src) > 1 and src[0] + src[1] in DOUBLE_CHAR_TOKENS:
            token = src.pop(0) + src.pop(0)
            tokens.append(
                Token(token, DOUBLE_CHAR_TOKENS[token], (current_pos, current_pos + 1))
            )
            continue

        # Check for single character tokens
        if src[0] in SINGLE_CHAR_TOKENS:
            token = src.pop(0)

            # Single character token
            tokens.append(Token(token, SINGLE_CHAR_TOKENS[token], current_pos))
            continue

        # Check for comments
        if src[0] == "#":
            comment = True
            src.pop(0)
            continue

        # If its not a single/double character token, check for negative numbers/variables
        if src[0] == "-":
            if len(src) > 0 and (src[1].isdigit() or src[1].isalpha() or src[1] == "_"):
                negative_num = True  # Set negative number flag
                src.pop(0) 
            else:
                # If its not a negative number, its a "-" operator
                tokens.append(Token(src.pop(0), TokenType.BINARY_OPERATOR, current_pos))
                continue

        # Check for multi character tokens
        if src[0].isdigit():  # Number
            start_pos = current_pos
            end_pos = start_pos
            number = src.pop(0)

            if negative_num:
                end_pos += 1
                number = "-" + number  # Add negative sign to the number

            dots = 0
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                if src[0] == ".":
                    dots += 1
                    if dots > 1:
                        break  # Only one dot is allowed in a number
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

            if identifier in KEYWORDS:  # Check if the identifier is a keyword
                tokens.append(
                    Token(identifier, KEYWORDS[identifier], (start_pos, end_pos))
                )

            else:  # If its not a keyword, its an identifier
                if negative_num:  # Fake a unary minus operator
                    tokens.append(
                        Token("(", TokenType.OPEN_PAREN, (start_pos, end_pos))
                    )
                    tokens.append(Token("0", TokenType.NUMBER, (start_pos, end_pos)))
                    tokens.append(
                        Token("-", TokenType.BINARY_OPERATOR, (start_pos, end_pos))
                    )

                tokens.append(
                    Token(identifier, TokenType.IDENTIFIER, (start_pos, end_pos))
                )

                if negative_num:  # Finish the unary minus operator
                    tokens.append(
                        Token(")", TokenType.CLOSE_PAREN, (start_pos, end_pos))
                    )

        elif src[0] == '"':  # String
            start_pos = current_pos
            end_pos = start_pos
            src.pop(0)  # Remove the opening quote
            string = ""
            while len(src) > 0 and src[0] != '"':
                end_pos += 1
                string += src.pop(0)
            src.pop(0)  # Remove the closing quote
            tokens.append(Token(string, TokenType.STRING, (start_pos, end_pos + 1)))

        else:
            # If this is reached, its an unknown character
            syntax_error(
                source_code,
                current_pos,
                f"Unknown character found in source '{Fore.MAGENTA}{src.pop(0)}{Fore.RESET}'",
            )

    # Add the final EOF token
    tokens.append(Token("EOF", TokenType.EOF, current_pos + 1))

    return tokens
