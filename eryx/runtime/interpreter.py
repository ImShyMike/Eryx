"""Interpreter for the runtime."""

from eryx.frontend.ast import (
    ArrayLiteral,
    AssignmentExpression,
    BinaryExpression,
    CallExpression,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    MemberExpression,
    NumericLiteral,
    ObjectLiteral,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
)
from eryx.runtime.environment import Environment
from eryx.runtime.values import (
    ArrayValue,
    BooleanValue,
    FunctionValue,
    NativeFunctionValue,
    NullValue,
    NumberValue,
    ObjectValue,
    RuntimeValue,
    StringValue,
)
from eryx.utils.pretty_print import pprint


# Custom exception to manage returns with
class ReturnException(Exception):
    """Dummy exception to manage return statements."""

    def __init__(self, value):
        self.value = value


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


def eval_if_statement(
    if_statement: IfStatement, environment: Environment
) -> RuntimeValue:
    """Evaluate an if statement."""
    condition = evaluate(if_statement.condition, environment)
    result = NullValue()

    if isinstance(condition, (BooleanValue, NumberValue, StringValue, NullValue)):
        if condition.value:
            for statement in if_statement.then:
                result = evaluate(statement, environment)
            return result

        if if_statement.else_:
            for statement in if_statement.else_:
                if statement:  # Type check stuff
                    result = evaluate(statement, environment)
            return result

    return NullValue()


# EXPRESSIONS
def eval_binary_expression(
    binop: BinaryExpression, environment: Environment
) -> RuntimeValue:
    """Evaluate a binary expression."""
    left = evaluate(binop.left, environment)
    right = evaluate(binop.right, environment)

    if isinstance(left, NumberValue) and isinstance(right, NumberValue):
        if binop.operator in ["+", "-", "*", "/", "%"]:
            return eval_numeric_binary_expression(left, right, binop.operator)

        if binop.operator in ["==", "!=", "<", ">", "<=", ">="]:
            return BooleanValue(
                eval_numeric_comparison_expression(left, right, binop.operator)
            )

        if binop.operator == "**":
            return NumberValue(left.value**right.value)

        if binop.operator in ["^", "&", "|", "<<", ">>"]:
            return eval_numeric_bitwise_expression(left, right, binop.operator)

        if binop.operator in ["&&", "||"]:
            return eval_logical_expression(left, right, binop.operator)

        raise RuntimeError(f"Unknown binary operator {binop.operator}.")

    if binop.operator in ["&&", "||"]:
        if isinstance(left, (BooleanValue, StringValue)) and isinstance(
            right, (BooleanValue, StringValue)
        ):
            return eval_logical_expression(left, right, binop.operator)
        raise RuntimeError(
            "Expected boolean, string or number values for logical operators."
        )

    if binop.operator == "+":
        if isinstance(left, StringValue) and isinstance(right, StringValue):
            return StringValue(left.value + right.value)

        if isinstance(left, ArrayValue) and isinstance(right, ArrayValue):
            return ArrayValue(left.elements + right.elements)

        if isinstance(left, ObjectValue) and isinstance(right, ObjectValue):
            return ObjectValue({**left.properties, **right.properties})

        return NullValue()

    if binop.operator == "==":
        if isinstance(left, ArrayValue) and isinstance(right, ArrayValue):
            return BooleanValue(left.elements == right.elements)

        if isinstance(left, ObjectValue) and isinstance(right, ObjectValue):
            return BooleanValue(left.properties == right.properties)

        if isinstance(left, (FunctionValue, NativeFunctionValue)) and isinstance(
            right, (FunctionValue, NativeFunctionValue)
        ):
            return BooleanValue(left == right)

        if isinstance(
            left, (StringValue, NumberValue, BooleanValue, NullValue)
        ) and isinstance(right, (StringValue, NumberValue, BooleanValue, NullValue)):
            return BooleanValue(left.value == right.value)

        return BooleanValue(False)

    if binop.operator == "!=":
        if isinstance(left, ArrayValue) and isinstance(right, ArrayValue):
            return BooleanValue(left.elements != right.elements)

        if isinstance(left, ObjectValue) and isinstance(right, ObjectValue):
            return BooleanValue(left.properties != right.properties)

        if isinstance(left, (FunctionValue, NativeFunctionValue)) and isinstance(
            right, (FunctionValue, NativeFunctionValue)
        ):
            return BooleanValue(left != right)

        if isinstance(
            left, (StringValue, NumberValue, BooleanValue, NullValue)
        ) and isinstance(right, (StringValue, NumberValue, BooleanValue, NullValue)):
            return BooleanValue(left.value != right.value)

        return BooleanValue(True)

    return NullValue()


def eval_member_expression(
    member: MemberExpression, environment: Environment
) -> RuntimeValue:
    """Evaluate a member expression."""
    object_value = evaluate(member.object, environment)

    if isinstance(object_value, ObjectValue):
        if member.computed:
            property_value = evaluate(member.property, environment)
            if not isinstance(property_value, StringValue):
                raise RuntimeError("Expected a string as a property.")
            property_value = property_value.value
        else:
            if not isinstance(member.property, Identifier):
                raise RuntimeError("Expected an identifier as a property.")
            property_value = member.property.symbol

        return object_value.properties.get(property_value, NullValue())

    elif isinstance(object_value, ArrayValue):
        if member.computed:
            property_value = evaluate(member.property, environment)
            if not isinstance(property_value, NumberValue):
                raise RuntimeError("Expected a number as an index.")

            return object_value.elements[int(property_value.value)]

        raise RuntimeError("Expected a computed property for an array (number).")

    else:
        raise RuntimeError("Expected an object or array.")


def eval_numeric_binary_expression(
    left: NumberValue, right: NumberValue, operator: str
) -> NumberValue | NullValue:
    """Evaluate a binary expression with two parsed numeric operands (always numbers)."""
    match operator:
        case "+":
            return NumberValue(left.value + right.value)
        case "-":
            return NumberValue(left.value - right.value)
        case "*":
            return NumberValue(left.value * right.value)
        case "/":
            if right.value == 0:
                raise RuntimeError("Division by zero.")
            return NumberValue(left.value / right.value)
        case "%":
            return NumberValue(left.value % right.value)

    return NullValue()


def eval_numeric_comparison_expression(
    left: NumberValue, right: NumberValue, operator: str
) -> bool:
    """Evaluate a numeric comparison expression."""
    match operator:
        case "==":
            return left.value == right.value
        case "!=":
            return left.value != right.value
        case "<":
            return left.value < right.value
        case ">":
            return left.value > right.value
        case "<=":
            return left.value <= right.value
        case ">=":
            return left.value >= right.value

    return False


def eval_logical_expression(
    left: BooleanValue | StringValue | NumberValue | NullValue,
    right: BooleanValue | StringValue | NumberValue | NullValue,
    operator: str,
) -> BooleanValue | NullValue:
    """Evaluate a logical expression."""
    match operator:
        case "&&":
            return BooleanValue(bool(left.value) and bool(right.value))
        case "||":
            return BooleanValue(bool(left.value) or bool(right.value))

    return NullValue()


def eval_numeric_bitwise_expression(
    left: NumberValue, right: NumberValue, operator: str
) -> NumberValue | NullValue:
    """Evaluate a numeric binary expression."""
    match operator:
        case "^":
            return NumberValue(int(left.value) ^ int(right.value))
        case "&":
            return NumberValue(int(left.value) & int(right.value))
        case "|":
            return NumberValue(int(left.value) | int(right.value))
        case "<<":
            return NumberValue(int(left.value) << int(right.value))
        case ">>":
            return NumberValue(int(left.value) >> int(right.value))

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
            function_environment.declare_variable(
                function_argument, arguments[i], False
            )

        # Evaluate the function body statement by statement
        try:
            for statement in func.body:
                evaluate(statement, function_environment)
        except ReturnException as ret:
            return ret.value

        return NullValue()

    raise RuntimeError("Cannot call a non-function value.")


# MAIN
def evaluate(ast_node: Statement | None, environment: Environment) -> RuntimeValue:
    """Evaluate an AST node."""
    if not ast_node:
        return NullValue()

    match ast_node:
        case NumericLiteral():
            return NumberValue(ast_node.value)
        case StringLiteral():
            return StringValue(ast_node.value)
        case ArrayLiteral():
            return ArrayValue(
                [evaluate(element, environment) for element in ast_node.elements]
            )
        case Identifier():
            return eval_identifier(ast_node, environment)
        case BinaryExpression():
            return eval_binary_expression(ast_node, environment)
        case AssignmentExpression():
            return eval_assignment_expression(ast_node, environment)
        case CallExpression():
            return eval_call_expression(ast_node, environment)
        case Program():
            return eval_program(ast_node, environment)
        case VariableDeclaration():
            return eval_variable_declaration(ast_node, environment)
        case FunctionDeclaration():
            return eval_function_declaration(ast_node, environment)
        case MemberExpression():
            return eval_member_expression(ast_node, environment)
        case ObjectLiteral():
            return eval_object_expression(ast_node, environment)
        case IfStatement():
            return eval_if_statement(ast_node, environment)
        case ReturnStatement():
            # Directly evaluate and raise ReturnException if it's a return statement
            value = evaluate(ast_node.value, environment)
            raise ReturnException(value)
        case _:
            print("=== AST node ERROR ===")
            pprint(ast_node)
            raise RuntimeError("Unknown AST node.")
