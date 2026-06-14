import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}:{self.column})"

class Lexer:
    TOKEN_TYPES = [
        ('NUMBER',   r'\d+(\.\d+)?'),
        ('STRING',   r'"[^"]*"|\'[^\']*\''),
        ('TEMPLATE', r'`[^`]*`'),
        ('BOOLEAN',  r'\b(true|false)\b'),
        ('NULL',     r'\bnull\b'),
        ('UNDEFINED',r'\bundefined\b'),
        ('KEYWORD',  r'\b(let|const|var|if|else|for|while|function|return|new|class|try|catch|finally|throw|break|continue|switch|case|default|do|import|export|from|as|in|of|typeof|instanceof|delete)\b'),
        ('OPERATOR', r'\.\.\.|\*\*=|(?:\+\+|--|\+=|-=|\*=|/=|%=|\*\*|===|==|!==|!=|>=|<=|=>|&&|\|\||[+\-*/%><=!])'),
        ('IDENTIFIER', r'[a-zA-Z_$][a-zA-Z0-9_$]*'),
        ('S_OPERATOR', r'[{}()\[\],.;:]'),
        ('NEWLINE',  r'\n'),
        ('SKIP',     r'[ \t]+'),
        ('COMMENT',  r'//.*|/\*[\s\S]*?\*/'),
        ('MISMATCH', r'.'),
    ]

    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.line = 1
        self.column_start = 0

    def tokenize(self):
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_TYPES)
        for mo in re.finditer(regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - self.column_start
            
            if kind == 'NUMBER':
                self.tokens.append(Token(kind, float(value) if '.' in value else int(value), self.line, column))
            elif kind == 'STRING':
                self.tokens.append(Token(kind, value[1:-1], self.line, column))
            elif kind == 'TEMPLATE':
                # Simplified: No interpolation support for now
                self.tokens.append(Token('STRING', value[1:-1], self.line, column))
            elif kind == 'BOOLEAN':
                self.tokens.append(Token(kind, value == 'true', self.line, column))
            elif kind == 'NULL':
                self.tokens.append(Token(kind, None, self.line, column))
            elif kind == 'UNDEFINED':
                self.tokens.append(Token(kind, 'undefined', self.line, column))
            elif kind == 'KEYWORD':
                self.tokens.append(Token(kind, value, self.line, column))
            elif kind == 'OPERATOR':
                self.tokens.append(Token(kind, value, self.line, column))
            elif kind == 'IDENTIFIER':
                self.tokens.append(Token(kind, value, self.line, column))
            elif kind == 'S_OPERATOR':
                self.tokens.append(Token(kind, value, self.line, column))
            elif kind == 'NEWLINE':
                self.line += 1
                self.column_start = mo.end()
            elif kind == 'SKIP' or kind == 'COMMENT':
                pass
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Unexpected character {value!r} at line {self.line}')
        
        self.tokens.append(Token('EOF', None, self.line, 0))
        return self.tokens
