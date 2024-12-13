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

    BINARY_OPERATOR = auto()

    LET = auto()
    CONST = auto()
    EQUALS = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()

    EOF = auto()


class Token:
    """Token class."""

    def __init__(self, value, token_type) -> None:
        self.value = value
        self.type = token_type

    def __repr__(self) -> str:
        return "{" + f' "value": "{self.value}", "type": {self.type.name} ' + "}"


KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST
}


def is_skipable(char: str) -> bool:
    """Check if a character is a skipable character."""
    return char in (" ", "\n", "\t", "\r")


def tokenize(source_code: str) -> list[Token]:
    """Tokenize the source code."""
    tokens = []
    src = list(source_code)

    while len(src) > 0:
        if src[0] == "(":
            tokens.append(Token(src.pop(0), TokenType.OPEN_PAREN))
        elif src[0] == ")":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_PAREN))
        elif src[0] == "[":
            tokens.append(Token(src.pop(0), TokenType.OPEN_BRACE))
        elif src[0] == "]":
            tokens.append(Token(src.pop(0), TokenType.CLOSE_BRACE))
        elif src[0] in ("+", "-", "*", "/", "%"):
            tokens.append(Token(src.pop(0), TokenType.BINARY_OPERATOR))
        elif src[0] == "=":
            tokens.append(Token(src.pop(0), TokenType.EQUALS))
        elif src[0] == ";":
            tokens.append(Token(src.pop(0), TokenType.SEMICOLON))
        elif src[0] == ",":
            tokens.append(Token(src.pop(0), TokenType.COMMA))
        elif src[0] == ":":
            tokens.append(Token(src.pop(0), TokenType.COLON))
        else:
            if src[0].isdigit():
                number = src.pop(0)
                while len(src) > 0 and src[0].isdigit():
                    number += src.pop(0)
                tokens.append(Token(number, TokenType.NUMBER))

            elif src[0].isalpha():
                identifier = src.pop(0)
                while len(src) > 0 and (src[0].isalpha() or src[0].isdigit()):
                    identifier += src.pop(0)

                if identifier in KEYWORDS:
                    tokens.append(Token(identifier, KEYWORDS[identifier]))
                else:
                    tokens.append(Token(identifier, TokenType.IDENTIFIER))
            elif is_skipable(src[0]):
                src.pop(0)
            else:
                print(f"Character not found in source: {src.pop(0)}")
                exit(1)

    tokens.append(Token("EOF", TokenType.EOF))

    return tokens


if __name__ == "__main__":
    # Test for the lexer
    with open("./test.txt", "r", encoding="utf-8") as file:
        code = file.read()

    # Print the tokenized code
    for token in tokenize(code):
        print(token)
