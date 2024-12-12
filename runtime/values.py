"""Values and their types in the runtime environment."""

from enum import Enum, auto


class ValueType(Enum):
    """Types of values in the runtime environment."""

    NULL = auto()
    NUMBER = auto()
    BOOL = auto()


class RuntimeValue:
    """Base class for all runtime values."""

    def __init__(self, kind) -> None:
        self.kind = kind

    def __repr__(self) -> str:
        return f'RuntimeValue("kind": {self.kind.name})'


class NullValue(RuntimeValue):
    """Null value class."""

    def __init__(self) -> None:
        super().__init__(ValueType.NULL)
        self.value = None

    def __repr__(self) -> str:
        return f'NullValue("value": {self.value}, "kind": {self.kind.name})'


class NumberValue(RuntimeValue):
    """Number value class."""

    def __init__(self, number: float) -> None:
        super().__init__(ValueType.NUMBER)
        self.value = number

    def __repr__(self) -> str:
        return f'NumberValue("value": {self.value}, "kind": {self.kind.name})'


class BooleanValue(RuntimeValue):
    """Boolean value class."""

    def __init__(self, value: bool = True) -> None:
        super().__init__(ValueType.BOOL)
        self.value = value

    def __repr__(self) -> str:
        return f'BooleanValue("value": {self.value}, "kind": {self.kind.name})'
