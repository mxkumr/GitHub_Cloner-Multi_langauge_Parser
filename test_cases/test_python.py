"""
This is a docstring for the module.
Testing parser accuracy with Python code.
"""

class TestClass:
    """Class docstring for TestClass."""
    
    def __init__(self, name):
        # Initialize instance variables
        self.name = name
        self.value = 42  # Magic number
    
    def calculate(self, x):
        # Calculate something
        result = x * self.value
        return result

class HelperClass:
    def process_data(self, data):
        # Process the input data
        processed = data.upper()
        return processed

def main():
    # Create instances and test
    test_obj = TestClass("test")
    helper = HelperClass()
    
    # Test the functionality
    result = test_obj.calculate(10)
    print(result) 