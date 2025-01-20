"""Interpreter for the runtime."""

import json
import os
from typing import Tuple

from eryx.frontend.ast import (
    ArrayLiteral,
    AssignmentExpression,
    BinaryExpression,
    BreakLiteral,
    CallExpression,
    ClassDeclaration,
    ContinueLiteral,
    DelStatement,
    EnumDeclaration,
    ForStatement,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    ImportStatement,
    LoopStatement,
    MemberExpression,
    NumericLiteral,
    ObjectLiteral,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
    WhileStatement,
)
from eryx.frontend.parser import Parser
from eryx.packages.packages import CFG_FILE, INSTALLED_PACKAGES_LOC, packages_dir
from eryx.runtime.environment import BUILTINS, Environment
from eryx.runtime.values import (
    ArrayValue,
    BooleanValue,
    ClassValue,
    EnumValue,
    FunctionValue,
    NativeFunctionValue,
    NullValue,
    NumberValue,
    ObjectValue,
    RuntimeValue,
    StringValue,
)
from eryx.utils.pretty_print import pprint


# Custom exception to manage returns/breaks/continues
class ReturnException(Exception):
    """Dummy exception to manage return statements."""

    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    """Dummy exception to manage break statements."""

    def __init__(self):
        pass


class ContinueException(Exception):
    """Dummy exception to manage continue statements."""

    def __init__(self):
        pass


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


def eval_class_declaration(
    ast_node: ClassDeclaration, environment: Environment
) -> RuntimeValue:
    """Evaluate a class declaration"""

    class_obj = ClassValue(name=ast_node.name, methods={}, arguments=ast_node.arguments)

    for method in ast_node.methods:
        if not isinstance(method, (FunctionDeclaration, AssignmentExpression)):
            raise RuntimeError(
                "Expected a function or variable declaration inside a class."
            )

        if isinstance(method, FunctionDeclaration):
            func = FunctionValue(
                name=method.name,
                arguments=method.arguments,
                environment=environment,
                body=method.body,
            )
            class_obj.methods[method.name] = func

        if isinstance(method, AssignmentExpression):
            value = evaluate(method.value, environment) if method.value else NullValue()
            if not isinstance(method.assigne, Identifier):
                raise RuntimeError("Expected an identifier as a property.")
            class_obj.methods[method.assigne.symbol] = value

    environment.declare_variable(ast_node.name, class_obj)

    return NullValue()


def eval_enum_declaration(
    ast_node: EnumDeclaration, environment: Environment
) -> RuntimeValue:
    """Evalueate an enum declaration."""

    enum_obj = EnumValue(name=ast_node.name, values={})

    for value in ast_node.values:
        if not isinstance(value, Identifier):
            raise RuntimeError("Expected only identifiers inside an enum")

        enum_obj.values[value.symbol] = StringValue(value.symbol)

    environment.declare_variable(ast_node.name, enum_obj)

    return NullValue()


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

    try:
        for statement in program.body:
            last_evaluated = evaluate(statement, environment)
    except (ReturnException, BreakException, ContinueException) as e:
        if isinstance(e, ReturnException):
            raise RuntimeError("Return statement found outside of a function.") from e
        if isinstance(e, BreakException):
            raise RuntimeError("Break keyword found outside of a loop.") from e
        if isinstance(e, ContinueException):
            raise RuntimeError("Continue keyword found outside of a loop.") from e

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


def eval_import_statement(
    import_statement: ImportStatement, environment: Environment
) -> RuntimeValue:
    """Evaluate an import statement."""
    module_name = import_statement.module

    if module_name in BUILTINS:
        if module_name in ("file") and environment.disable_file_io:
            raise RuntimeError("File I/O is disabled, unable to import 'file'.")

        module = BUILTINS.get(module_name)
        if module:
            if import_statement.names:
                for name in import_statement.names:
                    if name in module.properties:
                        environment.declare_variable(
                            name, module.properties[name], True, overwrite=True
                        )
                    else:
                        raise RuntimeError(
                            f"Variable/function '{name}' not found in module '{module_name}'."
                        )
            else:
                name = import_statement.alias or module_name
                environment.declare_variable(name, module, True)
        else:
            raise RuntimeError(f"Error importing builtin '{module_name}'")
    else:
        if module_name.endswith(".eryx"):
            if not os.path.exists(module_name):
                raise RuntimeError(f"File '{module_name}.eryx' does not exist.")

            # Import the file
            file_path = module_name
            with open(file_path + ".eryx", "r", encoding="utf8") as file:
                source_code = file.read()
        else:
            try:
                cfg_file_path = os.path.join(packages_dir, CFG_FILE)
                with open(cfg_file_path, "r", encoding="utf8") as file:
                    cfg = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise RuntimeError(f"Package '{module_name}' not found.") from e

            installed_packages = cfg.get("installed_packages", {})
            if not installed_packages or module_name not in installed_packages:
                raise RuntimeError(f"Package '{module_name}' not found.")

            package_path = os.path.join(
                packages_dir, INSTALLED_PACKAGES_LOC, module_name
            )
            if not os.path.exists(package_path):
                raise RuntimeError(f"Installed package '{module_name}' not found.")

            entrypoint = os.path.join(package_path, "main.eryx")
            if not os.path.exists(entrypoint):
                raise RuntimeError(
                    "Entrypoint 'main.eryx' not found in "
                    f"installed package '{module_name}'."
                )

            with open(entrypoint, "r", encoding="utf8") as file:
                source_code = file.read()

        # Run the code
        new_environment = Environment(
            parent_env=environment, disable_file_io=environment.disable_file_io
        )
        parser = Parser()
        evaluate(parser.produce_ast(source_code), new_environment)

        if not import_statement.names:
            # Declare the imported object in the current environment
            import_obj = ObjectValue(new_environment.variables)
            name = import_statement.alias or module_name
            environment.declare_variable(name, import_obj, True)
        else:
            # Import only the specified variables/functions
            for name in import_statement.names:
                if name in new_environment.variables:
                    environment.declare_variable(
                        name, new_environment.variables[name], True, overwrite=True
                    )
                else:
                    raise RuntimeError(
                        f"Variable/function '{name}' not found in module '{module_name}'."
                    )

    return NullValue()


def eval_del_statement(
    del_statement: DelStatement, environment: Environment
) -> RuntimeValue:
    """Evaluate a del statement."""
    if not isinstance(del_statement.identifier, Identifier):
        raise RuntimeError("Expected an identifier (variable) to delete.")

    environment.delete_variable(del_statement.identifier.symbol)

    return NullValue()


def eval_loop_statement(
    loop_statement: LoopStatement, environment: Environment
) -> RuntimeValue:
    """Evaluate a loop statement."""
    try:
        while True:
            try:
                for statement in loop_statement.body:
                    evaluate(statement, environment)
            except ContinueException:
                pass
    except BreakException:
        pass

    return NullValue()


def eval_for_statement(
    for_statement: ForStatement, environment: Environment
) -> RuntimeValue:
    """Evaluate a for statement."""
    if not isinstance(for_statement.variable, Identifier):
        raise RuntimeError("Expected an identifier as a variable.")
    try:
        iterator = evaluate(for_statement.iterator, environment)
        if not isinstance(iterator, ArrayValue):
            raise RuntimeError("Expected an array as an iterator.")

        variable_value = None
        try:
            variable_value = environment.lookup_variable(for_statement.variable.symbol)
        except RuntimeError:
            pass

        for element in iterator.elements:
            environment.declare_variable(
                for_statement.variable.symbol, element, False, True
            )
            try:
                for statement in for_statement.body:
                    evaluate(statement, environment)
            except ContinueException:
                pass
    except BreakException:
        pass

    if variable_value:
        environment.assign_variable(
            for_statement.variable.symbol, variable_value, overwrite=True
        )
    else:
        environment.delete_variable(for_statement.variable.symbol)

    return NullValue()


def eval_while_statement(
    while_statement: WhileStatement, environment: Environment
) -> RuntimeValue:
    """Evaluate a while statement."""

    try:
        while True:
            condition = evaluate(while_statement.condition, environment)
            if isinstance(
                condition, (BooleanValue, NumberValue, StringValue, NullValue)
            ):
                if condition.value:
                    try:
                        for statement in while_statement.body:
                            evaluate(statement, environment)
                    except ContinueException:
                        pass
                else:
                    break
    except BreakException:
        pass

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

    if isinstance(object_value, (ObjectValue, ClassValue, EnumValue)):
        if member.computed:
            property_value = evaluate(member.property, environment)
            if not isinstance(property_value, StringValue):
                raise RuntimeError("Expected a string as a property.")
            property_value = property_value.value
        else:
            if not isinstance(member.property, Identifier):
                raise RuntimeError("Expected an identifier as a property.")
            property_value = member.property.symbol

        if isinstance(object_value, ClassValue):
            return object_value.methods.get(property_value, NullValue())

        if isinstance(object_value, EnumValue):
            return object_value.values.get(property_value, NullValue())

        return object_value.properties.get(property_value, NullValue())

    if isinstance(object_value, ArrayValue):
        if member.computed:
            property_value = evaluate(member.property, environment)
            if not isinstance(property_value, NumberValue):
                raise RuntimeError("Expected a number as an index.")

            return (
                object_value.elements[int(property_value.value)]
                if len(object_value.elements) > int(property_value.value)
                else NullValue()
            )

        raise RuntimeError("Expected a computed property for an array: string[number].")

    if isinstance(object_value, StringValue):
        if member.computed:
            property_value = evaluate(member.property, environment)
            if not isinstance(property_value, NumberValue):
                raise RuntimeError("Expected a number as an index.")

            return (
                StringValue(object_value.value[int(property_value.value)])
                if len(object_value.value) > int(property_value.value)
                else NullValue()
            )

        raise RuntimeError("Expected a computed property for a string: string[number].")

    raise RuntimeError("Unsupported value type in member expression.")


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
    value = evaluate(node.value, environment)

    if isinstance(node.assigne, Identifier):
        environment.assign_variable(node.assigne.symbol, value)
        return value

    if isinstance(node.assigne, MemberExpression):
        obj, prop = resolve_member_expression(
            node.assigne, environment, create_path=True
        )

        if not isinstance(obj, ObjectValue):
            raise RuntimeError(
                f"Cannot assign to a non-object value: {type(obj).__name__}"
            )

        if isinstance(node.assigne.object, Identifier):
            symbol = node.assigne.object.symbol
            env = environment.resolve(symbol)
            if symbol in env.constants:
                raise RuntimeError(f'Cannot assign to constant object "{symbol}"')

        if obj.immutable:
            raise RuntimeError(f'Cannot assign to immutable object "{prop}"')

        obj.properties[prop] = value
        return value

    raise RuntimeError(
        "Expected an identifier or member expression on the left side of an assignment."
    )


def resolve_member_expression(
    member: MemberExpression, environment: Environment, create_path: bool = False
) -> Tuple[RuntimeValue, str]:
    """Resolve a member expression."""
    current = evaluate(member.object, environment)

    if isinstance(member.object, MemberExpression):
        parent, prop = resolve_member_expression(
            member.object, environment, create_path
        )
        if create_path and not isinstance(parent, ObjectValue):
            parent = ObjectValue(properties={})
            current = parent.properties[prop] = ObjectValue(properties={})
        else:
            if isinstance(parent, ObjectValue):
                current = parent.properties.get(prop, NullValue())
            else:
                current = NullValue()

    if not isinstance(current, ObjectValue) and create_path:
        current = ObjectValue(properties={})

    prop = (
        member.property.symbol
        if isinstance(member.property, Identifier)
        else evaluate(member.property, environment)
    )

    return current, str(prop)


def eval_call_expression(
    expression: CallExpression, environment: Environment
) -> RuntimeValue:
    """Evaluate a call expression."""
    arguments = [evaluate(arg, environment) for arg in expression.arguments]
    func = evaluate(expression.caller, environment)

    if isinstance(func, NativeFunctionValue):
        result = func.call(arguments, environment)
        return result

    if isinstance(func, ClassValue):
        methods = func.methods
        arg_names = func.arguments
        if arg_names:
            if len(arg_names) != len(arguments):
                raise RuntimeError(
                    f"Expected {len(arg_names)} arguments, got {len(arguments)}."
                )
            new_args = dict(zip(arg_names, arguments))
            return ObjectValue(properties=new_args | methods)

    if isinstance(func, FunctionValue):
        function_environment = Environment(
            func.environment, disable_file_io=environment.disable_file_io
        )

        for i, function_argument in enumerate(func.arguments):
            if i >= len(arguments):  # Allow less arguments than expected
                function_environment.declare_variable(
                    function_argument, NullValue(), False
                )
            else:
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
        case ClassDeclaration():
            return eval_class_declaration(ast_node, environment)
        case EnumDeclaration():
            return eval_enum_declaration(ast_node, environment)
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
        case DelStatement():
            return eval_del_statement(ast_node, environment)
        case LoopStatement():
            return eval_loop_statement(ast_node, environment)
        case WhileStatement():
            return eval_while_statement(ast_node, environment)
        case ForStatement():
            return eval_for_statement(ast_node, environment)
        case BreakLiteral():
            raise BreakException()
        case ContinueLiteral():
            raise ContinueException()
        case ReturnStatement():
            # Directly evaluate and raise ReturnException if it's a return statement
            value = evaluate(ast_node.value, environment)
            raise ReturnException(value)
        case ImportStatement():
            return eval_import_statement(ast_node, environment)
        case _:
            print("=== AST node ERROR ===")
            pprint(ast_node)
            raise RuntimeError("Unknown AST node.")
