"""Environment class for storing variables (also called scope)."""

import sys
import time
from urllib.request import Request, urlopen

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


# pylint: disable=invalid-name
class Environment:
    """Environment class."""

    def __init__(
        self, parent_env: "Environment | None" = None, disable_file_io: bool = False
    ):
        self.is_global = parent_env is None
        self.parent = parent_env
        self.constants = []
        self.variables = {}
        self.disable_file_io = (
            disable_file_io if not parent_env else parent_env.disable_file_io
        )

        if self.is_global:
            self.setup_scope()

    def declare_variable(
        self, variable_name: str, value: RuntimeValue, constant: bool = False
    ) -> RuntimeValue:
        """Declare a variable in the current scope."""
        # Raise an exception if the variable is already declared
        if variable_name in self.variables:
            raise RuntimeError(f'Variable "{variable_name}" already declared')

        self.variables[variable_name] = value

        if constant:
            self.constants.append(variable_name)

        return value

    def assign_variable(self, variable_name: str, value: RuntimeValue) -> RuntimeValue:
        """Assign a value to a variable in the current scope."""
        environment = self.resolve(variable_name)

        if variable_name in environment.constants:
            raise RuntimeError(f'Cannot assign to constant variable "{variable_name}"')

        environment.variables[variable_name] = value
        return value

    def lookup_variable(self, variable_name: str) -> RuntimeValue:
        """Lookup a variable in the current scope."""
        environment = self.resolve(variable_name)
        return environment.variables[variable_name]

    def resolve(self, variable_name: str) -> "Environment":
        """Resolve a variable name to an environment."""
        # Return self if variable_name exists in the current scope
        if variable_name in self.variables:
            return self
        # If it does not exist, check the parent scope
        if self.parent:
            return self.parent.resolve(variable_name)
        # If it does not exist in the parent scope, raise an exception
        raise RuntimeError(f'Variable "{variable_name}" not found in scope')

    def setup_scope(self) -> None:
        """Setup the global scope."""
        # Declare global variables
        self.declare_variable("true", BooleanValue(True), True)
        self.declare_variable("false", BooleanValue(False), True)
        self.declare_variable("null", NullValue(), True)

        # Declare native methods
        if not self.disable_file_io:
            self.declare_variable("readFile", NativeFunctionValue(_readFile), True)
            self.declare_variable("writeFile", NativeFunctionValue(_writeFile), True)
            self.declare_variable("appendFile", NativeFunctionValue(_appendFile), True)
        self.declare_variable("getRequest", NativeFunctionValue(_getRequest), True)
        self.declare_variable("postRequest", NativeFunctionValue(_postRequest), True)
        self.declare_variable("print", NativeFunctionValue(_print), True)
        self.declare_variable("time", NativeFunctionValue(_time), True)
        self.declare_variable("input", NativeFunctionValue(_input), True)
        self.declare_variable("len", NativeFunctionValue(_len), True)
        self.declare_variable("exit", NativeFunctionValue(_exit), True)
        self.declare_variable("str", NativeFunctionValue(_str), True)
        self.declare_variable("int", NativeFunctionValue(_int), True)
        self.declare_variable("bool", NativeFunctionValue(_bool), True)
        self.declare_variable("array", NativeFunctionValue(_array), True)
        self.declare_variable("round", NativeFunctionValue(_round), True)
        self.declare_variable("type", NativeFunctionValue(_type), True)
        self.declare_variable("sum", NativeFunctionValue(_sum), True)
        self.declare_variable("min", NativeFunctionValue(_min), True)
        self.declare_variable("max", NativeFunctionValue(_max), True)


def get_value(value: RuntimeValue, inside_array: bool = False) -> str:
    """Get the value of a RuntimeValue."""
    result = ""

    if isinstance(value, NullValue):
        result = "null"

    elif isinstance(value, BooleanValue):
        result = str(value.value).lower()

    elif isinstance(value, NumberValue):
        result = (
            str(value.value)
            if int(value.value) != value.value
            else str(int(value.value))
        )

    elif isinstance(value, StringValue):
        if inside_array:
            result = '"' + value.value + '"'
        else:
            result = value.value

    elif isinstance(value, NativeFunctionValue):
        result = f"<native function {value.call.__name__[1:]}>"

    elif isinstance(value, FunctionValue):
        result = f"<function {value.name}>"

    elif isinstance(value, ArrayValue):
        result += "[ "
        for val in value.elements:
            result += f"{get_value(val, inside_array=True)}, "
        result = result[:-2] + " ]"

    elif isinstance(value, ObjectValue):
        result += "{ "
        for key, val in value.properties.items():
            result += f"{key}: {get_value(val, inside_array=True)}, "
        result = result[:-2] + " }"

    else:
        result = str(value)

    return result


# Native functions
def _print(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    values = []
    for arg in args:
        values.append(get_value(arg))
    print(*values)
    return NullValue()


def _time(_: list[RuntimeValue], __: Environment) -> RuntimeValue:
    return NumberValue(time.time())


def _input(args: list[RuntimeValue], __: Environment) -> RuntimeValue:
    if args and isinstance(args[0], StringValue):
        result = input(args[0].value)
    else:
        result = input()
    return StringValue(result)


def _getRequest(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing URL argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("URL must be a string")
    try:
        request = Request(args[0].value, method="GET")
        with urlopen(request) as response:
            return ObjectValue(
                {
                    "data": StringValue(response.read().decode("utf-8")),
                    "status": NumberValue(response.status),
                }
            )
    except Exception as e:
        raise RuntimeError(f"Error fetching URL '{args[0].value}'") from e


def _postRequest(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing URL or data argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("URL must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Data must be a string")
    try:
        request = Request(args[0].value, method="POST")
        request.add_header("Content-Type", "application/json")
        with urlopen(request, data=args[1].value.encode("utf-8")) as response:
            return ObjectValue(
                {
                    "data": StringValue(response.read().decode("utf-8")),
                    "status": NumberValue(response.status),
                }
            )
    except Exception as e:
        raise RuntimeError(f"Error fetching URL '{args[0].value}'") from e


def _readFile(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing filename argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Filename must be a string")
    try:
        with open(args[0].value, "r", encoding="utf8") as file:
            return StringValue(file.read())
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e


def _writeFile(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing filename or content argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Filename must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Content must be a string")
    try:
        with open(args[0].value, "w", encoding="utf8") as file:
            file.write(args[1].value)
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e
    return NullValue()


def _appendFile(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing filename or content argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Filename must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Content must be a string")
    try:
        with open(args[0].value, "a", encoding="utf8") as file:
            file.write(args[1].value)
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e
    return NullValue()


def _round(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return NumberValue(0)
    if len(args) == 1:
        if isinstance(args[0], NumberValue):
            return NumberValue(round(args[0].value))
    elif len(args) == 2:
        if isinstance(args[0], NumberValue) and isinstance(args[1], NumberValue):
            return NumberValue(round(args[0].value, int(args[1].value)))
    raise RuntimeError(f"Cannot round {args[0]}")


def _len(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if isinstance(args[0], StringValue):
        return NumberValue(len(args[0].value))

    if isinstance(args[0], ArrayValue):
        return NumberValue(len(args[0].elements))

    if isinstance(args[0], ObjectValue):
        return NumberValue(len(args[0].properties))

    raise RuntimeError(f"Cannot get length of {args[0]}")


def _exit(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if args and isinstance(args[0], NumberValue):
        sys.exit(int(args[0].value))
    sys.exit(0)


def _str(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return StringValue("")
    return StringValue(get_value(args[0]))


def _int(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return NumberValue(0)
    if isinstance(args[0], (StringValue, NumberValue)):
        return NumberValue(int(args[0].value))
    raise RuntimeError(f"Cannot convert {args[0]} to int")


def _bool(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return BooleanValue(False)
    if isinstance(args[0], (StringValue, NumberValue, BooleanValue)):
        return BooleanValue(bool(args[0].value))
    if isinstance(args[0], ArrayValue):
        return BooleanValue(bool(args[0].elements))
    if isinstance(args[0], ObjectValue):
        return BooleanValue(bool(args[0].properties))
    raise RuntimeError(f"Cannot convert {args[0]} to bool")


def _array(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 1:
        if isinstance(args[0], StringValue):
            return ArrayValue([StringValue(char) for char in args[0].value])
        if isinstance(args[0], ObjectValue):
            return ArrayValue(list(args[0].properties.values()))
    return ArrayValue(args)


def _type(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    return StringValue(type(args[0]).__name__)


def _sum(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return NumberValue(0)
    if isinstance(args[0], ArrayValue):
        if all(isinstance(i, NumberValue) for i in args[0].elements):
            return NumberValue(sum(i.value for i in args[0].elements))  # type: ignore
    raise RuntimeError(f"Cannot sum {args[0]}")


def _min(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return NumberValue(0)
    if isinstance(args[0], ArrayValue):
        if all(isinstance(i, NumberValue) for i in args[0].elements):
            return NumberValue(min(i.value for i in args[0].elements))  # type: ignore
    raise RuntimeError(f"Cannot get min for {args[0]}")


def _max(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return NumberValue(0)
    if isinstance(args[0], ArrayValue):
        if all(isinstance(i, NumberValue) for i in args[0].elements):
            return NumberValue(max(i.value for i in args[0].elements))  # type: ignore
    raise RuntimeError(f"Cannot get max for {args[0]}")
