"""Abstract syntax tree (AST) for the frontend."""


class Statement:
    """Base class for all statements in the AST."""

    def __init__(self) -> None:
        pass


class Program(Statement):
    """Program class."""

    def __init__(self, body: list[Statement]) -> None:
        super().__init__()
        self.body = body


class Expression(Statement):
    """Expression base class."""

    def __init__(self) -> None:  # pylint: disable=useless-super-delegation
        super().__init__()


class AssignmentExpression(Expression):
    """Assignment expression class."""

    def __init__(self, assigne: Expression, value: Expression) -> None:
        super().__init__()
        self.assigne = assigne
        self.value = value


class BinaryExpression(Expression):
    """Binary expression class."""

    def __init__(self, left: Expression, operator: str, right: Expression) -> None:
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right


class Identifier(Expression):
    """Identifier class."""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.symbol = symbol


class VariableDeclaration(Statement):
    """Variable declaration class."""

    def __init__(
        self, constant: bool, identifier: Identifier, value: Expression = None
    ) -> None:
        super().__init__()
        self.constant = constant
        self.identifier = identifier
        self.value = value


class NumericLiteral(Expression):
    """Numeric literal class."""

    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value


class StringLiteral(Expression):
    """String literal class."""

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = str(value)


class Property(Expression):
    """Property class."""

    def __init__(self, key: str, value: Expression = None) -> None:
        super().__init__()
        self.key = key
        self.value = value


class ObjectLiteral(Expression):
    """Object literal class."""

    def __init__(self, properties: list[Property]) -> None:
        super().__init__()
        self.properties = properties


class CallExpression(Expression):
    """Binary expression class."""

    def __init__(self, arguments: list[Expression], caller: Expression) -> None:
        super().__init__()
        self.arguments = arguments
        self.caller = caller


class MemberExpression(Expression):
    """Binary expression class."""

    def __init__(self, obj: Expression, proprty: Expression, computed: bool) -> None:
        super().__init__()
        self.object = obj
        self.property = proprty
        self.computed = computed


class FunctionDeclaration(Statement):
    """Function declaration class."""

    def __init__(self, name: str, arguments: list[str], body: Statement) -> None:
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.body = body
