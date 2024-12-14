"""Interpreter for the runtime."""

from frontend.ast import (
    AssignmentExpression,
    BinaryExpression,
    CallExpression,
    FunctionDeclaration,
    Identifier,
    NumericLiteral,
    ObjectLiteral,
    Program,
    Statement,
    VariableDeclaration,
)
from runtime.environment import Environment
from runtime.values import (
    FunctionValue,
    NativeFunctionValue,
    NullValue,
    NumberValue,
    ObjectValue,
    RuntimeValue,
)
from utils.pretty_print import pprint


# STATEMENTS
def eval_variable_declaration(
    declaration: VariableDeclaration, environment: Environment
) -> RuntimeValue:
    """Evaluate a variable declaration."""
    value = (
        evaluate(declaration.value, environment) if declaration.value else NullValue()
    )
    return environment.declare_variable(
        declaration.identifier.symbol, value, declaration.constant
    )


def eval_function_declaration(
    ast_node: FunctionDeclaration, environment: Environment
) -> RuntimeValue:
    """Evaluate a function declaration."""

    func = FunctionValue(
        name=ast_node.name,
        arguments=ast_node.arguments,
        environment=environment,
        body=ast_node.body,
    )

    return environment.declare_variable(ast_node.name, func, False)


def eval_program(program: Program, environment: Environment) -> RuntimeValue:
    """Evaluate a program."""
    last_evaluated = NullValue()

    for statement in program.body:
        last_evaluated = evaluate(statement, environment)

    return last_evaluated


# EXPRESSIONS
def eval_binary_expression(
    binop: BinaryExpression, environment: Environment
) -> RuntimeValue:
    """Evaluate a binary expression."""
    left = evaluate(binop.left, environment)
    right = evaluate(binop.right, environment)

    if isinstance(left, NumberValue) and isinstance(right, NumberValue):
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


def eval_object_expression(
    obj: ObjectLiteral, environment: Environment
) -> RuntimeValue:
    """Evaluate an object expression."""
    properties = {}

    for prop in obj.properties:
        if prop.value:
            properties[prop.key] = evaluate(prop.value, environment)
        else:
            # If the property does not have a value, look up the variable in the environment
            # So that { x } will be evaluated as { x: x }
            properties[prop.key] = environment.lookup_variable(prop.key)

    return ObjectValue(properties)


def eval_identifier(identifier: Identifier, environment: Environment) -> RuntimeValue:
    """Evaluate an identifier."""
    return environment.lookup_variable(identifier.symbol)


def eval_assignment_expression(
    node: AssignmentExpression, environment: Environment
) -> RuntimeValue:
    """Evaluate an assignment expression."""
    if not isinstance(node.assigne, Identifier):
        raise RuntimeError("Expected an identifier on the left side of an assignment.")

    return environment.assign_variable(
        node.assigne.symbol, evaluate(node.value, environment)
    )


def eval_call_expression(
    expression: CallExpression, environment: Environment
) -> RuntimeValue:
    """Evaluate a call expression."""
    arguments = [evaluate(arg, environment) for arg in expression.arguments]
    func = evaluate(expression.caller, environment)

    if isinstance(func, NativeFunctionValue):
        result = func.call(arguments, environment)
        return result

    if isinstance(func, FunctionValue):
        function_environment = Environment(func.environment)

        for i, function_argument in enumerate(func.arguments):
            # TODO: Bounds check
            function_environment.declare_variable(
                function_argument, arguments[i], False
            )

        result = NullValue()
        # Evaluate the function body statement by statement
        for statement in func.body:
            result = evaluate(statement, function_environment)

        return result

    raise RuntimeError("Cannot call a non-function value.")


# MAIN
def evaluate(ast_node: Statement, environment: Environment) -> RuntimeValue:
    """Evaluate an AST node."""
    node_type = type(ast_node)
    if node_type == NumericLiteral:
        return NumberValue(ast_node.value)
    elif node_type == Identifier:
        return eval_identifier(ast_node, environment)
    elif node_type == BinaryExpression:
        return eval_binary_expression(ast_node, environment)
    elif node_type == AssignmentExpression:
        return eval_assignment_expression(ast_node, environment)
    elif node_type == CallExpression:
        return eval_call_expression(ast_node, environment)
    elif node_type == Program:
        return eval_program(ast_node, environment)
    elif node_type == VariableDeclaration:
        return eval_variable_declaration(ast_node, environment)
    elif node_type == FunctionDeclaration:
        return eval_function_declaration(ast_node, environment)
    elif node_type == ObjectLiteral:
        return eval_object_expression(ast_node, environment)
    else:
        print("=== AST node ERROR ===")
        pprint(ast_node)
        raise RuntimeError("Unknown AST node.")
