"""This is a module level docstring."""

# Global variables
global_var = 42
another_global = "test"

class TestClass:
    """This is a class docstring."""
    
    class_var = "class variable"
    
    def __init__(self):
        """Constructor docstring."""
        self.instance_var = 123
        self._private_var = "private"
    
    def method(self):
        """This is a method docstring."""
        local_var = "local"
        local_var += " modified"
        return local_var

def standalone_function():
    """This is a function docstring."""
    result = 0
    for i in range(10):
        result += i
    return result 