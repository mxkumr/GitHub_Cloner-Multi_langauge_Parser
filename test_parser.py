import unittest
from git_cloner import RepoParser
import os

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = RepoParser()
        
        # Create a test file with known elements
        self.test_content = '''#!/usr/bin/env python3
"""This is a module docstring."""

from typing import List, Dict
import math

# Global constant
MAX_VALUE = 100

def calculate_square(x: float) -> float:
    """Calculate the square of a number."""
    return x * x

class MathOperations:
    """A class for mathematical operations."""
    
    def __init__(self, value: float):
        self.value = value
    
    def process(self) -> Dict[str, float]:
        result = {}
        for i in range(3):
            if i > 0:
                result[str(i)] = calculate_square(i)
            else:
                continue
        return result

def main():
    try:
        math_ops = MathOperations(5.0)
        result = math_ops.process()
        assert result is not None
    except Exception as e:
        pass

if __name__ == "__main__":
    main()
'''
        # Write test content to a file
        self.test_file = "test_sample.py"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(self.test_content)
    
    def tearDown(self):
        # Clean up test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def calculate_accuracy(self, expected, actual):
        """Calculate precision, recall, and F1 score."""
        expected_set = set(expected)
        actual_set = set(actual)
        
        true_positives = len(expected_set.intersection(actual_set))
        false_positives = len(actual_set - expected_set)
        false_negatives = len(expected_set - actual_set)
        
        precision = true_positives / len(actual_set) if actual_set else 0
        recall = true_positives / len(expected_set) if expected_set else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def test_parser_accuracy(self):
        """Test if the parser correctly identifies all elements and calculate accuracy metrics."""
        result = self.parser.parse_file(self.test_file)
        self.assertTrue(result['success'])
        
        elements = result['elements']
        
        # Expected values for each category
        expected = {
            'identifiers': {
                'List', 'Dict', 'math', 'MAX_VALUE', 'calculate_square', 'x', 
                'MathOperations', 'value', 'self', 'process', 'result', 'i', 
                'range', 'str', 'main', 'math_ops', 'Exception', 'e', '__name__',
                'typing', 'float', '__init__'
            },
            'classes': {'MathOperations'},
            'functions': {'calculate_square', 'process', '__init__', 'main'},
            'variables': {'MAX_VALUE', 'value', 'result', 'i', 'math_ops'},
            'docstrings': {
                'This is a module docstring.',
                'Calculate the square of a number.',
                'A class for mathematical operations.'
            },
            'comments': {'#!/usr/bin/env python3\r', '# Global constant\r'},
            'literals': {'100', '3', '5.0'}
        }
        
        # Calculate accuracy for each category
        accuracy_scores = {}
        total_f1 = 0
        categories = 0
        
        print("\nAccuracy Metrics:")
        print("=" * 50)
        
        for category in expected:
            actual = set(elements[category])
            metrics = self.calculate_accuracy(expected[category], actual)
            accuracy_scores[category] = metrics
            
            print(f"\n{category.upper()}:")
            print(f"Precision: {metrics['precision']:.2%}")
            print(f"Recall: {metrics['recall']:.2%}")
            print(f"F1 Score: {metrics['f1']:.2%}")
            print(f"True Positives: {metrics['true_positives']}")
            print(f"False Positives: {metrics['false_positives']}")
            print(f"False Negatives: {metrics['false_negatives']}")
            
            if metrics['false_positives'] > 0:
                print("Extra items found:", actual - expected[category])
            if metrics['false_negatives'] > 0:
                print("Missing items:", expected[category] - actual)
            
            total_f1 += metrics['f1']
            categories += 1
        
        overall_accuracy = total_f1 / categories
        print("\nOVERALL ACCURACY:")
        print(f"Average F1 Score: {overall_accuracy:.2%}")
        
        # Assert that overall accuracy is above 95%
        self.assertGreaterEqual(overall_accuracy, 0.95, "Overall accuracy should be at least 95%")

if __name__ == '__main__':
    unittest.main() 