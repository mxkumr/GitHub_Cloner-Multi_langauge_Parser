import unittest
from git_cloner import RepoParser
from language_detector import LanguageDetector
import os

class TestComplexParser(unittest.TestCase):
    def setUp(self):
        self.parser = RepoParser()
        self.language_detector = LanguageDetector()
        self.test_file = "test_complex.py"
    
    def tearDown(self):
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
            'false_negatives': false_negatives,
            'missed_items': expected_set - actual_set,
            'extra_items': actual_set - expected_set
        }
    
    def analyze_language_distribution(self, items):
        """Analyze language distribution in a list of items."""
        if not items:
            return {}
        
        lang_dist = {}
        for item in items:
            result = self.language_detector.analyze_text(item)
            lang = result.primary_language
            lang_dist[lang] = lang_dist.get(lang, 0) + 1
        
        total = sum(lang_dist.values())
        return {lang: count/total for lang, count in lang_dist.items()}
    
    def test_complex_parsing(self):
        """Test parsing of complex multi-language code."""
        result = self.parser.parse_file(self.test_file)
        self.assertTrue(result['success'])
        
        elements = result['elements']
        
        # Expected elements with their languages
        expected = {
            'classes': {
                'names': {'BaseHandler', 'データ処理', '用户数据', '高度な計算'},
                'languages': {'en', 'ja', 'zh'}
            },
            'functions': {
                'names': {'process', '_処理アイテム', 'calculate_statistics', '計算実行', 'main', '加算', '乗算'},
                'languages': {'en', 'ja'}
            },
            'variables': {
                'names': {
                    'MAX_重试_COUNT', '数据库_TIMEOUT', 'デバッグ_MODE',
                    '名字', '年龄', 'メール', 'データ', '_処理済み',
                    '数値リスト', '结果', '現在値', '_履歴', '操作', '値'
                },
                'languages': {'zh', 'ja'}
            },
            'docstrings': {
                'content': [
                    '多语言测试模块\nマルチ言語テストモジュール\nMulti-language test module',
                    '用户数据类\nRepresents user data with mixed language fields',
                    'Base handler for data processing',
                    'データ処理クラス\nData processing class with Japanese elements',
                    'Process the data',
                    'Process individual items',
                    'Calculate statistics for a list of numbers\n计算数字列表的统计信息',
                    'Advanced calculations with nested functions and complex logic',
                    'Execute calculation with operation and value'
                ],
                'languages': {'en', 'ja', 'zh'}
            },
            'comments': {
                'content': [
                    '#!/usr/bin/env python3',
                    '# Global constants - Mixed languages',
                    '# Max retry count',
                    '# Database timeout',
                    '# Debug mode',
                    '# Test data with mixed languages',
                    '# Test processing with Japanese data',
                    '# Test calculations'
                ],
                'languages': {'en'}
            }
        }
        
        # Test each category
        accuracy_scores = {}
        print("\nDetailed Analysis Results:")
        print("=" * 50)
        
        for category, expected_data in expected.items():
            actual_items = elements.get(category, [])
            
            # Calculate accuracy
            accuracy = self.calculate_accuracy(
                expected_data['names'] if 'names' in expected_data else expected_data['content'],
                actual_items
            )
            
            # Analyze language distribution
            actual_lang_dist = self.analyze_language_distribution(actual_items)
            
            print(f"\n{category.upper()}:")
            print(f"Precision: {accuracy['precision']:.2%}")
            print(f"Recall: {accuracy['recall']:.2%}")
            print(f"F1 Score: {accuracy['f1']:.2%}")
            print(f"True Positives: {accuracy['true_positives']}")
            print(f"False Positives: {accuracy['false_positives']}")
            print(f"False Negatives: {accuracy['false_negatives']}")
            
            if accuracy['missed_items']:
                print("Missed items:", accuracy['missed_items'])
            if accuracy['extra_items']:
                print("Extra items found:", accuracy['extra_items'])
            
            print("\nLanguage Distribution:")
            for lang, percentage in actual_lang_dist.items():
                print(f"- {lang}: {percentage:.2%}")
            
            accuracy_scores[category] = accuracy['f1']
        
        # Calculate overall accuracy
        overall_accuracy = sum(accuracy_scores.values()) / len(accuracy_scores)
        print("\nOVERALL ACCURACY:")
        print(f"Average F1 Score: {overall_accuracy:.2%}")
        
        # Assert minimum accuracy requirements
        self.assertGreaterEqual(overall_accuracy, 0.90, 
                              "Overall accuracy should be at least 90%")
        
        # Test language detection accuracy
        for category, expected_data in expected.items():
            actual_items = elements.get(category, [])
            actual_lang_dist = self.analyze_language_distribution(actual_items)
            
            # Verify that all expected languages are detected
            detected_langs = set(actual_lang_dist.keys())
            expected_langs = expected_data['languages']
            self.assertTrue(
                expected_langs.issubset(detected_langs),
                f"Missing languages in {category}: {expected_langs - detected_langs}"
            )

if __name__ == '__main__':
    unittest.main() 