"""Values and their types in the runtime environment."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Callable

if TYPE_CHECKING:
    from frontend.ast import Statement
    from runtime.environment import Environment


@dataclass()
class RuntimeValue:
    """Base class for all runtime values."""


@dataclass()
class NullValue(RuntimeValue):
    """Null value class."""

    value: None = None


@dataclass()
class NumberValue(RuntimeValue):
    """Number value class."""

    value: float


@dataclass()
class BooleanValue(RuntimeValue):
    """Boolean value class."""

    value: bool


@dataclass()
class ObjectValue(RuntimeValue):
    """Object value class."""

    properties: Dict[str, RuntimeValue]


@dataclass()
class FunctionCall:
    """Function call class."""

    arguments: List[RuntimeValue]
    environment: "Environment"


@dataclass()
class NativeFunctionValue(RuntimeValue):
    """Native function value class."""

    call: Callable


@dataclass()
class FunctionValue(RuntimeValue):
    """Function value class."""

    name: str
    arguments: List[str]
    environment: "Environment"
    body: List["Statement"]


@dataclass()
class StringValue(RuntimeValue):
    """String value class."""

    value: str


@dataclass()
class ArrayValue(RuntimeValue):
    """Array value class."""

    elements: List[RuntimeValue]
