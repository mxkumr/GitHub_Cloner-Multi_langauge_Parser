class SimpleClass:
    def __init__(self):
        self.value = 42

    def method(self):
        return self.value

class InheritedClass(SimpleClass):
    def __init__(self):
        super().__init__()
        self.name = "test"

    def another_method(self):
        return self.name

# Class with decorators
class DecoratedClass:
    @property
    def prop(self):
        return "property"

    @staticmethod
    def static_method():
        return "static"

# Empty class
class EmptyClass:
    pass 