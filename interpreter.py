from ast_nodes import *
from environment import Environment
from runtime import BuiltinFunction, JSFunction, create_global_env, handle_member_access

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_env = create_global_env(self)

    def interpret(self, program):
        try:
            return self.evaluate(program, self.global_env)
        except Exception as e:
            print(f"Runtime Error: {e}")
            raise e

    def evaluate(self, node, env):
        if isinstance(node, Program):
            result = None
            for stmt in node.body:
                result = self.evaluate(stmt, env)
            return result

        elif isinstance(node, ExpressionStatement):
            return self.evaluate(node.expression, env)

        elif isinstance(node, Literal):
            return node.value

        elif isinstance(node, Identifier):
            return env.lookup(node.name)

        elif isinstance(node, BinaryExpression):
            left = self.evaluate(node.left, env)
            right = self.evaluate(node.right, env)
            
            op = node.operator
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    from runtime import format_js
                    return format_js(left) + format_js(right)
                return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '%': return left % right
            if op == '**': return left ** right
            if op == '===' or op == '==': return left == right
            if op == '!==' or op == '!=': return left != right
            if op == '>': return left > right
            if op == '<': return left < right
            if op == '>=': return left >= right
            if op == '<=': return left <= right
            if op == '&&': return left and right
            if op == '||': return left or right
            raise Exception(f"Unknown operator {op}")

        elif isinstance(node, UnaryExpression):
            # Handle unaries like !, -, ++, --
            arg = node.argument
            if node.operator == '!': return not self.evaluate(arg, env)
            if node.operator == '-': return -self.evaluate(arg, env)
            if node.operator == '++':
                # Simplified pre-increment
                val = env.lookup(arg.name) + 1
                env.assign(arg.name, val)
                return val
            if node.operator == '--':
                val = env.lookup(arg.name) - 1
                env.assign(arg.name, val)
                return val

        elif isinstance(node, VariableDeclaration):
            val = self.evaluate(node.init, env) if node.init else None
            env.define(node.identifier, val, node.kind == 'const')
            return None

        elif isinstance(node, AssignmentExpression):
            val = self.evaluate(node.right, env)
            if isinstance(node.left, Identifier):
                name = node.left.name
                if node.operator == '=': env.assign(name, val)
                elif node.operator == '+=': env.assign(name, env.lookup(name) + val)
                elif node.operator == '-=': env.assign(name, env.lookup(name) - val)
                elif node.operator == '*=': env.assign(name, env.lookup(name) * val)
                elif node.operator == '/=': env.assign(name, env.lookup(name) / val)
                return val
            elif isinstance(node.left, MemberExpression):
                obj = self.evaluate(node.left.object, env)
                prop = self.evaluate(node.left.property, env) if node.left.computed else node.left.property.name
                obj[prop] = val
                return val
            raise Exception("Invalid assignment left-hand side")

        elif isinstance(node, BlockStatement):
            new_env = Environment(env)
            result = None
            for stmt in node.body:
                result = self.evaluate(stmt, new_env)
            return result

        elif isinstance(node, IfStatement):
            if self.evaluate(node.test, env):
                return self.evaluate(node.consequent, env)
            elif node.alternate:
                return self.evaluate(node.alternate, env)
            return None

        elif isinstance(node, WhileStatement):
            result = None
            while self.evaluate(node.test, env):
                result = self.evaluate(node.body, env)
            return result

        elif isinstance(node, DoWhileStatement):
            result = self.evaluate(node.body, env)
            while self.evaluate(node.test, env):
                result = self.evaluate(node.body, env)
            return result

        elif isinstance(node, ForStatement):
            new_env = Environment(env)
            if node.init: self.evaluate(node.init, new_env)
            result = None
            while node.test is None or self.evaluate(node.test, new_env):
                result = self.evaluate(node.body, new_env)
                if node.update: self.evaluate(node.update, new_env)
            return result

        elif isinstance(node, FunctionDeclaration):
            func = JSFunction(node.params, node.body, env, self)
            if node.id:
                env.define(node.id.name, func)
            return func

        elif isinstance(node, ReturnStatement):
            val = self.evaluate(node.argument, env) if node.argument else None
            raise ReturnException(val)

        elif isinstance(node, CallExpression):
            callee = self.evaluate(node.callee, env)
            args = [self.evaluate(arg, env) for arg in node.arguments]
            if callable(callee):
                # If it's a member expression call, the 'this' context might be needed.
                # Simplified: just call.
                return callee(*args)
            raise TypeError(f"{callee} is not a function")

        elif isinstance(node, MemberExpression):
            obj = self.evaluate(node.object, env)
            if node.computed:
                prop = self.evaluate(node.property, env)
            else:
                prop = node.property.name
            
            # Special handling for methods/properties in runtime.py
            result = handle_member_access(obj, prop, node.computed)
            return result

        elif isinstance(node, ArrayExpression):
            result = []
            for el in node.elements:
                if isinstance(el, SpreadElement):
                    arg = self.evaluate(el.argument, env)
                    if isinstance(arg, (list, str)):
                        result.extend(list(arg))
                    else:
                        raise TypeError(f"{arg} is not iterable")
                elif el:
                    result.append(self.evaluate(el, env))
                else:
                    result.append(None)
            return result

        elif isinstance(node, ObjectExpression):
            obj = {}
            for k, v in node.properties:
                obj[k] = self.evaluate(v, env)
            return obj

        elif isinstance(node, ArrowFunctionExpression):
            return JSFunction(node.params, node.body if isinstance(node.body, BlockStatement) else ExpressionStatement(node.body), env, self)

        raise Exception(f"Wait... don't know how to evaluate node {type(node)}")
