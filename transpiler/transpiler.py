"""Eryx to python transpiler."""

from typing import List

from eryx.frontend.ast import (
    ArrayLiteral,
    AssertStatement,
    AssignmentExpression,
    BinaryExpression,
    BreakLiteral,
    CallExpression,
    ClassDeclaration,
    ContinueLiteral,
    DelStatement,
    Expression,
    ForStatement,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    ImportStatement,
    LoopStatement,
    MemberExpression,
    NumericLiteral,
    ObjectLiteral,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
    WhileStatement,
)
from eryx.frontend.parser import Parser

parser = Parser()

PRINT_OUTPUT = False

OUT = {}

def cprint(text: str | float | int = "", tabs: int = 0):
    """Print with tabs."""
    if not OUT:
        OUT["out"] = ""
    if PRINT_OUTPUT:
        print(f"{'    ' * tabs}{text}")
    else:
        OUT["out"] += f"{'    ' * tabs}{str(text)}\n"


def convert_value(value: Expression) -> str:
    """Convert value to python."""
    if isinstance(value, ArrayLiteral):
        return f"[{', '.join([convert_value(v) for v in value.elements])}]"

    if isinstance(value, StringLiteral):
        return f'"{value.value}"'

    if isinstance(value, NumericLiteral):
        return (
            str(value.value)
            if int(value.value) != value.value
            else str(int(value.value))
        )

    if isinstance(value, ObjectLiteral):
        result = "{ "
        for prop in value.properties:
            if prop.value:
                result += f'"{prop.key}": {convert_value(prop.value)}, '
            else:
                result += f'"{prop.key}": {prop.key}, '
        return result[:-2] + " }"

    if isinstance(value, Identifier):
        if value.symbol == "true":
            return "True"
        if value.symbol == "false":
            return "False"
        if value.symbol == "null":
            return "None"
        return value.symbol

    if isinstance(value, BinaryExpression):
        return (
            f"{convert_value(value.left)} {value.operator} {convert_value(value.right)}"
        )

    if isinstance(value, CallExpression):
        return (
            f"{convert_value(value.caller)}"
            f"({', '.join([convert_value(arg) for arg in value.arguments])})"
        )

    if isinstance(value, MemberExpression):
        if not value.computed:
            return f"{convert_value(value.object)}.{convert_value(value.property)}"

        return f"{convert_value(value.object)}[{convert_value(value.property)}]"

    return str(value)


def transpile(parsed_code: List[Statement], tabs: int = 0, main: bool = False) -> None:
    """Main transpiler function."""

    for node in parsed_code:
        if isinstance(node, FunctionDeclaration):
            cprint(f"def {node.name}({', '.join(node.arguments)}):", tabs)
            if node.body:
                transpile(node.body, tabs + 1)
            else:
                cprint("pass", tabs + 1)
            cprint()

        elif isinstance(node, IfStatement):
            cprint(f"if {convert_value(node.condition)}:", tabs)
            transpile(node.then, tabs + 1)
            if node.else_:
                cprint("else:", tabs)
                transpile([x for x in node.else_ if x], tabs + 1)

        elif isinstance(node, AssertStatement):
            if node.message:
                cprint(f"assert {convert_value(node.condition)}, {node.message}", tabs)
            else:
                cprint(f"assert {convert_value(node.condition)}", tabs)

        elif isinstance(node, AssignmentExpression):
            cprint(
                f"{convert_value(node.assigne)} {node.operator or '='} {convert_value(node.value)}",
                tabs,
            )

        elif isinstance(node, VariableDeclaration):
            if node.value:
                cprint(f"{node.identifier.symbol} = {convert_value(node.value)}", tabs)
            else:
                cprint(f"{node.identifier.symbol}", tabs)

        elif isinstance(node, WhileStatement):
            cprint(f"while {convert_value(node.condition)}:", tabs)
            transpile(node.body, tabs + 1)
            cprint()

        elif isinstance(node, ForStatement):
            cprint(f"for {node.variable} in {node.iterator}:", tabs)
            transpile(node.body, tabs + 1)
            cprint()

        elif isinstance(node, LoopStatement):
            cprint("while True:", tabs)
            transpile(node.body, tabs + 1)
            cprint()

        elif isinstance(node, BreakLiteral):
            cprint("break", tabs)

        elif isinstance(node, ContinueLiteral):
            cprint("continue", tabs)

        elif isinstance(node, ReturnStatement):
            if node.value:
                cprint(f"return {convert_value(node.value)}", tabs)
            else:
                cprint("return", tabs)

        elif isinstance(node, DelStatement):
            cprint(f"del {convert_value(node.identifier)}", tabs)

        elif isinstance(node, CallExpression):
            cprint(
                f"{convert_value(node.caller)}"
                f"({', '.join([convert_value(arg) for arg in node.arguments])})",
                tabs,
            )

        elif isinstance(node, Identifier):
            if node.symbol == "true":
                cprint("True", tabs)
            if node.symbol == "false":
                cprint("False", tabs)
            if node.symbol == "null":
                cprint("None", tabs)
            cprint(node.symbol, tabs)

        elif isinstance(node, ObjectLiteral):
            cprint("{", tabs)
            for prop in node.properties:
                if prop.value:
                    cprint(f'"{prop.key}": {convert_value(prop.value)},', tabs + 1)
                else:
                    cprint(f'"{prop.key}": {prop.key},', tabs + 1)
            cprint("}", tabs)

        elif isinstance(node, NumericLiteral):
            cprint(node.value, tabs)

        elif isinstance(node, StringLiteral):
            cprint(f'"{node.value}"', tabs)

        elif isinstance(node, BinaryExpression):
            cprint(
                f"{convert_value(node.left)} {node.operator} {convert_value(node.right)}",
                tabs,
            )

        elif isinstance(node, MemberExpression):
            if not node.computed:
                cprint(
                    f"{convert_value(node.object)}.{convert_value(node.property)}", tabs
                )
            else:
                cprint(
                    f"{convert_value(node.object)}[{convert_value(node.property)}]",
                    tabs,
                )

        elif isinstance(node, ArrayLiteral):
            cprint(f"[{', '.join([convert_value(v) for v in node.elements])}]", tabs)

        elif isinstance(node, ImportStatement):
            if node.alias:
                cprint(f"import {node.module} as {node.alias}", tabs)
            elif node.names:
                cprint(f"from {node.module} import {', '.join(node.names)}", tabs)
            else:
                cprint(f"import {node.module}", tabs)

        elif isinstance(node, ClassDeclaration):
            cprint(f"class {node.name}:", tabs)
            if node.arguments:
                for method in node.methods:
                    if isinstance(method, AssignmentExpression):
                        if method.value:
                            cprint(
                                f"{convert_value(method.assigne)} "
                                f"= {convert_value(method.value)}",
                                tabs + 1,
                            )
                cprint(
                    "def __init__(self, " + ", ".join(node.arguments) + "):", tabs + 1
                )
                for arg in node.arguments:
                    cprint(f"self.{arg} = {arg}", tabs + 2)
                for method in node.methods:
                    if isinstance(method, AssignmentExpression):
                        if method.value:
                            cprint(
                                f"self.{convert_value(method.assigne)} "
                                f"= {convert_value(method.value)}",
                                tabs + 2,
                            )
            for method in node.methods:
                if isinstance(method, FunctionDeclaration):
                    cprint(
                        f"def {method.name}({', '.join(['self'] + method.arguments)}):",
                        tabs + 1,
                    )
                    if method.body:
                        transpile(method.body, tabs + 2)
                    else:
                        cprint("pass", tabs + 2)
                elif isinstance(method, VariableDeclaration):
                    cprint(f"{method.identifier} = {method.value}", tabs)
            cprint()

        else:
            print(f"Unkown type: {type(node)}")

    if main:
        output = OUT.get("out", "")
        OUT["out"] = ""
        return output[:-1]


if __name__ == "__main__":
    SAMPLE_CODE = """class Test {
    yes: String
    a: Number
    c: Boolean
    g

    abc: Number = 1;

    func sum() {
        print("doing something...");
    }

    func nothing() {}
}

let tst = Test("aaaaa", 7, true, 1);

tst.sum();
tst.sum();

print(Test)

print(tst)

print(tst.a, Test.abc)"""

    parsed = parser.produce_ast(SAMPLE_CODE)
    print(transpile(parsed.body, main=True))

    # with open("sample.py", "w", encoding="utf8") as f:
    # f.write(transpile(parsed))
