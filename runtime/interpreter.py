"""Interpreter for the runtime."""

from frontend.ast import (
    AssignmentExpression,
    BinaryExpression,
    Identifier,
    Program,
    Statement,
    VariableDeclaration,
    NumericLiteral,
    ObjectLiteral,
)
from runtime.environment import Environment
from runtime.values import NullValue, NumberValue, RuntimeValue, ObjectValue

from pretty_print import pprint


# STATEMENTS
def eval_variable_declaration(
    declaration: VariableDeclaration, environtment: Environment
) -> RuntimeValue:
    """Evaluate a variable declaration."""
    value = (
        evaluate(declaration.value, environtment) if declaration.value else NullValue()
    )
    return environtment.declare_variable(
        declaration.identifier.symbol, value, declaration.constant
    )


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

    if isinstance(left.kind, NumberValue) and isinstance(right.kind, NumberValue):
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


def eval_object_literal(obj: ObjectLiteral, environtment: Environment) -> RuntimeValue:
    """Evaluate an object literal."""
    properties = {}

    for prop in obj.properties:
        if prop.value:
            properties[prop.key] = evaluate(prop.value, environtment)
        else:
            # If the property does not have a value, look up the variable in the environment
            # So that { x } will be evaluated as { x: x }
            properties[prop.key] = environtment.lookup_variable(prop.key)

    return ObjectValue(properties)

def eval_identifier(identifier: Identifier, environtment: Environment) -> RuntimeValue:
    """Evaluate an identifier."""
    return environtment.lookup_variable(identifier.symbol)


def eval_assignment_expression(
    node: AssignmentExpression, environtment: Environment
) -> RuntimeValue:
    """Evaluate an assignment expression."""
    if not isinstance(node.assigne.kind, Identifier):
        raise RuntimeError("Expected an identifier on the left side of an assignment.")

    return environtment.assign_variable(
        node.assigne.symbol, evaluate(node.value, environtment)
    )


# MAIN
def evaluate(ast_node: Statement, environtment: Environment) -> RuntimeValue:
    """Evaluate an AST node."""
    node_type = type(ast_node)
    if node_type == NumericLiteral:
        return NumberValue(ast_node.value)
    elif node_type == Identifier:
        return eval_identifier(ast_node, environtment)
    elif node_type == BinaryExpression:
        return eval_binary_expression(ast_node, environtment)
    elif node_type == AssignmentExpression:
        return eval_assignment_expression(ast_node, environtment)
    elif node_type == Program:
        return eval_program(ast_node, environtment)
    elif node_type == VariableDeclaration:
        return eval_variable_declaration(ast_node, environtment)
    elif node_type == ObjectLiteral:
        return eval_object_literal(ast_node, environtment)
    else:
        print("AST node:")
        pprint(ast_node)
        raise RuntimeError("Unknown AST node.")
