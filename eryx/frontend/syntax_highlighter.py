"""Module for lexer based syntax highlighting code."""

from colorama import Fore, init
from lexer import TokenType, tokenize  # pylint: disable=import-error

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
    TokenType.IDENTIFIER: Fore.WHITE,
    TokenType.LET: Fore.RED,
    TokenType.CONST: Fore.RED,
    TokenType.FUNC: Fore.RED,
    TokenType.DOUBLE_QUOTE: Fore.GREEN,
    TokenType.EOF: Fore.WHITE,
}

NATIVE_FUNCTIONS = ["print", "time"]


def highlight(source_code: str) -> str:
    """Highlight the source code."""
    tokens = tokenize(source_code)
    highlighted_code = list(source_code)
    offset = 0

    for token in tokens:
        if token.value in NATIVE_FUNCTIONS:
            color = Fore.CYAN
        else:
            color = COLOR_TABLE.get(token.type, Fore.WHITE)

        if isinstance(token.position, int):
            highlighted_code.insert(token.position + offset, color)
            highlighted_code.insert(token.position + offset + 2, Fore.WHITE)
        else:
            highlighted_code.insert(token.position[0] + offset, color)
            highlighted_code.insert(token.position[1] + offset + 2, Fore.WHITE)
        offset += 2

    return "".join(highlighted_code)


if __name__ == "__main__":
    code = """let int = 10;

const float = 15.5;

let neg_num = -100;

let str = "abc";

const obj = {
    int,
    float,
    neg_num,
    abc_str: str,
    nested: {
        nested_val: 100,
        nest_squared: {
            maybe: "works"
        }
    }
};

let obj_lookup = "float";

print("test1", obj, obj[obj_lookup], obj.nested.nested_val, obj.nested["nest_squared"].maybe)"""

    print(highlight(code))
