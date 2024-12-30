"""Parser module for the frontend of the compiler."""

from eryx.frontend.ast import (
    ArrayLiteral,
    AssignmentExpression,
    BinaryExpression,
    CallExpression,
    Expression,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    ImportStatement,
    MemberExpression,
    NumericLiteral,
    ObjectLiteral,
    Program,
    Property,
    ReturnStatement,
    Statement,
    StringLiteral,
    VariableDeclaration,
)
from eryx.frontend.lexer import Token, TokenType, tokenize
from eryx.utils.errors import syntax_error

# Precedence:
# 1. Member expression: obj.prop, obj[expr]
# 2. Call expression: func(), obj.method()
# 3. Exponentiation: **
# 4. Multiplication, division, modulo: *, /, %
# 5. Addition, subtraction: +, -
# 6. Bitwise operations: <<, >>, &, |, ^
# 7. Logical AND and OR: &&, ||
# 8. Comparison: ==, !=, >, >=, <, <=
# 9. Assignment: =


class Parser:
    """Parser class."""

    def __init__(self) -> None:
        self.source_code = ""
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

    def look_ahead(self, n: int) -> Token:
        """Look ahead n tokens."""
        return self.tokens[n]

    def assert_next(self, token_type: TokenType, error: str) -> Token:
        """Return the current token and assert that the next token is of a certain type."""
        token = self.next()
        if token.type != token_type:
            syntax_error(self.source_code, token.position, error)
        return token

    def parse_additive_expression(self) -> Expression:
        """Parse an additive expression."""
        left = self.parse_multiplicative_expression()

        while self.at().value in ("+", "-"):
            operator = self.next().value
            right = self.parse_multiplicative_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_call_member_expression(self) -> Expression:
        """Parse a call member expression."""
        member = self.parse_member_expression()

        if self.at().type == TokenType.OPEN_PAREN:
            return self.parse_call_expression(member)

        return member

    def parse_call_expression(self, caller: Expression) -> Expression:
        """Parse a call expression."""
        call_expression = CallExpression(self.parse_arguments(), caller)

        if self.at().type == TokenType.OPEN_PAREN:
            call_expression = self.parse_call_expression(call_expression)

        return call_expression

    def parse_arguments(self) -> list[Expression]:
        """Parse arguments."""
        self.assert_next(TokenType.OPEN_PAREN, "Expected an open parenthesis.")

        arguments = (
            []
            if self.at().type == TokenType.CLOSE_PAREN
            else self.parse_arguments_list()
        )

        self.assert_next(TokenType.CLOSE_PAREN, "Expected a closing parenthesis.")

        return arguments

    def parse_arguments_list(self) -> list[Expression]:
        """Parse an arguments list."""
        arguments = [self.parse_assignment_expression()]

        while self.at().type == TokenType.COMMA:
            self.next()  # Skip the comma
            arguments.append(self.parse_assignment_expression())

        return arguments

    def parse_member_expression(self) -> Expression:
        """Parse a member expression."""
        obj = self.parse_primary_expression()

        while self.at().type in (TokenType.OPEN_BRACKET, TokenType.DOT):
            operator = self.next()
            proprty = None
            computed = False

            if operator.type == TokenType.DOT:
                proprty = self.parse_primary_expression()  # Identifier

                if not isinstance(proprty, Identifier):
                    syntax_error(
                        self.source_code,
                        self.at().position,
                        "Expected an identifier as a property.",
                    )
            else:
                computed = True
                proprty = self.parse_expression()
                self.assert_next(TokenType.CLOSE_BRACKET, "Expected a closing bracket.")

            obj = MemberExpression(obj, proprty, computed)

        return obj

    def parse_multiplicative_expression(self) -> Expression:
        """Parse a multiplicative expression."""
        left = self.parse_exponentiation_expression()

        while self.at().value in ("/", "*", "%"):
            operator = self.next().value
            right = self.parse_exponentiation_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_exponentiation_expression(self) -> Expression:
        """Parse an exponentiation expression."""
        left = self.parse_call_member_expression()

        while self.at().value == "**":
            operator = self.next().value
            right = self.parse_call_member_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_array_expression(self) -> Expression:
        """Parse an array expression."""
        self.assert_next(
            TokenType.OPEN_BRACKET, "Expected an opening bracket '[' for array."
        )

        elements = []
        # Check for empty arrays
        if self.at().type != TokenType.CLOSE_BRACKET:
            elements.append(self.parse_expression())

            while self.at().type == TokenType.COMMA:
                self.next()  # Skip the comma
                elements.append(self.parse_expression())

        self.assert_next(
            TokenType.CLOSE_BRACKET, "Expected a closing bracket ']' for array."
        )
        return ArrayLiteral(elements)

    def parse_primary_expression(self) -> Expression:
        """Parse a primary expression."""
        token = self.at()

        match token.type:
            case TokenType.IDENTIFIER:
                return Identifier(self.next().value)
            case TokenType.NUMBER:
                return NumericLiteral(float(self.next().value))
            case TokenType.STRING:
                return StringLiteral(self.next().value)
            case TokenType.OPEN_BRACKET:
                return self.parse_array_expression()
            case TokenType.OPEN_BRACE:
                return self.parse_object_expression()
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
                syntax_error(self.source_code, token.position, "Unexpected token.")
                return Expression()  # This will never be reached

    def parse_assignment_expression(self) -> Expression:
        """Parse an assignment expression."""
        left = self.parse_comparison_expression()

        if (
            self.at().type == TokenType.EQUALS
            and self.look_ahead(1).type != TokenType.EQUALS
        ):
            self.next()  # Skip the equals sign

            value = self.parse_assignment_expression()
            return AssignmentExpression(left, value)

        return left

    def parse_expression(self) -> Expression:
        """Parse an expression."""
        return self.parse_assignment_expression()

    def parse_object_expression(self) -> Expression:
        """Parse an object expression."""

        self.next()  # Skip the open brace

        properties = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            key = self.assert_next(
                TokenType.IDENTIFIER, "Expected an identifier as a key."
            )

            if self.at().type == TokenType.COMMA:
                self.next()  # Skip the comma
                properties.append(Property(key.value))
                continue

            if self.at().type == TokenType.CLOSE_BRACE:
                properties.append(Property(key.value))
                continue

            self.assert_next(TokenType.COLON, "Expected a colon after the key.")

            value = self.parse_expression()
            properties.append(Property(key.value, value))

            if self.at().type != TokenType.CLOSE_BRACE:
                self.assert_next(
                    TokenType.COMMA,
                    "Expected a comma or closing brace after the value.",
                )

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected a closing brace after the object."
        )
        return ObjectLiteral(properties)

    def parse_comparison_expression(self) -> Expression:
        """Parse a comparison expression."""
        left = self.parse_logical_expression()

        while self.at().value in ("==", "!=", ">", ">=", "<", "<="):
            operator = self.next().value
            right = self.parse_logical_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_bitwise_expression(self) -> Expression:
        """Parse a bitwise expression."""
        left = self.parse_additive_expression()

        while self.at().value in ("&", "|", "^", "<<", ">>"):
            operator = self.next().value
            right = self.parse_additive_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_logical_expression(self) -> Expression:
        """Parse a logical expression."""
        left = self.parse_bitwise_expression()

        while self.at().value in ("&&", "||"):
            operator = self.next().value
            right = self.parse_bitwise_expression()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_if_statement(self) -> Statement:
        """Parse an if statement."""
        self.next()  # Skip the if keyword
        self.assert_next(
            TokenType.OPEN_PAREN,
            "Expected an opening parenthesis for the if condition.",
        )

        condition = self.parse_expression()

        self.assert_next(
            TokenType.CLOSE_PAREN,
            "Expected a closing parenthesis after the if condition.",
        )

        self.assert_next(
            TokenType.OPEN_BRACE, "Expected an opening brace for the if body."
        )

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            body.append(self.parse_statement())

        self.assert_next(
            TokenType.CLOSE_BRACE, "Expected a closing brace after the if body."
        )

        if self.at().type == TokenType.ELSE:
            self.next()
            self.assert_next(
                TokenType.OPEN_BRACE, "Expected an opening brace for the else body."
            )

            else_body = []
            while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
                else_body.append(self.parse_statement())

            self.assert_next(
                TokenType.CLOSE_BRACE, "Expected a closing brace after the else body."
            )

            return IfStatement(condition, then=body, else_=else_body)

        return IfStatement(condition, then=body)

    def parse_return_statement(self) -> Statement:
        """Parse a return statement."""
        self.next()  # Skip the return keyword
        value = self.parse_expression()

        self.assert_next(TokenType.SEMICOLON, "Expected a semicolon after the return.")

        return ReturnStatement(value)

    def parse_function_declaration(self) -> Statement:
        """Parse a function declaration."""
        self.next()  # Skip the func keyword
        name = self.assert_next(
            TokenType.IDENTIFIER,
            "Expected an function name after the function keyword.",
        ).value
        arguments = self.parse_arguments()

        parameters = []
        for argument in arguments:
            if isinstance(argument, Identifier):
                parameters.append(argument.symbol)
            else:
                syntax_error(
                    self.source_code,
                    self.at().position,
                    "Function arguments must be identifiers.",
                )

        self.assert_next(TokenType.OPEN_BRACE, "Expected an opening brace.")

        body = []
        while self.not_eof() and self.at().type != TokenType.CLOSE_BRACE:
            body.append(self.parse_statement())

        self.assert_next(
            TokenType.CLOSE_BRACE,
            "Expected a closing brace after the function body.",
        )

        return FunctionDeclaration(name, parameters, body)

    def parse_variable_declaration(self) -> Statement:
        """Parse a variable declaration."""
        is_constant = self.next().type == TokenType.CONST
        identifier = self.assert_next(
            TokenType.IDENTIFIER, "Expected an identifier after a declaration."
        ).value

        if self.at().type == TokenType.SEMICOLON:
            self.next()  # Skip the semicolon
            if is_constant:
                syntax_error(
                    self.source_code,
                    self.at().position,
                    "Constant declaration must have an initial value.",
                )

            return VariableDeclaration(is_constant, Identifier(identifier))

        self.assert_next(
            TokenType.EQUALS, "Expected an equals sign after the identifier."
        )

        declaration = VariableDeclaration(
            is_constant, Identifier(identifier), self.parse_expression()
        )

        self.assert_next(
            TokenType.SEMICOLON, "Expected a semicolon after the declaration."
        )

        return declaration

    def parse_import_statement(self) -> Statement:
        """Parse an import statement."""
        self.next()  # Skip the import keyword

        value = self.assert_next(
            TokenType.STRING, "Expected a string after the import keyword."
        )

        if self.at().type == TokenType.AS:
            self.next() # Skip the as keyword

            alias = self.assert_next(TokenType.STRING, "Expected a string for the import alias.")

            return ImportStatement(value.value, alias=alias.value)

        return ImportStatement(value.value)

    def parse_from_statement(self) -> Statement:
        """Parse a from statement."""
        self.next()  # Skip the from keyword

        from_value = self.assert_next(
            TokenType.STRING, "Expected a string after the from keyword."
        )

        if not self.at().type == TokenType.IMPORT:
            syntax_error(
                self.source_code,
                self.at().position,
                "Expected an import keyword after the from keyword.",
            )

        self.next()  # Skip the import keyword

        import_value = self.parse_array_expression()

        if not isinstance(import_value, ArrayLiteral):
            syntax_error(
                self.source_code,
                self.at().position,
                "Import properties must be an array.",
            )
            return ImportStatement(
                from_value.value, None
            )  # Type checker stuff, will never happen

        if not import_value.elements:
            syntax_error(
                self.source_code,
                self.at().position,
                "Import properties must not be empty.",
            )

        if not all(isinstance(item, StringLiteral) for item in import_value.elements):
            syntax_error(
                self.source_code,
                self.at().position,
                "Import properties must be strings.",
            )

        return ImportStatement(
            from_value.value,
            [
                item.value
                for item in import_value.elements
                if isinstance(item, StringLiteral)
            ],
        )

    def parse_statement(self) -> Statement:
        """Parse a statement."""
        match self.at().type:
            case TokenType.LET:
                return self.parse_variable_declaration()
            case TokenType.CONST:
                return self.parse_variable_declaration()
            case TokenType.FUNC:
                return self.parse_function_declaration()
            case TokenType.IF:
                return self.parse_if_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case TokenType.IMPORT:
                return self.parse_import_statement()
            case TokenType.FROM:
                return self.parse_from_statement()
            case _:
                return self.parse_expression()

    def produce_ast(self, source_code: str) -> Program:
        """Produce an abstract syntax tree (AST) from source code."""
        self.source_code = source_code
        self.tokens = tokenize(source_code)
        program = Program(body=[])

        # Parse all statements in the program until the EOF
        while self.not_eof():
            program.body.append(self.parse_statement())

        return program
