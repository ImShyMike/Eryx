"""Parser module for the frontend of the compiler."""

from frontend.ast import (
    BinaryExpression,
    Expression,
    Identifier,
    NumericLiteral,
    Program,
    Statement,
    VariableDeclaration,
    AssignmentExpression,
    Property,
)
from frontend.lexer import Token, TokenType, tokenize


class Parser:
    """Parser class."""

    def __init__(self) -> None:
        self.tokens = []

    def not_eof(self) -> bool:
        """Check if the parser has not reached the end of the token stream."""
        return self.tokens[0].type != TokenType.EOF

    def at(self) -> Token:
        """Get the current token."""
        return self.tokens[0]

    def next(self) -> Token:
        """Get the current token and skip to next one (also called eat)."""
        return self.tokens.pop(0)

    def assert_next(self, token_type: TokenType, error: str) -> Token:
        """Assert that the next token is of a certain type and get the current token."""
        token = self.next()
        if token.type != token_type:
            raise RuntimeError(
                f"Parser error: \n{error} {token} - Expected: {token_type}"
            )
        return token

    def parse_additive_expression(self) -> Expression:
        """Parse an additive expression."""
        left = self.parse_multiplicative_expression()

        while self.at().value in ("+", "-"):
            operator = self.next().value
            right = self.parse_multiplicative_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_multiplicative_expression(self) -> Expression:
        """Parse a multiplicative expression."""
        left = self.parse_primary_expression()

        while self.at().value in ("/", "*", "%"):
            operator = self.next().value
            right = self.parse_primary_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_primary_expression(self) -> Expression:
        """Parse a primary expression."""
        token = self.at()

        match token.type:
            case TokenType.IDENTIFIER:
                return Identifier(self.next().value)
            case TokenType.NUMBER:
                return NumericLiteral(float(self.next().value))
            case TokenType.OPEN_PAREN:
                self.next()  # Skip the open parenthesis
                expression = self.parse_expression()
                self.assert_next(
                    TokenType.CLOSE_PAREN,
                    "Unexpected token found inside parenthesised expression."
                    "Expected closing parenthesis.",
                )  # Skip the close parenthesis
                return expression
            case _:
                raise RuntimeError(f"Unexpected token: {token}")

    def parse_assignment_expression(self) -> Expression:
        """Parse an assignment expression."""
        left = self.parse_object_expression() # TODO: support objects and stuff

        if self.at().type == TokenType.EQUALS:
            self.next() # Skip the equals sign

            value = self.parse_assignment_expression()
            return AssignmentExpression(left, value)

        return left

    def parse_expression(self) -> Expression:
        """Parse an expression."""
        return self.parse_assignment_expression()

    def parse_object_expression(self) -> Expression:
        """Parse an object expression."""
        if self.at().type != TokenType.OPEN_BRACE:
            return self.parse_additive_expression()

        self.next() # Skip the open brace

        properties = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            key = self.assert_next(TokenType.IDENTIFIER, "Expected an identifier as a key.")

            if self.at().type == TokenType.COMMA:
                self.next() # Skip the comma
                properties.append(Property(key.value))
                continue
            elif self.at().type == TokenType.CLOSE_BRACE:
                properties.append(Property(key.value))
                continue

        self.assert_next(TokenType.COLON, "Expected a colon after the key.")

        value = self.parse_expression()
        properties.append(Property(key.value), value)

        if self.at().type != TokenType.CLOSE_BRACE:
            self.assert_next(TokenType.COMMA, "Expected a comma or closing brace after the value.")

    def parse_variable_declaration(self) -> Statement:
        """Parse a variable declaration."""
        is_constant = self.next().type == TokenType.CONST
        identifier = self.assert_next(
            TokenType.IDENTIFIER,
            "Expected an identifier after a declaration."
        ).value

        if self.at().type == TokenType.SEMICOLON:
            self.next() # Skip the semicolon
            if is_constant:
                raise RuntimeError("Constant declaration must have an initial value.")

            return VariableDeclaration(is_constant, Identifier(identifier))

        self.assert_next(
            TokenType.EQUALS,
            "Expected an equals sign after the identifier."
        )

        declaration = VariableDeclaration(
            is_constant,
            Identifier(identifier),
            self.parse_expression()
        )

        self.assert_next(
            TokenType.SEMICOLON,
            "Expected a semicolon after the declaration."
        )

        return declaration

    def parse_statement(self) -> Statement:
        """Parse a statement."""
        match self.at().type:
            case TokenType.LET:
                return self.parse_variable_declaration()
            case TokenType.CONST:
                return self.parse_variable_declaration()
            case _:
                return self.parse_expression()

    def produce_ast(self, source_code: str) -> Program:
        """Produce an abstract syntax tree (AST) from source code."""
        self.tokens = tokenize(source_code)
        program = Program(body=[])

        # Parse all statements in the program until the EOF
        while self.not_eof():
            program.body.append(self.parse_statement())

        return program
