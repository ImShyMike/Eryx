"""Lexer for the fronted."""

from enum import Enum, auto


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
    EQUALS = auto()

    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()

    EOF = auto()


class Token:
    """Token class."""

    def __init__(self, value, token_type: TokenType, position: int | tuple[int, int]) -> None:
        self.value = value
        self.type = token_type
        self.position = position

    def __repr__(self) -> str:
        return (
            "{"
            + f' "value": "{self.value}", "type": {self.type.name}, "position", {self.position} '
            + "}"
        )

    def to_dict(self) -> dict:
        """Return the token as a dictionary."""
        return {
            "value": self.value,
            "type": self.type.name,
            "position": self.position,
        }


KEYWORDS = {"let": TokenType.LET, "const": TokenType.CONST, "func": TokenType.FUNC}


def is_skipable(char: str) -> bool:
    """Check if a character is a skipable character."""
    return char in (
        " ",
        "\n",
        "\t",
        "\r",
    )  # Skip spaces, newlines, tabs, and carriage returns


def get_line(source_code: str, src: list[str]) -> int:
    """Get the line of the current token."""
    line = source_code.count("\n", 0, len(source_code) - len(src)) + 1

    return line


def tokenize(source_code: str) -> list[Token]:
    """Tokenize the source code."""
    tokens = []
    source_size = len(source_code)
    src = list(source_code)

    while len(src) > 0:
        negative_num = False
        starting_length = len(src)
        current_pos = source_size - len(src)
        if src[0] == "(":
            tokens.append(Token(src.pop(0), TokenType.OPEN_PAREN, current_pos))
        elif src[0] == ")":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_PAREN, current_pos))
        elif src[0] == "{":
            tokens.append(Token(src.pop(0), TokenType.OPEN_BRACE, current_pos))
        elif src[0] == "}":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_BRACE, current_pos))
        elif src[0] == "[":
            tokens.append(Token(src.pop(0), TokenType.OPEN_BRACKET, current_pos))
        elif src[0] == "]":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_BRACKET, current_pos))
        elif src[0] in ("+", "-", "*", "/", "%"):
            if src[0] == "-" and len(src) > 0 and src[1].isdigit():
                negative_num = True  # Keep size the same
            else:
                tokens.append(Token(src.pop(0), TokenType.BINARY_OPERATOR, current_pos))
        elif src[0] == "=":
            tokens.append(Token(src.pop(0), TokenType.EQUALS, current_pos))
        elif src[0] == ";":
            tokens.append(Token(src.pop(0), TokenType.SEMICOLON, current_pos))
        elif src[0] == ",":
            tokens.append(Token(src.pop(0), TokenType.COMMA, current_pos))
        elif src[0] == ":":
            tokens.append(Token(src.pop(0), TokenType.COLON, current_pos))
        elif src[0] == ".":
            tokens.append(Token(src.pop(0), TokenType.DOT, current_pos))

        # If the length of the source code has changed, skip the rest of the loop
        if starting_length != len(src):
            continue

        if negative_num:
            src.pop(0)  # Remove the negative sign from negative numbers

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
                tokens.append(Token(identifier, KEYWORDS[identifier], (start_pos, end_pos)))
            else:
                tokens.append(Token(identifier, TokenType.IDENTIFIER, (start_pos, end_pos)))

        elif is_skipable(src[0]):
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

        else:
            print(f"Character not found in source: {src.pop(0)}")
            exit(1)

    current_pos = source_size - len(src)
    tokens.append(Token("EOF", TokenType.EOF, (current_pos, current_pos)))

    return tokens
