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

"""这是模块级文档字符串"""

# 全局变量
全局变量 = 42
另一个变量 = "测试"

class 测试类:
    """这是类的文档字符串"""
    
    类变量 = "类变量值"
    
    def __init__(self):
        """构造函数的文档字符串"""
        self.实例变量 = 123
        self._私有变量 = "私有"
    
    def 方法(self):
        """这是方法的文档字符串"""
        局部变量 = "局部"
        局部变量 += " 修改"
        return 局部变量

def 独立函数():
    """这是函数的文档字符串"""
    结果 = 0
    for 计数器 in range(10):
        结果 += 计数器
    return 结果

# 创建实例并测试
测试实例 = 测试类()
print(测试实例.方法())
print(独立函数()) 

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