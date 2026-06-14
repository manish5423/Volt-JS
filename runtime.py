import math
import time
import random
from datetime import datetime

class JSValue:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)

class JSObject(dict):
    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        self[name] = value

class JSFunction:
    def __init__(self, params, body, env, interpreter):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter

    def __call__(self, *args):
        from environment import Environment
        from interpreter import ReturnException
        new_env = Environment(self.env)
        for i, param in enumerate(self.params):
            val = args[i] if i < len(args) else None
            new_env.define(param.name, val)
        
        try:
            return self.interpreter.evaluate(self.body, new_env)
        except ReturnException as e:
            return e.value

class BuiltinFunction:
    def __init__(self, func):
        self.func = func
    def __call__(self, *args):
        return self.func(*args)

def js_log(*args):
    print(*(format_js(a) for a in args))

def format_js(val):
    if val is True: return "true"
    if val is False: return "false"
    if val is None: return "null"
    if isinstance(val, list):
        return "[" + ", ".join(format_js(x) for x in val) + "]"
    if isinstance(val, dict):
        return "{ " + ", ".join(f"{k}: {format_js(v)}" for k, v in val.items()) + " }"
    return str(val)

def create_global_env(interpreter):
    from environment import Environment
    env = Environment()
    
    # console
    console = JSObject()
    console['log'] = BuiltinFunction(js_log)
    env.define('console', console)
    
    # Math
    math_obj = JSObject()
    math_obj['floor'] = BuiltinFunction(lambda x: math.floor(x))
    math_obj['random'] = BuiltinFunction(lambda: random.random())
    math_obj['abs'] = BuiltinFunction(lambda x: abs(x))
    math_obj['sqrt'] = BuiltinFunction(lambda x: math.sqrt(x))
    math_obj['pow'] = BuiltinFunction(lambda x, y: x ** y)
    math_obj['round'] = BuiltinFunction(lambda x: round(x))
    math_obj['ceil'] = BuiltinFunction(lambda x: math.ceil(x))
    env.define('Math', math_obj)
    
    # Date
    def js_date():
        d = JSObject()
        now = datetime.now()
        d['getTime'] = BuiltinFunction(lambda: int(time.time() * 1000))
        d['getFullYear'] = BuiltinFunction(lambda: now.year)
        return d
    env.define('Date', BuiltinFunction(js_date))
    
    # Global methods
    env.define('parseInt', BuiltinFunction(lambda x: int(float(x))))
    
    return env

def handle_member_access(obj, prop, computed=False):
    if isinstance(obj, list):
        if isinstance(prop, (int, float)):
            idx = int(prop)
            if 0 <= idx < len(obj):
                return obj[idx]
            return None
        if prop == 'length':
            return len(obj)
        if prop == 'push':
            return BuiltinFunction(lambda x: obj.append(x))
        if prop == 'pop':
            return BuiltinFunction(lambda: obj.pop() if obj else None)
        if prop == 'join':
            return BuiltinFunction(lambda sep=",": sep.join(format_js(x) for x in obj))
        if prop == 'reverse':
            def js_reverse():
                obj.reverse()
                return obj
            return BuiltinFunction(js_reverse)
        if prop == 'map':
            return BuiltinFunction(lambda callback: [callback(x, i, obj) for i, x in enumerate(obj)])
        if prop == 'filter':
            return BuiltinFunction(lambda callback: [x for i, x in enumerate(obj) if callback(x, i, obj)])
        if prop == 'reduce':
            def js_reduce(callback, initial=None):
                it = iter(enumerate(obj))
                if initial is None:
                    try:
                        _, acc = next(it)
                    except StopIteration:
                        raise TypeError("Reduce of empty array with no initial value")
                else:
                    acc = initial
                for i, x in it:
                    acc = callback(acc, x, i, obj)
                return acc
            return BuiltinFunction(js_reduce)
        if prop == 'find':
            def js_find(callback):
                for i, x in enumerate(obj):
                    if callback(x, i, obj): return x
                return None
            return BuiltinFunction(js_find)
        if prop == 'indexOf':
            return BuiltinFunction(lambda x: obj.index(x) if x in obj else -1)
        if prop == 'includes':
            return BuiltinFunction(lambda x: x in obj)
        if prop == 'sort':
            return BuiltinFunction(lambda: sorted(obj)) # Simplified
        if prop == 'slice':
            return BuiltinFunction(lambda start, end=None: obj[start:end])
        if prop == 'forEach':
            def js_forEach(callback):
                for i, x in enumerate(obj):
                    callback(x, i, obj)
            return BuiltinFunction(js_forEach)
        if prop == 'split': # For strings
            pass
    
    if isinstance(obj, str):
        if prop == 'length':
            return len(obj)
        if prop == 'split':
            return BuiltinFunction(lambda s="": list(obj) if s == "" else obj.split(s))
        if prop == 'toUpperCase':
            return BuiltinFunction(lambda: obj.upper())
        if prop == 'toLowerCase':
            return BuiltinFunction(lambda: obj.lower())
        if prop == 'substring' or prop == 'slice':
            return BuiltinFunction(lambda start, end=None: obj[start:end])
        if prop == 'trim':
            return BuiltinFunction(lambda: obj.strip())
        if prop == 'includes':
            return BuiltinFunction(lambda s: s in obj)
        if prop == 'indexOf':
            return BuiltinFunction(lambda s: obj.find(s))
        if prop == 'startsWith':
            return BuiltinFunction(lambda s: obj.startswith(s))
        if prop == 'endsWith':
            return BuiltinFunction(lambda s: obj.endswith(s))
        if prop == 'replace':
            return BuiltinFunction(lambda old, new: obj.replace(old, new, 1))
        if prop == 'replaceAll':
            return BuiltinFunction(lambda old, new: obj.replace(old, new))

    if isinstance(obj, dict):
        return obj.get(prop)
    
    return None
