# repo_parser.py
import os
import git
import shutil
from typing import Dict, List, Any
from pathlib import Path
from language_build import get_parser

class RepoElementParser:
    def __init__(self, repos_dir="cloned_repos"):
        self.repos_dir = repos_dir
        self.supported_extensions = {'.py', '.java', '.cpp', '.c', '.js'}  # Add more as needed
        
        # Create directory for cloned repos if it doesn't exist
        os.makedirs(repos_dir, exist_ok=True)
        
        # Standard library identifiers to exclude
        self.std_lib_identifiers = {
            'cout', 'endl', 'cin', 'cerr', 'clog',
            'string', 'vector', 'map', 'set', 'list',
            'make_unique', 'make_shared', 'unique_ptr', 'shared_ptr',
            'cout', 'endl', 'cin', 'cerr', 'clog',
            'printf', 'scanf', 'malloc', 'free', 'NULL',
            'stdout', 'stdin', 'stderr',
            'print', 'input', 'range', 'len', 'str', 'int', 'float',
            'list', 'dict', 'set', 'tuple',
            'console', 'document', 'window', 'require', 'module',
            'exports', 'import', 'from', 'as'
        }
        
        self.elements = {
            'identifiers': set(),
            'literals': [],
            'variables': set(),
            'comments': [],
            'docstrings': [],
            'functions': set(),
            'classes': set()
        }

    def clone_repo(self, repo_url: str) -> str:
        """Clone a repository from GitHub."""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.repos_dir, repo_name)
            
            # Remove existing repo if it exists
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            
            # Clone the repository
            print(f"Cloning {repo_url}...")
            git.Repo.clone_from(repo_url, repo_path)
            print(f"Successfully cloned to {repo_path}")
            return repo_path
            
        except Exception as e:
            print(f"Error cloning repository: {str(e)}")
            return ""

    def find_source_files(self, repo_path: str) -> List[str]:
        """Find all supported source files in the repository."""
        source_files = []
        for root, _, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in Path(root).parts:
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_extensions:
                    full_path = os.path.join(root, file)
                    source_files.append(full_path)
        return source_files

    def _is_docstring(self, node) -> bool:
        """Determine if a string node is a docstring."""
        if node.type != 'expression_statement':
            return False
            
        parent = node.parent
        if not parent:
            return False
            
        if parent.type == 'module':
            for child in parent.children:
                if child.type not in ('comment', 'line_comment'):
                    return child == node
        elif parent.type == 'block':
            grand_parent = parent.parent
            if not grand_parent or grand_parent.type not in ('class_definition', 'function_definition'):
                return False
            for child in parent.children:
                if child.type not in ('comment', 'line_comment'):
                    return child == node
                    
        return False

    def _is_std_lib_identifier(self, name: str) -> bool:
        """Check if an identifier is from the standard library."""
        return name in self.std_lib_identifiers

    def _collect_class_names(self, node, class_names):
        """First pass: Collect all class names in the AST."""
        # Handle different language-specific class definitions
        if node.type in ('class_definition', 'class_declaration', 'class_specifier', 'struct_specifier'):
            # For Python, Java, JavaScript classes
            if node.type in ('class_definition', 'class_declaration'):
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = child.text.decode('utf8')
                        class_names.add(class_name)
                        break
            # For C++ classes and C structs
            elif node.type in ('class_specifier', 'struct_specifier'):
                for child in node.children:
                    if child.type == 'type_identifier':
                        class_name = child.text.decode('utf8')
                        class_names.add(class_name)
                        break
        
        for child in node.children:
            self._collect_class_names(child, class_names)

    def _is_variable(self, node, class_names=None) -> bool:
        """Determine if an identifier node represents a variable."""
        if node.type != 'identifier':
            return False
        name = node.text.decode('utf8')
        if self._is_std_lib_identifier(name):
            return False
        if class_names and name in class_names:
            return False
        if node.parent and node.parent.type in ('function_definition', 'class_definition', 'constructor_declaration', 'constructor_or_destructor_definition'):
            return False
        if node.parent and node.parent.type == 'call':
            return False
        if node.parent and node.parent.type in ('import_statement', 'import_from_statement'):
            return False
        if name in ('__name__', '__main__', '__file__', 'this', 'super'):
            return False
        if node.parent and node.parent.type == 'method_definition':
            return False
        if node.parent and node.parent.type == 'function_definition':
            return False
        if node.parent and node.parent.type == 'class_definition':
            return False
        if node.parent and node.parent.parent and node.parent.parent.type == 'class_definition':
            if node.parent.type == 'block' and any(child.type == 'method_definition' for child in node.parent.children):
                return False
        if node.parent and node.parent.parent and node.parent.parent.type == 'function_definition':
            if node.parent.type == 'block' and any(child.type == 'method_definition' for child in node.parent.children):
                return False
        if node.parent and node.parent.parent and node.parent.parent.type == 'class_definition':
            if node.parent.type == 'block' and any(child.type == 'function_definition' for child in node.parent.children):
                return False
        return True

    def _extract_elements(self, node, source_code: bytes, class_names=None) -> None:
        node_type = node.type
        node_text = node.text.decode('utf8')

        # Handle class definitions for all languages
        if node_type in ('class_definition', 'class_declaration', 'class_specifier', 'struct_specifier'):
            # For Python, Java, JavaScript classes
            if node_type in ('class_definition', 'class_declaration'):
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = child.text.decode('utf8')
                        if not self._is_std_lib_identifier(class_name):
                            self.elements['classes'].add(class_name)
                            self.elements['identifiers'].add(class_name)
                        break
            # For C++ classes and C structs
            elif node_type in ('class_specifier', 'struct_specifier'):
                for child in node.children:
                    if child.type == 'type_identifier':
                        class_name = child.text.decode('utf8')
                        if not self._is_std_lib_identifier(class_name):
                            self.elements['classes'].add(class_name)
                            self.elements['identifiers'].add(class_name)
                        break

        # Handle code elements
        if node_type == 'identifier':
            name = node_text
            if not self._is_std_lib_identifier(name):
                if name not in ('__name__', '__main__', '__file__', 'this', 'super'):
                    self.elements['identifiers'].add(name)
                if self._is_variable(node, class_names):
                    self.elements['variables'].add(name)
        elif node_type in ('string_literal', 'string'):
            text = node_text.strip('"\'')
            if text:  # Only add non-empty strings
                if self._is_docstring(node.parent):
                    self.elements['docstrings'].append(text)
                else:
                    self.elements['literals'].append(text)
        elif node_type in ('number_literal', 'integer', 'float'):
            self.elements['literals'].append(node_text)
        elif node_type in ('comment', 'line_comment'):
            text = node_text.lstrip('#').strip()
            self.elements['comments'].append(text)
        elif node_type in ('function_definition', 'constructor_declaration', 'constructor_or_destructor_definition', 'method_definition'):
            for child in node.children:
                if child.type == 'identifier':
                    func_name = child.text.decode('utf8')
                    if not self._is_std_lib_identifier(func_name) and func_name != '__init__':
                        self.elements['functions'].add(func_name)
                        self.elements['identifiers'].add(func_name)
                    break

        # Recursively process children
        for child in node.children:
            self._extract_elements(child, source_code, class_names)

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single file and extract all code elements."""
        try:
            ext = os.path.splitext(file_path)[1]
            parser, lang_name = get_parser(ext)
            
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            tree = parser.parse(source_code)
            
            # Reset elements for new file
            self.elements = {k: set() if isinstance(v, set) else [] for k, v in self.elements.items()}
            
            # First pass: collect all class names
            class_names = set()
            self._collect_class_names(tree.root_node, class_names)
            
            # Second pass: extract all elements, using class_names
            self._extract_elements(tree.root_node, source_code, class_names)
            
            result = {
                'identifiers': sorted(list(self.elements['identifiers'])),
                'literals': self.elements['literals'],
                'variables': sorted(list(self.elements['variables'])),
                'comments': self.elements['comments'],
                'docstrings': self.elements['docstrings'],
                'functions': sorted(list(self.elements['functions'])),
                'classes': sorted(list(self.elements['classes']))
            }
            
            return {
                'success': True,
                'language': lang_name,
                'file_path': file_path,
                'elements': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """Analyze an entire GitHub repository."""
        # Clone the repository
        repo_path = self.clone_repo(repo_url)
        if not repo_path:
            return {
                'success': False,
                'error': 'Failed to clone repository'
            }

        # Find all source files
        source_files = self.find_source_files(repo_path)
        if not source_files:
            return {
                'success': False,
                'error': 'No supported source files found'
            }

        # Analyze each file
        file_analyses = []
        repo_elements = {
            'identifiers': set(),
            'literals': [],
            'variables': set(),
            'comments': [],
            'docstrings': [],
            'functions': set(),
            'classes': set()
        }

        for file_path in source_files:
            result = self.parse_file(file_path)
            if result['success']:
                file_analyses.append(result)
                
                # Aggregate elements
                elements = result['elements']
                for key in repo_elements:
                    if isinstance(repo_elements[key], set):
                        repo_elements[key].update(elements[key])
                    else:
                        repo_elements[key].extend(elements[key])

        # Convert sets to sorted lists for final output
        final_elements = {
            'identifiers': sorted(list(repo_elements['identifiers'])),
            'literals': repo_elements['literals'],
            'variables': sorted(list(repo_elements['variables'])),
            'comments': repo_elements['comments'],
            'docstrings': repo_elements['docstrings'],
            'functions': sorted(list(repo_elements['functions'])),
            'classes': sorted(list(repo_elements['classes']))
        }

        return {
            'success': True,
            'repository_url': repo_url,
            'total_files': len(source_files),
            'analyzed_files': len(file_analyses),
            'repository_elements': final_elements,
            'file_analyses': file_analyses
        }

def main():
    parser = RepoElementParser()
    
    # Get repository URL
    repo_url = input("Enter GitHub repository URL: ")
    
    # Analyze repository
    result = parser.analyze_repo(repo_url)
    
    if result['success']:
        print(f"\nRepository Analysis Complete!")
        print(f"Total files analyzed: {result['analyzed_files']}/{result['total_files']}")
        print("\nRepository-wide Elements:")
        print("=" * 50)
        
        elements = result['repository_elements']
        for element_type, items in elements.items():
            print(f"\n{element_type.upper()} ({len(items)}):")
            if items:
                for item in items[:10]:  # Show first 10 items
                    print(f"  - {item}")
                if len(items) > 10:
                    print(f"  ... and {len(items) - 10} more")
            else:
                print("  (none found)")
        
        # Save detailed results to file
        import json
        output_file = "repo_analysis_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {output_file}")
    else:
        print(f"Error analyzing repository: {result['error']}")

if __name__ == "__main__":
    main()