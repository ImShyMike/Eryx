"""Values and their types in the runtime environment."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.ast import Statement
    from runtime.environment import Environment


class RuntimeValue:
    """Base class for all runtime values."""

    def __init__(self) -> None:
        pass


class NullValue(RuntimeValue):
    """Null value class."""

    def __init__(self) -> None:
        super().__init__()
        self.value = None


class NumberValue(RuntimeValue):
    """Number value class."""

    def __init__(self, number: float) -> None:
        super().__init__()
        self.value = number


class BooleanValue(RuntimeValue):
    """Boolean value class."""

    def __init__(self, value: bool = True) -> None:
        super().__init__()
        self.value = value


class ObjectValue(RuntimeValue):
    """Object value class."""

    def __init__(self, properties: dict[str, RuntimeValue]) -> None:
        super().__init__()
        self.properties = properties


class FunctionCall:
    """Function call class."""

    def __init__(
        self, arguments: list[RuntimeValue], environment: EnvironmentError
    ) -> RuntimeValue:
        self.arguments = arguments
        self.environment = environment


class NativeFunctionValue(RuntimeValue):
    """Native function value class."""

    def __init__(self, call: FunctionCall) -> None:
        super().__init__()
        self.call = call


class FunctionValue(RuntimeValue):
    """Function value class."""

    def __init__(
        self,
        name: str,
        arguments: list[str],
        environment: "Environment",
        body: list["Statement"],
    ) -> None:
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.environment = environment
        self.body = body
