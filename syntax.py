import lexer


class Parser:
    def __init__(self, tokens, source_code):
        self.tokens = tokens
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.current_index = 0
        self.current_token = tokens[self.current_index] if tokens else None

    def advance(self):
        """Move to the next token in the list."""
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = None  # End of file (EOF)

    def fetch_line_content(self, line_number):
        """Fetch the content of the source code at a given line number for error context."""
        if line_number > 0 and line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1]
        return ""  # Return an empty string if the line number is out of range

    def eat(self, expected_type):
        """Consume the next token if it matches expected_type; otherwise, raise a syntax error."""
        if self.current_token is None:
            raise SyntaxError(
                f"Unexpected end of input while expecting {expected_type}"
            )
        if self.current_token['type'] == expected_type:
            print(
                f"Eating token: Type: {expected_type}, Value: {self.current_token['value']}"
            )
            self.advance()
        else:
            found_msg = "but found end of input" if self.current_token is None else f"but found {self.current_token['type']}"
            error_msg = f"Expected token {expected_type}, {found_msg} at line {self.current_token['line']} col {self.current_token['column']}"
            raise SyntaxError(
                error_msg,
                token=self.current_token,
                code_line=self.fetch_line_content(
                    self.current_token['line']
                ) if self.current_token is not None else "",
                line_number=self.current_token['line'] if self.current_token is not None else 0,
                expected_tokens=[expected_type]
            )

    def parse(self):
        print("Starting parsing...")
        try:
            while self.current_token:
                self.statement()
        except SyntaxError as e:
            raise e
        except Exception as e:
            raise SyntaxError(f"Caught exception: {str(e)}")
        finally:
            if self.is_acceptable_end():
                print("Parsing completed successfully.")
            else:
                raise SyntaxError("Unexpected end of input.")

    def statement(self):
        """Identify and process different types of statements based on the current token."""
        try:
            if self.current_token['type'] == 'DATATYPE':
                self.declaration_statement()
            elif self.current_token['type'] in ['IFF', 'MAYBE', 'ORELSE']:
                self.conditional_statement()
            elif self.current_token['type'] in ['ITERATE', 'WHILST']:
                self.loop_statement()
            elif self.current_token['type'] == 'FUNCTION_DEF':
                self.function_definition()
            elif self.current_token['type'] == 'VARIABLE':
                self.assignment_statement()  # Ensure this handles cases like `v-i = v-i + 1`
            else:
                raise SyntaxError("Unexpected statement type",
                                  self.current_token)
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            raise

    def assignment_statement(self):
        """Handle assignments which may not start with a DATATYPE token."""
        self.eat('VARIABLE')
        self.eat('ASSIGN')
        self.expression()  # Handle the expression to the right of the '='
        # This assumes that every statement ends with a comma
        self.eat('STATEMENT_TERMINATOR')

    def declaration_statement(self):
        print(
            f"Processing token: {self.current_token['type']} with value '{self.current_token['value']}'")
        self.eat('DATATYPE')
        self.eat('VARIABLE')
        self.eat('ASSIGN')

        # Instead of directly eating a value token, parse a full expression
        self.expression()  # This will handle things like "v-pi * v-i"

        # Debugging output
        if self.current_token:
            print(
                f"Debug: Finished processing declaration, next token: {self.current_token}")
        else:
            print("Debug: Finished processing declaration, no more tokens.")

        # Verify that the expression ends correctly with a statement terminator
        self.eat('STATEMENT_TERMINATOR')

    def condition_expression(self):
        """ Parse condition expressions which might involve relational or logical operators. """
        self.expression()  # Parse the left-hand side of the expression

        # Consume relational operator if present
        if self.current_token['type'] == 'OPERATOR' and self.current_token['value'] in ['==', '!=', '<', '<=', '>', '>=']:
            self.advance()  # Consume the relational operator
            self.expression()  # Parse the right-hand side of the expression

        # Handle syntax for 'IFF' condition
        if self.current_token['type'] == 'IFF':
            self.advance()  # Consume the 'IFF' token
            if self.current_token['type'] == 'LPAREN':
                self.advance()  # Consume the '(' token
                self.condition_expression()  # Parse the condition inside 'IFF'
                if self.current_token['type'] == 'RPAREN':
                    self.advance()  # Consume the ')' token
                else:
                    self.error("Expected ')' after 'IFF' condition")
            else:
                self.error("Expected '(' after 'IFF'")

        # Handle increment/decrement operators
        if self.current_token['type'] == 'OPERATOR' and self.current_token['value'] in ['++', '--']:
            self.advance()  # Consume the increment/decrement operator
            if self.current_token['type'] != 'VARIABLE':
                self.error("Expected variable for increment/decrement")
            self.advance()  # Consume the variable after increment/decrement

    def expression(self):
        """
        Parse a full expression which could include binary operations.
        """
        self.term()  # Parse the first term

        # Continue parsing if the current token is an operator
        while self.current_token and self.current_token['type'] == 'OPERATOR':
            operator_token = self.current_token
            print(f"Operator token: {operator_token}")
            self.advance()  # Consume the operator
            self.term()  # Parse the next term

    def raise_syntax_error(self, message):
        """
        Helper function to raise a syntax error with detailed information.
        """
        error_msg = f"{message} at line {self.current_token['line']} col {self.current_token['column']}"
        raise SyntaxError(error_msg, self.current_token, self.fetch_line_content(
            self.current_token['line']), self.current_token['line'])

    def conditional_statement(self):
        """ Parses conditional statements, allowing for complex expressions as conditions. """
        while self.current_token:
            if self.current_token['type'] == 'IFF':
                self.eat('IFF')
                self.eat('LPAREN')
                self.condition_expression()   # Parse the condition
                self.eat('RPAREN')
                self.eat('LCURLY')
                while self.current_token and self.current_token['type'] != 'RCURLY':
                    self.statement()  # Process all statements inside the block
                self.eat('RCURLY')

            elif self.current_token['type'] == 'MAYBE':
                self.eat('MAYBE')
                self.eat('LPAREN')  # Condition also for 'maybe'
                self.condition_expression()  # Parse the condition
                self.eat('RPAREN')
                self.eat('LCURLY')
                while self.current_token and self.current_token['type'] != 'RCURLY':
                    self.statement()
                self.eat('RCURLY')

            elif self.current_token['type'] == 'ORELSE':
                self.eat('ORELSE')
                self.eat('LCURLY')
                while self.current_token and self.current_token['type'] != 'RCURLY':
                    self.statement()
                self.eat('RCURLY')

            # Break the loop if the next token is not a continuation of conditional constructs
            else:
                break

    def function_definition(self):
        self.eat('FUNCTION_DEF')
        self.eat('LPAREN')
        if self.current_token['type'] == 'DATATYPE':
            self.parameter_list()
        self.eat('RPAREN')
        self.eat('LCURLY')
        while self.current_token and self.current_token['type'] != 'RCURLY':
            self.statement()
        self.eat('RCURLY')

    def parameter_list(self):
        """ Handle parameter lists in function definitions. """
        self.eat('DATATYPE')
        self.eat('VARIABLE')
        while self.current_token and self.current_token['type'] == 'COMMA':
            self.advance()
            self.eat('DATATYPE')
            self.eat('VARIABLE')

    def block(self):
        """ Parse a block of statements. """
        self.eat('LCURLY')  # Consume the opening curly brace

        # Parse statements until a closing curly brace is encountered
        while self.current_token['type'] != 'RCURLY':
            self.statement()
            # Consume the statement terminator after each statement
            self.eat('STATEMENT_TERMINATOR')

        self.eat('RCURLY')  # Consume the closing curly brace

    def condition(self):
        self.expression()
        if self.current_token['type'] == 'OPERATOR':
            self.eat('OPERATOR')  # Consume the operator
            self.expression()
        # Check for assignment operator (=)
        elif self.current_token['type'] == 'ASSIGN':
            raise SyntaxError(
                "Expected operator in condition expression",
                self.current_token,
                self.fetch_line_content(self.current_token['line']),
                self.current_token['line'] if self.current_token is not None else 0
            )
        else:
            raise SyntaxError(
                "Expected operator in condition expression",
                self.current_token,
                self.fetch_line_content(self.current_token['line']),
                self.current_token['line'] if self.current_token is not None else 0
            )

    def loop_statement(self):
        if self.current_token['type'] == 'ITERATE':
            self.iterate_loop()  # Call a method that handles the syntax of iterate loops
        elif self.current_token['type'] == 'WHILST':
            self.whilst_loop()  # Existing method to handle whilst loops
        else:
            raise SyntaxError("Expected 'ITERATE' or 'WHILST' for loop statement",
                              self.current_token, self.fetch_line_content(
                                  self.current_token['line']),
                              self.current_token['line'] if self.current_token is not None else 0)

        # Check if more tokens are expected after the loop
        if self.current_token and not self.is_acceptable_end():
            raise SyntaxError(
                "Unexpected tokens after loop block", self.current_token)
        elif not self.current_token:
            print("Reached the logical end of input.")

    def iterate_loop(self):
        self.eat('ITERATE')
        self.eat('LPAREN')

        # Process the initialization part
        self.declaration_statement()  # Parse the variable declaration

        # Process the condition part
        self.condition_expression()  # Parse the condition expression

        # Process the increment/decrement part
        self.increment_decrement_statement()  # Parse the increment/decrement

        self.eat('RPAREN')  # End of the loop declaration part

        # Process the loop body
        self.eat('LCURLY')
        while self.current_token and self.current_token['type'] != 'RCURLY':
            self.statement()  # Handle each statement in the loop body
        self.eat('RCURLY')

    def increment_decrement_statement(self):
        """Handles the increment/decrement statement."""
        if self.current_token['type'] == 'VARIABLE':
            self.advance()  # Advance past the variable
            if self.current_token['type'] == 'OPERATOR' and self.current_token['value'] in ['++', '--']:
                self.advance()  # Handle post-increment or post-decrement
                if self.current_token['type'] == 'STATEMENT_TERMINATOR' and self.current_token['value'] == ',':
                    self.advance()  # Expect a comma after the increment/decrement
                else:
                    raise SyntaxError(
                        "Expected ',' after increment/decrement", self.current_token)
            else:
                raise SyntaxError(
                    "Expected '++' or '--' after variable", self.current_token)
        else:
            raise SyntaxError(
                "Expected variable for increment/decrement", self.current_token)

    def whilst_loop(self):
        self.eat('WHILST')
        self.eat('LPAREN')
        self.expression()  # Evaluate the loop's condition
        self.eat('RPAREN')
        self.eat('LCURLY')

        while self.current_token and self.current_token['type'] != 'RCURLY':
            self.statement()
            # If the next token is a statement terminator, consume it,
            # unless it's immediately before a right curly brace which closes the loop.
            if self.peek_next_token() != 'RCURLY' and self.peek_next_token() == 'STATEMENT_TERMINATOR':
                self.eat('STATEMENT_TERMINATOR')

        self.eat('RCURLY')

    def peek_next_token(self):
        """ Look ahead to the next token without consuming it """
        if self.current_index + 1 < len(self.tokens):
            return self.tokens[self.current_index + 1]['type']
        return None  # Return None if there's no next token

    def term(self):
        """Handles terms in an expression, including literals, identifiers, and nested expressions."""
        if self.current_token['type'] in ['NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE']:
            print(
                f"Consuming primary expression token: Type: {self.current_token['type']}, Value: {self.current_token['value']}")
            self.advance()  # Directly consume the primary token
        elif self.current_token['type'] == 'LPAREN':
            self.advance()  # Consume '(' for sub-expressions
            self.expression()
            self.eat('RPAREN')  # Ensure ')' is consumed
        else:
            self.raise_syntax_error("Unexpected primary term in expression")

    def is_acceptable_end(self):
        """ Determines if the current token position is an acceptable place to end the parsing """
        # Examples of acceptable end: after a block, at the file's end, or after a main function
        if not self.current_token or self.current_token['type'] in ['RCURLY', 'EOF']:
            return True
        return False
