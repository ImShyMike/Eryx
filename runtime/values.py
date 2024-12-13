"""Values and their types in the runtime environment."""

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
