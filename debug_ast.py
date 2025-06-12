from tree_sitter import Language, Parser
import os

# Load the languages
CGRAMMAR = Language('build/my-languages.so', 'c')
CPPGRAMMAR = Language('build/my-languages.so', 'cpp')

def print_ast(node, level=0):
    print('  ' * level + f"Type: {node.type}, Text: {node.text.decode('utf8')}")
    for child in node.children:
        print_ast(child, level + 1)

def analyze_file(file_path, language):
    with open(file_path, 'rb') as f:
        source_code = f.read()
    
    parser = Parser()
    if language == 'c':
        parser.set_language(CGRAMMAR)
    else:
        parser.set_language(CPPGRAMMAR)
    
    tree = parser.parse(source_code)
    print(f"\nAnalyzing {file_path} with {language} grammar:")
    print_ast(tree.root_node)

if __name__ == "__main__":
    analyze_file("test_cases/test_c.c", "c")
    analyze_file("test_cases/test_cpp.cpp", "cpp") 