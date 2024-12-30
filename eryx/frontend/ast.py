"""Abstract syntax tree (AST) for the frontend."""

from dataclasses import dataclass, field
from typing import List, Union


@dataclass()
class Statement:
    """Base class for all statements in the AST."""


@dataclass()
class Program(Statement):
    """Program class."""

    body: List[Statement]


@dataclass()
class Expression(Statement):
    """Expression base class."""


@dataclass()
class AssignmentExpression(Expression):
    """Assignment expression class."""

    assigne: Expression
    value: Expression


@dataclass()
class BinaryExpression(Expression):
    """Binary expression class."""

    left: Expression
    operator: str
    right: Expression


@dataclass()
class Identifier(Expression):
    """Identifier class."""

    symbol: str


@dataclass()
class VariableDeclaration(Statement):
    """Variable declaration class."""

    constant: bool
    identifier: Identifier
    value: Union[Expression, None] = None


@dataclass()
class NumericLiteral(Expression):
    """Numeric literal class."""

    value: float


@dataclass()
class StringLiteral(Expression):
    """String literal class."""

    value: str


@dataclass()
class Property(Expression):
    """Property class."""

    key: str
    value: Union[Expression, None] = None


@dataclass()
class ObjectLiteral(Expression):
    """Object literal class."""

    properties: List[Property]


@dataclass()
class ArrayLiteral(Expression):
    """Represents an array literal."""

    elements: List[Expression]


@dataclass()
class CallExpression(Expression):
    """Binary expression class."""

    arguments: List[Expression]
    caller: Expression


@dataclass()
class MemberExpression(Expression):
    """Binary expression class."""

    object: Expression
    property: Expression
    computed: bool


@dataclass()
class FunctionDeclaration(Statement):
    """Function declaration class."""

    name: str
    arguments: List[str]
    body: list[Statement]


@dataclass()
class IfStatement(Statement):
    """If statement class."""

    condition: Expression
    then: list[Statement]
    else_: list[Union[Statement, None]] = field(default_factory=list)


@dataclass()
class ReturnStatement(Statement):
    """Return statement class."""

    value: Union[Expression, None] = None

@dataclass()
class ImportStatement(Statement):
    """Import statement class."""

    module: str
    names: List[str] | None = None
    alias: str | None = None
