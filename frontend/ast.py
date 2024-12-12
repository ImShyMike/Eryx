"""Abstract syntax tree (AST) for the frontend."""

from enum import Enum, auto


class NodeType(Enum):
    """Node types in the AST."""
    # Statements
    PROGRAM = auto()
    VARIABLE_DECLARATION = auto()

    # Expressions
    NUMERIC_LITERAL = auto()
    IDENTIFIER = auto()
    BINARY_EXPRESSION = auto()


class Statement:
    """Base class for all statements in the AST."""

    def __init__(self, kind: NodeType) -> None:
        self.kind = kind


class Program(Statement):
    """Program class."""

    def __init__(self, body: list[Statement]) -> None:
        super().__init__(NodeType.PROGRAM)
        self.body = body

    def __repr__(self) -> str:
        return f'Program("body": {self.body})'


class Expression(Statement):
    """Expression base class."""

    def __init__(self, kind: NodeType) -> None:
        super().__init__(kind)
        self.kind = kind

    def __repr__(self) -> str:
        return f'Expression("kind": {self.kind.name})'


class BinaryExpression(Expression):
    """Binary expression class."""

    def __init__(self, left: Expression, operator: str, right: Expression) -> None:
        super().__init__(NodeType.BINARY_EXPRESSION)
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f'BinaryExpression("kind": "{self.kind.name}", "left": {self.left}, "operator": "{self.operator}", "right": {self.right})'


class Identifier(Expression):
    """Identifier class."""

    def __init__(self, symbol: str) -> None:
        super().__init__(NodeType.IDENTIFIER)
        self.symbol = symbol

    def __repr__(self) -> str:
        return f'Identifier("kind": "{self.kind.name}", "symbol": "{self.symbol}")'


class VariableDeclaration(Statement):
    """Variable declaration class."""

    def __init__(self, constant: bool, identifier: Identifier, value: Expression = None) -> None:
        super().__init__(NodeType.VARIABLE_DECLARATION)
        self.constant = constant
        self.identifier = identifier
        self.value = value

    def __repr__(self) -> str:
        return f'VariableDeclaration("constant": "{self.constant}, "identifier": "{self.identifier}", "value": {self.value})'


class NumericLiteral(Expression):
    """Numeric literal class."""

    def __init__(self, value: int) -> None:
        super().__init__(NodeType.NUMERIC_LITERAL)
        self.value = value

    def __repr__(self) -> str:
        return f'NumericLiteral("kind": "{self.kind.name}", "value": {self.value})'
