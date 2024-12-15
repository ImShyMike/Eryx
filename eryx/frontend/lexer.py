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

    def __init__(self, value, token_type: TokenType, line: int) -> None:
        self.value = value
        self.type = token_type
        self.line = line

    def __repr__(self) -> str:
        return "{" + f' "value": "{self.value}", "type": {self.type.name} ' + "}"


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
    src = list(source_code)

    while len(src) > 0:
        negative_num = False
        starting_length = len(src)
        line = get_line(source_code, src)
        if src[0] == "(":
            tokens.append(Token(src.pop(0), TokenType.OPEN_PAREN, line))
        elif src[0] == ")":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_PAREN, line))
        elif src[0] == "{":
            tokens.append(Token(src.pop(0), TokenType.OPEN_BRACE, line))
        elif src[0] == "}":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_BRACE, line))
        elif src[0] == "[":
            tokens.append(Token(src.pop(0), TokenType.OPEN_BRACKET, line))
        elif src[0] == "]":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_BRACKET, line))
        elif src[0] in ("+", "-", "*", "/", "%"):
            if src[0] == "-" and len(src) > 0 and src[1].isdigit():
                negative_num = True # Keep size the same
            else:
                tokens.append(Token(src.pop(0), TokenType.BINARY_OPERATOR, line))
        elif src[0] == "=":
            tokens.append(Token(src.pop(0), TokenType.EQUALS, line))
        elif src[0] == ";":
            tokens.append(Token(src.pop(0), TokenType.SEMICOLON, line))
        elif src[0] == ",":
            tokens.append(Token(src.pop(0), TokenType.COMMA, line))
        elif src[0] == ":":
            tokens.append(Token(src.pop(0), TokenType.COLON, line))
        elif src[0] == ".":
            tokens.append(Token(src.pop(0), TokenType.DOT, line))

        if starting_length != len(src):
            continue

        if negative_num:
            src.pop(0) # Remove the negative sign

        if src[0].isdigit():  # Number
            number = src.pop(0)
            if negative_num:
                number = "-" + number
            dots = 0
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                if src[0] == ".":
                    dots += 1
                    if dots > 1:
                        break
                number += src.pop(0)
            tokens.append(Token(number, TokenType.NUMBER, line))

        elif src[0].isalpha() or src[0] == "_": # Identifier
            identifier = src.pop(0)
            while len(src) > 0 and (src[0].isalpha() or src[0].isdigit() or src[0] == "_"):
                identifier += src.pop(0)

            if identifier in KEYWORDS:
                tokens.append(Token(identifier, KEYWORDS[identifier], line))
            else:
                tokens.append(Token(identifier, TokenType.IDENTIFIER, line))
        elif is_skipable(src[0]):
            src.pop(0)

        elif src[0] == '"': # String
            src.pop(0)
            string = ""
            while len(src) > 0 and src[0] != '"':
                string += src.pop(0)
            src.pop(0)
            tokens.append(Token(string, TokenType.STRING, line))

        else:
            print(f"Character not found in source: {src.pop(0)}")
            exit(1)

    line = get_line(source_code, src)
    tokens.append(Token("EOF", TokenType.EOF, line))

    return tokens


if __name__ == "__main__":
    # Test for the lexer
    with open("./test.txt", "r", encoding="utf-8") as file:
        code = file.read()

    # Print the tokenized code
    for token in tokenize(code):
        print(token)
