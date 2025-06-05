import os
from language_build import get_parser

def test_file(file_path):
    _, ext = os.path.splitext(file_path)
    try:
        parser, lang_name = get_parser(ext)
        
        with open(file_path, 'rb') as f:
            source_code = f.read()
        
        tree = parser.parse(source_code)
        root_node = tree.root_node
        
        print(f"\nTesting {file_path}:")
        print(f"Language: {lang_name}")
        print(f"Tree type: {root_node.type}")
        print(f"Number of children: {len(root_node.children)}")
        print(f"First child type: {root_node.children[0].type if root_node.children else 'No children'}")
        print("Parsing successful!")
        
    except Exception as e:
        print(f"\nError parsing {file_path}:")
        print(str(e))

def main():
    test_files_dir = "test_files"
    for file_name in os.listdir(test_files_dir):
        file_path = os.path.join(test_files_dir, file_name)
        test_file(file_path)

if __name__ == "__main__":
    main() 