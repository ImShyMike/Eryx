"""Environment class for storing variables (also called scope)."""

from runtime.values import BooleanValue, NullValue, NumberValue, RuntimeValue, NativeFunctionValue, ObjectValue
import time

class Environment:
    """Environment class."""

    def __init__(self, parent_env: "Environment" = None):
        self.is_global = parent_env is None
        self.parent = parent_env
        self.constants = []
        self.variables = {}

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
        self.declare_variable("print", NativeFunctionValue(_print), True)
        self.declare_variable("time", NativeFunctionValue(_time), True)

def get_value(value: RuntimeValue) -> object:
    """Get the value of a RuntimeValue."""
    if isinstance(value, NullValue):
        return None
    if isinstance(value, BooleanValue):
        return value.value
    if isinstance(value, NumberValue):
        return value.value
    if isinstance(value, ObjectValue):
        result = "{ "
        for key, val in value.properties.items():
            result += f"{key}: {get_value(val)}, "
        result = result[:-2]
        return result + " }"
    return value

# Native functions
def _print(args: list[RuntimeValue], _: Environment) -> RuntimeValue:
    values = []
    for arg in args:
        values.append(get_value(arg))
    print(*values)
    return NullValue()

def _time(_: list[RuntimeValue], __: Environment) -> RuntimeValue:
    return NumberValue(time.time())
