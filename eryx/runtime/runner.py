"""Module for running Eryx code."""

import json

from colorama import Fore

from eryx.frontend.lexer import tokenize
from eryx.runtime.interpreter import evaluate
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.utils.pretty_print import pprint


def run_code(
    source_code: str,
    log_ast: bool = False,
    log_result: bool = False,
    log_tokens: bool = False,
    environment: Environment = None,
    parser: Parser = None,
) -> None:
    """Run an Eryx file."""

    environment = environment or Environment()
    parser = parser or Parser()

    if log_tokens:
        try:
            tokenized = tokenize(source_code)
            print("Tokenized:")
            print(json.dumps([token.to_dict() for token in tokenized], indent=2))
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
