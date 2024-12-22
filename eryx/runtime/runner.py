"""Module for running Eryx code."""

from colorama import Fore

from eryx.frontend.lexer import tokenize
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint


class TokenList:
    """List of tokens to use with the pretty printer."""

    def __init__(self, tokens: list):
        self.tokens = tokens


def run_code(
    source_code: str,
    log_ast: bool = False,
    log_result: bool = False,
    log_tokens: bool = False,
    environment: Environment | None = None,
    parser: Parser | None = None,
) -> None:
    """Run an Eryx file."""

    environment = environment or Environment()
    parser = parser or Parser()

    if log_tokens:
        try:
            tokenized = tokenize(source_code)
            print("Tokenized:")
            pprint(TokenList(tokenized))
        except RuntimeError as e:
            print(f"{Fore.RED}Tokenizer Error: {e}{Fore.WHITE}")
            return

    try:
        ast = parser.produce_ast(source_code)
        if log_ast:
            print("AST:")
            pprint(ast)
    except RuntimeError as e:
        print(f"{Fore.RED}Parser Error: {e}{Fore.WHITE}")
        return

    try:
        result = evaluate(ast, environment)
        if log_result:
            print("\nResult:")
            pprint(result)
    except RuntimeError as e:
        print(f"{Fore.RED}Runtime Error: {e}{Fore.WHITE}")

    return
