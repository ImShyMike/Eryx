"""Module for error classes."""

from dataclasses import dataclass
from typing import Union


@dataclass()
class BaseError(RuntimeError):
    """Base error class."""

    message: str
    position: Union[int, tuple[int, int]] = 0

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} (Position: {self.position})"


@dataclass()
class ZeroDivisionError(BaseError):
    message: str = "Division by zero"


@dataclass()
class IndexError(BaseError):
    message: str = "Index out of range"


@dataclass()
class KeyError(BaseError):
    message: str = "Key not found"


@dataclass()
class EOFError(BaseError):
    message: str = "End of file reached"


@dataclass()
class ImportError(BaseError):
    message: str = "Import error"


@dataclass()
class NameError(BaseError):
    message: str = "Variable not found"


@dataclass()
class NotImplementedError(BaseError):
    message: str = "Not implemented"


@dataclass()
class SyntaxError(BaseError):
    message: str = "Syntax error"
