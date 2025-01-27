"""Module for running Eryx code."""

from colorama import Fore

from eryx.frontend.lexer import tokenize
from eryx.frontend.parser import Parser
from eryx.frontend.transpiler import transpile
from eryx.runtime.environment import Environment, get_value
from eryx.runtime.interpreter import evaluate
from eryx.runtime.values import NullValue
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
    transpile_code: bool = False,
) -> str | None:
    """Run an Eryx file."""

    result = None

    environment = environment or Environment()
    parser = parser or Parser()

    try:
        if log_tokens:
            try:
                tokenized = tokenize(source_code)
                print("Tokenized:")
                pprint(TokenList(tokenized))
            except RuntimeError as e:
                print(f"{Fore.RED}Tokenizer Error{Fore.RESET}: {e}")
                return

        try:
            ast = parser.produce_ast(source_code)
            if log_ast:
                print("AST:")
                pprint(ast)
            if transpile_code:
                return transpile(ast.body, return_value=True)
        except RuntimeError as e:
            print(f"{Fore.RED}Parser Error{Fore.RESET}: {e}")
            return
    except SyntaxError as e:
        print(e)
        return

    try:
        result = evaluate(ast, environment)
        if log_result:
            print("\nResult:")
            pprint(result)
    except RuntimeError as e:
        print(f"{Fore.RED}Runtime Error{Fore.RESET}: {e}")

    if result is not None and not isinstance(result, NullValue):
        return get_value(result)
    return None
