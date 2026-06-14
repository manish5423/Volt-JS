from dataclasses import dataclass
from typing import List, Optional, Any, Union

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    body: List[Node]

@dataclass
class Expression(Node):
    pass

@dataclass
class Statement(Node):
    pass

@dataclass
class VariableDeclaration(Statement):
    kind: str  # 'let', 'const', 'var'
    identifier: str
    init: Optional[Expression]

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: Any

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryExpression(Expression):
    operator: str
    argument: Expression

@dataclass
class AssignmentExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class CallExpression(Expression):
    callee: Expression
    arguments: List[Expression]

@dataclass
class MemberExpression(Expression):
    object: Expression
    property: Expression
    computed: bool = False

@dataclass
class ArrayExpression(Expression):
    elements: List[Optional[Union[Expression, 'SpreadElement']]]

@dataclass
class SpreadElement(Node):
    argument: Expression

@dataclass
class ObjectExpression(Expression):
    properties: List[tuple] # (key, value)

@dataclass
class FunctionDeclaration(Statement):
    id: Identifier
    params: List[Identifier]
    body: 'BlockStatement'

@dataclass
class ArrowFunctionExpression(Expression):
    params: List[Identifier]
    body: Union['BlockStatement', Expression]

@dataclass
class BlockStatement(Statement):
    body: List[Statement]

@dataclass
class IfStatement(Statement):
    test: Expression
    consequent: Statement
    alternate: Optional[Statement]

@dataclass
class WhileStatement(Statement):
    test: Expression
    body: Statement

@dataclass
class DoWhileStatement(Statement):
    body: Statement
    test: Expression

@dataclass
class ForStatement(Statement):
    init: Optional[Union[VariableDeclaration, Expression]]
    test: Optional[Expression]
    update: Optional[Expression]
    body: Statement

@dataclass
class ReturnStatement(Statement):
    argument: Optional[Expression]

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class TemplateLiteral(Expression):
    quasis: List[str]
    expressions: List[Expression]
