"""Interpreter for the runtime."""

from frontend.ast import NodeType, Statement, BinaryExpression, Identifier, Program, VariableDeclaration
from runtime.environment import Environment
from runtime.values import NumberValue, RuntimeValue, NullValue, ValueType


# STATEMENTS
def eval_variable_declaration(
    declaration: VariableDeclaration, environtment: Environment
) -> RuntimeValue:
    """Evaluate a variable declaration."""
    value = evaluate(declaration.value, environtment) if declaration.value else NullValue()
    return environtment.declare_variable(declaration.identifier.symbol, value, declaration.constant)

def eval_program(program: Program, environtment: Environment) -> RuntimeValue:
    """Evaluate a program."""
    last_evaluated = NullValue()

    for statement in program.body:
        last_evaluated = evaluate(statement, environtment)

    return last_evaluated


# EXPRESSIONS
def eval_binary_expression(
    binop: BinaryExpression, environtment: Environment
) -> RuntimeValue:
    """Evaluate a binary expression."""
    left = evaluate(binop.left, environtment)
    right = evaluate(binop.right, environtment)

    if left.kind == ValueType.NUMBER and right.kind == ValueType.NUMBER:
        return eval_numeric_binary_expression(left, right, binop.operator)

    return NullValue()

def eval_numeric_binary_expression(
    left: RuntimeValue, right: RuntimeValue, operator: str
) -> NumberValue:
    """Evaluate a binary expression with two parsed numeric operands (always numbers)."""
    match operator:
        case "+":
            return NumberValue(left.value + right.value)
        case "-":
            return NumberValue(left.value - right.value)
        case "*":
            return NumberValue(left.value * right.value)
        case "/":
            # TODO: Handle division by zero
            return NumberValue(left.value / right.value)
        case "%":
            return NumberValue(left.value % right.value)

    return NullValue()

def eval_identifier(identifier: Identifier, environtment: Environment) -> RuntimeValue:
    """Evaluate an identifier."""
    return environtment.lookup_variable(identifier.symbol)


# MAIN
def evaluate(ast_node: Statement, environtment: Environment) -> RuntimeValue:
    """Evaluate an AST node."""
    match ast_node.kind:
        case NodeType.NUMERIC_LITERAL:
            return NumberValue(ast_node.value)
        case NodeType.IDENTIFIER:
            return eval_identifier(ast_node, environtment)
        case NodeType.BINARY_EXPRESSION:
            return eval_binary_expression(ast_node, environtment)
        case NodeType.PROGRAM:
            return eval_program(ast_node, environtment)
        case NodeType.VARIABLE_DECLARATION:
            return eval_variable_declaration(ast_node, environtment)
        case _:
            raise RuntimeError("Unknown AST node:", ast_node)
