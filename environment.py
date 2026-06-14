class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent
        self.constants = set()

    def define(self, name, value, is_const=False):
        self.values[name] = value
        if is_const:
            self.constants.add(name)

    def assign(self, name, value):
        if name in self.values:
            if name in self.constants:
                raise TypeError(f"Assignment to constant variable {name}")
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise NameError(f"Variable {name} is not defined")

    def lookup(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.lookup(name)
        raise NameError(f"Variable {name} is not defined")

    def has(self, name):
        if name in self.values:
            return True
        if self.parent:
            return self.parent.has(name)
        return False
