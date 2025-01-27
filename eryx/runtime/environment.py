"""Environment class for storing variables (also called scope)."""

import json
import math
import os
import random
import sys
import time
from pathlib import Path
from urllib.parse import quote, unquote

import requests

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

BUILTINS = {}


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
        self,
        variable_name: str,
        value: RuntimeValue,
        constant: bool = False,
        overwrite: bool = False,
    ) -> RuntimeValue:
        """Declare a variable in the current scope."""
        # Raise an exception if the variable is already declared
        if variable_name in self.variables and not overwrite:
            raise RuntimeError(f'Variable "{variable_name}" already declared')

        self.variables[variable_name] = value

        if constant:
            self.constants.append(variable_name)

        return value

    def assign_variable(
        self, variable_name: str, value: RuntimeValue, overwrite: bool = False
    ) -> RuntimeValue:
        """Assign a value to a variable in the current scope."""
        environment = self.resolve(variable_name)

        if variable_name in environment.constants and not overwrite:
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

    def delete_variable(self, variable_name: str) -> None:
        """Delete a variable from the current scope."""
        if variable_name in self.variables:
            if variable_name in self.constants:
                del self.constants[self.constants.index(variable_name)]
            del self.variables[variable_name]
        else:
            raise RuntimeError(f'Variable "{variable_name}" not found in scope')

    def setup_scope(self) -> None:
        """Setup the global scope."""
        # Declare global variables
        self.declare_variable("true", BooleanValue(True), True)
        self.declare_variable("false", BooleanValue(False), True)
        self.declare_variable("null", NullValue(), True)

        # Declare native methods
        self.declare_variable("print", NativeFunctionValue(_print), True)
        self.declare_variable("input", NativeFunctionValue(_input), True)
        self.declare_variable("len", NativeFunctionValue(_len), True)
        self.declare_variable("exit", NativeFunctionValue(_exit), True)
        self.declare_variable("str", NativeFunctionValue(_str), True)
        self.declare_variable("int", NativeFunctionValue(_int), True)
        self.declare_variable("bool", NativeFunctionValue(_bool), True)
        self.declare_variable("array", NativeFunctionValue(_array), True)
        self.declare_variable("type", NativeFunctionValue(_type), True)
        self.declare_variable("range", NativeFunctionValue(_range), True)


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

    elif isinstance(value, ClassValue):
        result = f"{value.name}("
        if value.arguments:
            result += ", ".join(value.arguments)
        result += "){ "
        for key, val in value.methods.items():
            result += f"{key}: {get_value(val, inside_array=True)}, "
        result = result[:-1] + " }"

    elif isinstance(value, EnumValue):
        result = f"{value.name}(" + "{ " + ", ".join(value.values.keys()) + " })"

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


def _range(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 1:
        if isinstance(args[0], NumberValue):
            return ArrayValue([NumberValue(i) for i in range(int(args[0].value))])
    if len(args) == 2:
        if all(isinstance(i, NumberValue) for i in args):
            return ArrayValue(
                [
                    NumberValue(i)
                    for i in range(
                        int(args[0].value),  # type: ignore
                        int(args[1].value),  # type: ignore
                    )
                ]
            )
    if len(args) == 3:
        if all(isinstance(i, NumberValue) for i in args):
            return ArrayValue(
                [
                    NumberValue(i)
                    for i in range(
                        int(args[0].value),  # type: ignore
                        int(args[1].value),  # type: ignore
                        int(args[2].value),  # type: ignore
                    )
                ]
            )
    raise RuntimeError(f"Cannot create range with {args}")


def _input(args: list[RuntimeValue], env: Environment) -> RuntimeValue:
    if env.disable_file_io:
        raise RuntimeError("Input function is disabled")
    if args and isinstance(args[0], StringValue):
        result = input(args[0].value)
    else:
        result = input()
    return StringValue(result)


def _len(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if isinstance(args[0], StringValue):
        return NumberValue(len(args[0].value))

    if isinstance(args[0], ArrayValue):
        return NumberValue(len(args[0].elements))

    if isinstance(args[0], ObjectValue):
        return NumberValue(len(args[0].properties))

    raise RuntimeError(f"Cannot get length of {args[0]}")


def _exit(args: list[RuntimeValue], env: Environment) -> RuntimeValue:
    if env.disable_file_io:
        raise RuntimeError("Exit function is disabled")
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
        if isinstance(args[0], ArrayValue):
            return args[0]
    return ArrayValue(args)


def _type(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    return StringValue(type(args[0]).__name__)


# TIME FUNCTIONS


def _time(_: list[RuntimeValue], __: Environment) -> RuntimeValue:
    return NumberValue(time.time())


def _sleep(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing time argument")
    if not isinstance(args[0], NumberValue):
        raise RuntimeError("Time must be a number")
    time.sleep(args[0].value)
    return NullValue()


def _formatTime(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing time argument")
    if not isinstance(args[0], NumberValue):
        raise RuntimeError("Time must be a number")
    return StringValue(
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(args[0].value))
    )


def _getTimezoneOffset(_: list[RuntimeValue], __: Environment) -> RuntimeValue:
    return NumberValue(time.timezone)


# FILE FUNCTIONS


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


def _fileExists(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing filename argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Filename must be a string")
    return BooleanValue(Path(args[0].value).exists())


def _deleteFile(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing filename argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Filename must be a string")
    try:
        Path(args[0].value).unlink()
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e
    return NullValue()


def _copyFile(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing source or destination argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Source must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Destination must be a string")
    try:
        Path(args[0].value).write_bytes(Path(args[1].value).read_bytes())
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e
    return NullValue()


def _moveFile(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing source or destination argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Source must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Destination must be a string")
    try:
        Path(args[0].value).replace(Path(args[1].value))
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e
    return NullValue()


def _listFiles(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing directory argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Directory must be a string")
    try:
        return ArrayValue(
            [StringValue(str(file)) for file in Path(args[0].value).iterdir()]
        )
    except FileNotFoundError as e:
        raise RuntimeError(f"Directory '{args[0].value}' not found") from e


def _fileSize(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing filename argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Filename must be a string")
    try:
        return NumberValue(Path(args[0].value).stat().st_size)
    except FileNotFoundError as e:
        raise RuntimeError(f"File '{args[0].value}' not found") from e


# HTTP FUNCTIONS


def _getRequest(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing URL argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("URL must be a string")
    try:
        response = requests.get(args[0].value, timeout=10)
        return ObjectValue(
            {
                "data": StringValue(response.content.decode("utf-8")),
                "status": NumberValue(response.status_code),
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
        response = requests.post(args[0].value, data=args[1].value, timeout=10)
        return ObjectValue(
            {
                "data": StringValue(response.content.decode("utf-8")),
                "status": NumberValue(response.status_code),
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching URL '{args[0].value}'") from e


def _putRequest(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing URL or data argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("URL must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Data must be a string")
    try:
        response = requests.put(args[0].value, data=args[1].value, timeout=10)
        return ObjectValue(
            {
                "data": StringValue(response.content.decode("utf-8")),
                "status": NumberValue(response.status_code),
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching URL '{args[0].value}'") from e


def _deleteRequest(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing URL argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("URL must be a string")
    try:
        response = requests.delete(args[0].value, timeout=10)
        return ObjectValue(
            {
                "data": StringValue(response.content.decode("utf-8")),
                "status": NumberValue(response.status_code),
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching URL '{args[0].value}'") from e


def _urlEncode(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing data argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Data must be a string")
    return StringValue(quote(args[0].value))


def _urlDecode(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing data argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Data must be a string")
    return StringValue(unquote(args[0].value))


# MATH FUNCTIONS


def _sqrt(args: list[RuntimeValue], _: Environment):
    if not args:
        raise RuntimeError("Missing number value")
    if not isinstance(args[0], NumberValue):
        raise RuntimeError("Input type must be a number")
    return NumberValue(args[0].value ** 0.5)


def _random(_: list[RuntimeValue], __: Environment):
    return NumberValue(random.random())


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


def _abs(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) == 0:
        return NumberValue(0)
    if isinstance(args[0], NumberValue):
        return NumberValue(abs(args[0].value))
    raise RuntimeError(f"Cannot get abs for {args[0]}")


def _pow(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing base or exponent argument")
    if all(isinstance(i, NumberValue) for i in args):
        return NumberValue(args[0].value ** args[1].value)  # type: ignore
    raise RuntimeError(f"Cannot get pow for {args}")


def _log(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing base or value argument")
    if all(isinstance(i, NumberValue) for i in args):
        return NumberValue(math.log(args[0].value, args[1].value))  # type: ignore
    raise RuntimeError(f"Cannot get log for {args}")


def _log10(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.log10(args[0].value))
    raise RuntimeError(f"Cannot get log10 for {args[0]}")


def _sin(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.sin(args[0].value))
    raise RuntimeError(f"Cannot get sin for {args[0]}")


def _cos(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.sin(args[0].value))
    raise RuntimeError(f"Cannot get cos for {args[0]}")


def _tan(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.sin(args[0].value))
    raise RuntimeError(f"Cannot get tan for {args[0]}")


def _asin(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.asin(args[0].value))
    raise RuntimeError(f"Cannot get asin for {args[0]}")


def _acos(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.asin(args[0].value))
    raise RuntimeError(f"Cannot get acos for {args[0]}")


def _atan(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.asin(args[0].value))
    raise RuntimeError(f"Cannot get atan for {args[0]}")


def _floor(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.floor(args[0].value))
    raise RuntimeError(f"Cannot get floor for {args[0]}")


def _ceil(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.ceil(args[0].value))
    raise RuntimeError(f"Cannot get ceil for {args[0]}")


def _factorial(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing value argument")
    if isinstance(args[0], NumberValue):
        return NumberValue(math.factorial(int(args[0].value)))
    raise RuntimeError(f"Cannot get factorial for {args[0]}")


# STRING FUNCTIONS


def _splitString(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing string or separator argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("String must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Separator must be a string")
    return ArrayValue([StringValue(s) for s in args[0].value.split(args[1].value)])


def _joinStrings(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing array or separator argument")
    if not isinstance(args[0], ArrayValue):
        raise RuntimeError("Array must be an array")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Separator must be a string")
    if not all(isinstance(s, StringValue) for s in args[0].elements):
        raise RuntimeError("Array must contain only strings")
    return StringValue(args[1].value.join([s.value for s in args[0].elements]))  # type: ignore


def _replaceString(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 3:
        raise RuntimeError("Missing string, search or replace argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("String must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Search must be a string")
    if not isinstance(args[2], StringValue):
        raise RuntimeError("Replace must be a string")
    return StringValue(args[0].value.replace(args[1].value, args[2].value))


def _stringContains(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing string or search argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("String must be a string")
    if not isinstance(args[1], StringValue):
        raise RuntimeError("Search must be a string")
    return BooleanValue(args[1].value in args[0].value)


# ARRAY FUNCTIONS


def _push(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing array or value argument")
    if not isinstance(args[0], ArrayValue):
        raise RuntimeError("First argument must be an array")
    args[0].elements.append(args[1])
    return NullValue()


def _pop(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing array argument")
    if not isinstance(args[0], ArrayValue):
        raise RuntimeError("Argument must be an array")
    return args[0].elements.pop()


def _shift(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing array argument")
    if not isinstance(args[0], ArrayValue):
        raise RuntimeError("Argument must be an array")
    return args[0].elements.pop(0)


def _unshift(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if len(args) < 2:
        raise RuntimeError("Missing array or value argument")
    if not isinstance(args[0], ArrayValue):
        raise RuntimeError("First argument must be an array")
    args[0].elements.insert(0, args[1])
    return NullValue()


def _sort(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing array argument")
    if not isinstance(args[0], ArrayValue):
        raise RuntimeError("Argument must be an array")
    if not all(isinstance(i, NumberValue) for i in args[0].elements):
        raise RuntimeError("Array must contain only numbers")
    args[0].elements.sort(key=lambda x: x.value)  # type: ignore
    return NullValue()


# OS FUNCTIONS


def _getCwd(_: list[RuntimeValue], __: Environment) -> RuntimeValue:
    return StringValue(str(Path.cwd()))


def _changeDir(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing directory argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Directory must be a string")
    os.chdir(args[0].value)
    return NullValue()


def _getEnv(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        return ObjectValue(
            {key: StringValue(value) for key, value in os.environ.items()}
        )
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Variable name must be a string")
    return StringValue(os.environ.get(args[0].value, ""))


def _exec(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing command argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Command must be a string")
    command = os.popen(args[0].value)
    return ObjectValue(
        {
            "output": StringValue(command.read()),
            "status": NumberValue(command.close() or 0),
        }
    )


# JSON FUNCTIONS


def json_to_value(data: dict) -> RuntimeValue:
    """Convert a JSON object to a RuntimeValue."""
    if isinstance(data, list):
        return ArrayValue([json_to_value(value) for value in data])
    if isinstance(data, str):
        return StringValue(data)
    if isinstance(data, (int, float)):
        return NumberValue(data)
    if isinstance(data, bool):
        return BooleanValue(data)
    if data is None:
        return NullValue()
    return ObjectValue({key: json_to_value(value) for key, value in data.items()})


def value_to_json(value: RuntimeValue) -> dict | list | str | int | float | bool | None:
    """Convert a RuntimeValue to a JSON object."""
    if isinstance(value, ObjectValue):
        return {key: value_to_json(val) for key, val in value.properties.items()}
    if isinstance(value, ArrayValue):
        return [value_to_json(val) for val in value.elements]
    if isinstance(value, (StringValue, NumberValue, BooleanValue)):
        return value.value
    if isinstance(value, NullValue):
        return None
    raise RuntimeError("Invalid value")


def _jsonParse(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing JSON string argument")
    if not isinstance(args[0], StringValue):
        raise RuntimeError("Argument must be a string")
    try:
        val = json_to_value(json.loads(args[0].value))
        print(val)
        return val
    except Exception as e:
        raise RuntimeError("Invalid JSON string") from e


def _jsonStringify(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    if not args:
        raise RuntimeError("Missing JSON object argument")
    try:
        return StringValue(json.dumps(value_to_json(args[0])))
    except Exception as e:
        raise RuntimeError("Invalid JSON object") from e


# Declare builtin modules
BUILTINS["file"] = ObjectValue(
    {
        "read": NativeFunctionValue(_readFile),
        "write": NativeFunctionValue(_writeFile),
        "append": NativeFunctionValue(_appendFile),
        "exists": NativeFunctionValue(_fileExists),
        "delete": NativeFunctionValue(_deleteFile),
        "copy": NativeFunctionValue(_copyFile),
        "move": NativeFunctionValue(_moveFile),
        "list": NativeFunctionValue(_listFiles),
        "size": NativeFunctionValue(_fileSize),
    },
    immutable=True,
)

BUILTINS["http"] = ObjectValue(
    {
        "get": NativeFunctionValue(_getRequest),
        "post": NativeFunctionValue(_postRequest),
        "put": NativeFunctionValue(_putRequest),
        "delete": NativeFunctionValue(_deleteRequest),
        "urlencode": NativeFunctionValue(_urlEncode),
        "urldecode": NativeFunctionValue(_urlDecode),
    },
    immutable=True,
)

BUILTINS["math"] = ObjectValue(
    {
        "sum": NativeFunctionValue(_sum),
        "min": NativeFunctionValue(_min),
        "max": NativeFunctionValue(_max),
        "round": NativeFunctionValue(_round),
        "pi": NumberValue(math.pi),
        "sqrt": NativeFunctionValue(_sqrt),
        "random": NativeFunctionValue(_random),
        "abs": NativeFunctionValue(_abs),
        "pow": NativeFunctionValue(_pow),
        "log": NativeFunctionValue(_log),
        "log10": NativeFunctionValue(_log10),
        "sin": NativeFunctionValue(_sin),
        "cos": NativeFunctionValue(_cos),
        "tan": NativeFunctionValue(_tan),
        "asin": NativeFunctionValue(_asin),
        "acos": NativeFunctionValue(_acos),
        "atan": NativeFunctionValue(_atan),
        "floor": NativeFunctionValue(_floor),
        "ceil": NativeFunctionValue(_ceil),
        "e": NumberValue(math.e),
        "factorial": NativeFunctionValue(_factorial),
    },
    immutable=True,
)

BUILTINS["time"] = ObjectValue(
    {
        "time": NativeFunctionValue(_time),
        "sleep": NativeFunctionValue(_sleep),
        "format": NativeFunctionValue(_formatTime),
        "timezone_offset": NativeFunctionValue(_getTimezoneOffset),
    },
    immutable=True,
)

BUILTINS["string"] = ObjectValue(
    {
        "split": NativeFunctionValue(_splitString),
        "join": NativeFunctionValue(_joinStrings),
        "replace": NativeFunctionValue(_replaceString),
        "contains": NativeFunctionValue(_stringContains),
    },
    immutable=True,
)

BUILTINS["array"] = ObjectValue(
    {
        "push": NativeFunctionValue(_push),
        "pop": NativeFunctionValue(_pop),
        "shift": NativeFunctionValue(_shift),
        "unshift": NativeFunctionValue(_unshift),
        "sort": NativeFunctionValue(_sort),
    },
    immutable=True,
)

BUILTINS["os"] = ObjectValue(
    {
        "cwd": NativeFunctionValue(_getCwd),
        "chdir": NativeFunctionValue(_changeDir),
        "env": NativeFunctionValue(_getEnv),
        "exec": NativeFunctionValue(_exec),
    },
    immutable=True,
)

BUILTINS["json"] = ObjectValue(
    {
        "parse": NativeFunctionValue(_jsonParse),
        "stringify": NativeFunctionValue(_jsonStringify),
    },
    immutable=True,
)
