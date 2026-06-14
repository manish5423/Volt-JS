from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]

    def consume(self, expected_type=None, expected_value=None):
        token = self.peek()
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type} at {token.line}:{token.column}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected {expected_value}, got {token.value} at {token.line}:{token.column}")
        self.pos += 1
        return token

    def parse(self):
        body = []
        while self.peek().type != 'EOF':
            body.append(self.parse_statement())
        return Program(body)

    def parse_statement(self):
        token = self.peek()
        if token.value in ('let', 'const', 'var'):
            return self.parse_variable_declaration()
        elif token.value == 'function' and self.peek(1).type == 'IDENTIFIER':
            return self.parse_function_declaration()
        elif token.value == 'if':
            return self.parse_if_statement()
        elif token.value == 'while':
            return self.parse_while_statement()
        elif token.value == 'do':
            return self.parse_do_while_statement()
        elif token.value == 'for':
            return self.parse_for_statement()
        elif token.value == 'return':
            return self.parse_return_statement()
        elif token.value == '{':
            return self.parse_block_statement()
        else:
            expr = self.parse_expression()
            if self.peek().value == ';':
                self.consume()
            return ExpressionStatement(expr)

    def parse_variable_declaration(self):
        kind = self.consume('KEYWORD').value
        identifier = self.consume('IDENTIFIER').value
        init = None
        if self.peek().value == '=':
            self.consume()
            init = self.parse_expression()
        if self.peek().value == ';':
            self.consume()
        return VariableDeclaration(kind, identifier, init)

    def parse_function_declaration(self):
        self.consume('KEYWORD', 'function')
        id = Identifier(self.consume('IDENTIFIER').value)
        self.consume('S_OPERATOR', '(')
        params = []
        if self.peek().value != ')':
            while True:
                params.append(Identifier(self.consume('IDENTIFIER').value))
                if self.peek().value == ',':
                    self.consume()
                else:
                    break
        self.consume('S_OPERATOR', ')')
        body = self.parse_block_statement()
        return FunctionDeclaration(id, params, body)

    def parse_block_statement(self):
        self.consume('S_OPERATOR', '{')
        body = []
        while self.peek().value != '}':
            body.append(self.parse_statement())
        self.consume('S_OPERATOR', '}')
        return BlockStatement(body)

    def parse_if_statement(self):
        self.consume('KEYWORD', 'if')
        self.consume('S_OPERATOR', '(')
        test = self.parse_expression()
        self.consume('S_OPERATOR', ')')
        consequent = self.parse_statement()
        alternate = None
        if self.peek().value == 'else':
            self.consume()
            alternate = self.parse_statement()
        return IfStatement(test, consequent, alternate)

    def parse_do_while_statement(self):
        self.consume('KEYWORD', 'do')
        body = self.parse_statement()
        self.consume('KEYWORD', 'while')
        self.consume('S_OPERATOR', '(')
        test = self.parse_expression()
        self.consume('S_OPERATOR', ')')
        if self.peek().value == ';':
            self.consume()
        return DoWhileStatement(body, test)

    def parse_while_statement(self):
        self.consume('KEYWORD', 'while')
        self.consume('S_OPERATOR', '(')
        test = self.parse_expression()
        self.consume('S_OPERATOR', ')')
        body = self.parse_statement()
        return WhileStatement(test, body)

    def parse_for_statement(self):
        self.consume('KEYWORD', 'for')
        self.consume('S_OPERATOR', '(')
        init = None
        if self.peek().value != ';':
            if self.peek().value in ('let', 'const', 'var'):
                init = self.parse_variable_declaration()
            else:
                init = self.parse_expression()
                if self.peek().value == ';': self.consume()
        else:
            self.consume()
        
        test = None
        if self.peek().value != ';':
            test = self.parse_expression()
        self.consume('S_OPERATOR', ';')
        
        update = None
        if self.peek().value != ')':
            update = self.parse_expression()
        self.consume('S_OPERATOR', ')')
        
        body = self.parse_statement()
        return ForStatement(init, test, update, body)

    def parse_return_statement(self):
        self.consume('KEYWORD', 'return')
        arg = None
        if self.peek().value != ';' and self.peek().type != 'EOF' and self.peek().value != '}':
            arg = self.parse_expression()
        if self.peek().value == ';':
            self.consume()
        return ReturnStatement(arg)

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_ternary()
        if self.peek().value in ('=', '+=', '-=', '*=', '/='):
            operator = self.consume().value
            right = self.parse_assignment()
            return AssignmentExpression(left, operator, right)
        return left

    def parse_ternary(self):
        # Skipping ternary for now, can add later if needed
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.peek().value == '||':
            op = self.consume().value
            right = self.parse_logical_and()
            left = BinaryExpression(left, op, right)
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        while self.peek().value == '&&':
            op = self.consume().value
            right = self.parse_equality()
            left = BinaryExpression(left, op, right)
        return left

    def parse_equality(self):
        left = self.parse_relational()
        while self.peek().value in ('==', '===', '!=', '!=='):
            op = self.consume().value
            right = self.parse_relational()
            left = BinaryExpression(left, op, right)
        return left

    def parse_relational(self):
        left = self.parse_additive()
        while self.peek().value in ('>', '<', '>=', '<='):
            op = self.consume().value
            right = self.parse_additive()
            left = BinaryExpression(left, op, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek().value in ('+', '-'):
            op = self.consume().value
            right = self.parse_multiplicative()
            left = BinaryExpression(left, op, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_exponentiation()
        while self.peek().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_exponentiation()
            left = BinaryExpression(left, op, right)
        return left

    def parse_exponentiation(self):
        left = self.parse_unary()
        while self.peek().value == '**':
            op = self.consume().value
            right = self.parse_unary()
            left = BinaryExpression(left, op, right)
        return left

    def parse_unary(self):
        if self.peek().value in ('!', '-', '++', '--'):
            op = self.consume().value
            arg = self.parse_unary()
            return UnaryExpression(op, arg)
        return self.parse_call_or_member()

    def parse_call_or_member(self):
        expr = self.parse_primary()
        while True:
            if self.peek().value == '(':
                self.consume()
                args = []
                if self.peek().value != ')':
                    while True:
                        args.append(self.parse_expression())
                        if self.peek().value == ',':
                            self.consume()
                        else:
                            break
                self.consume('S_OPERATOR', ')')
                expr = CallExpression(expr, args)
            elif self.peek().value == '.':
                self.consume()
                property = Identifier(self.consume('IDENTIFIER').value)
                expr = MemberExpression(expr, property, False)
            elif self.peek().value == '[':
                self.consume()
                property = self.parse_expression()
                self.consume('S_OPERATOR', ']')
                expr = MemberExpression(expr, property, True)
            elif self.peek().value in ('++', '--'):
                op = self.consume().value
                expr = UnaryExpression(op, expr) # Postfix
            else:
                break
        return expr

    def parse_primary(self):
        token = self.peek()
        if token.type in ('NUMBER', 'STRING', 'BOOLEAN', 'NULL', 'UNDEFINED'):
            self.consume()
            return Literal(token.value)
        elif token.type == 'IDENTIFIER':
            self.consume()
            # Check for Arrow Function
            if self.peek().value == '=>':
                params = [Identifier(token.value)]
                self.consume('OPERATOR', '=>')
                if self.peek().value == '{':
                    body = self.parse_block_statement()
                else:
                    body = self.parse_expression()
                return ArrowFunctionExpression(params, body)
            return Identifier(token.value)
        elif token.value == '(':
            # Lookahead to check if it's an arrow function: (a, b) =>
            # For simplicity, if we see ( and then some identifiers and then ) =>
            # We will try to parse grouping, but if followed by => we treat it as params.
            self.consume()
            
            # This is a hacky way to check for arrow
            checkpoint = self.pos
            is_arrow = False
            paren_count = 1
            temp_pos = self.pos
            while temp_pos < len(self.tokens):
                t = self.tokens[temp_pos]
                if t.value == '(': paren_count += 1
                elif t.value == ')': paren_count -= 1
                if paren_count == 0:
                    if temp_pos + 1 < len(self.tokens) and self.tokens[temp_pos + 1].value == '=>':
                        is_arrow = True
                    break
                temp_pos += 1
            
            if is_arrow:
                params = []
                if self.peek().value != ')':
                    while True:
                        params.append(Identifier(self.consume('IDENTIFIER').value))
                        if self.peek().value == ',': self.consume()
                        else: break
                self.consume('S_OPERATOR', ')')
                self.consume('OPERATOR', '=>')
                if self.peek().value == '{':
                    body = self.parse_block_statement()
                else:
                    body = self.parse_expression()
                return ArrowFunctionExpression(params, body)
            else:
                expr = self.parse_expression()
                self.consume('S_OPERATOR', ')')
                return expr
        elif token.value == '[':
            return self.parse_array_literal()
        elif token.value == '{':
            return self.parse_object_literal()
        elif token.value == 'function':
            # Function expression (anonymous or named)
            self.consume()
            id = None
            if self.peek().type == 'IDENTIFIER':
                id = Identifier(self.consume().value)
            self.consume('S_OPERATOR', '(')
            params = []
            if self.peek().value != ')':
                while True:
                    params.append(Identifier(self.consume('IDENTIFIER').value))
                    if self.peek().value == ',': self.consume()
                    else: break
            self.consume('S_OPERATOR', ')')
            body = self.parse_block_statement()
            # Reuse FunctionDeclaration for expression if id is None? Or new node.
            return FunctionDeclaration(id, params, body)
        
        raise SyntaxError(f"Unexpected token {token.value} at {token.line}:{token.column}")

    def parse_array_literal(self):
        self.consume('S_OPERATOR', '[')
        elements = []
        if self.peek().value != ']':
            while True:
                if self.peek().value == '...':
                    self.consume()
                    elements.append(SpreadElement(self.parse_expression()))
                elif self.peek().value == ',': # Elision
                    elements.append(None)
                    self.consume()
                else:
                    elements.append(self.parse_expression())
                
                if self.peek().value == ',':
                    self.consume()
                else:
                    break
        self.consume('S_OPERATOR', ']')
        return ArrayExpression(elements)

    def parse_object_literal(self):
        self.consume('S_OPERATOR', '{')
        properties = []
        if self.peek().value != '}':
            while True:
                key_token = self.consume()
                key = key_token.value
                self.consume('S_OPERATOR', ':')
                value = self.parse_expression()
                properties.append((key, value))
                if self.peek().value == ',':
                    self.consume()
                else:
                    break
        self.consume('S_OPERATOR', '}')
        return ObjectExpression(properties)
