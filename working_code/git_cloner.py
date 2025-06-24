import os
import git
import shutil
from pathlib import Path
from language_build import get_parser

class RepoParser:
    def __init__(self, repos_dir="cloned_repos"):
        self.repos_dir = repos_dir
        self.supported_extensions = {'.c', '.cpp', '.py', '.js', '.java'}
        
        # Create directory for cloned repos if it doesn't exist
        os.makedirs(repos_dir, exist_ok=True)
    
    def clone_repo(self, repo_url):
        """Clone a repository from GitHub."""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.repos_dir, repo_name)
            
            # Remove existing repo if it exists
            if os.path.exists(repo_path):
                try:
                    shutil.rmtree(repo_path)
                except PermissionError:
                    print(f"Permission error while removing {repo_path}")
                    print("Please try:")
                    print(f"1. Close any programs that might be using files in {repo_path}")
                    print("2. Run this script with administrator privileges")
                    return None
            
            # Clone the repository
            print(f"Cloning {repo_url}...")
            try:
                repo = git.Repo.clone_from(repo_url, repo_path)
                print(f"Successfully cloned to {repo_path}")
                return repo_path
            except git.exc.GitCommandError as e:
                print(f"Git command error: {str(e)}")
                return None
            except PermissionError as e:
                print(f"Permission error while cloning: {str(e)}")
                print("Please try running the script with administrator privileges")
                return None
        except Exception as e:
            print(f"Error cloning repository: {str(e)}")
            return None

    def find_supported_files(self, repo_path):
        """Find all supported files in the repository."""
        supported_files = []
        for root, _, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_extensions:
                    full_path = os.path.join(root, file)
                    supported_files.append(full_path)
        return supported_files

    def extract_elements(self, node, source_code):
        """Extract specific elements from an AST node."""
        elements = {
            'keywords_argument': [],
            'identifiers': set(),  # Changed to set to track unique identifiers
            'comments': [],
            'literals': [],
            'classes': set(),  # Using a set to avoid duplicates
            'functions': [],
            'variables': set(),  # Track variables
            'docstrings': []    # Track docstrings
        }
        
        # Keep track of all unique node types we see
        seen_node_types = set()
        
        def is_docstring(node):
            """Helper function to determine if a node is a docstring."""
            if node.type == 'expression_statement':
                # Must have a string as first child
                if not (node.children and node.children[0].type in ('string', 'string_literal')):
                    return False
                
                # Must be first statement in its parent block
                parent = node.parent
                if not parent:
                    return False
                
                if parent.type == 'module':
                    # For modules, must be the first non-comment statement
                    for child in parent.children:
                        if child.type not in ('comment', 'line_comment', 'block_comment'):
                            return child == node
                elif parent.type == 'block':
                    # For blocks, parent's parent must be class or function definition
                    grand_parent = parent.parent
                    if not grand_parent or grand_parent.type not in ('class_definition', 'function_definition'):
                        return False
                    # Must be first statement in the block
                    for child in parent.children:
                        if child.type not in ('comment', 'line_comment', 'block_comment'):
                            return child == node
                
            return False
        
        def visit_node(node):
            # Track unique node types
            #seen_node_types.add(node.type)
            
            # Handle different node types based on language
            if node.type == 'keyword_argument':
                elements['keywords_argument'].append(node.text.decode('utf8'))
            if node.type == 'identifier':
                elements['identifiers'].add(node.text.decode('utf8'))
            elif node.type in ('comment', 'line_comment', 'block_comment'):
                elements['comments'].append(node.text.decode('utf8'))
            elif node.type in ('string_literal', 'number_literal', 'string', 'number', 'integer', 'float'):
                text = node.text.decode('utf8')
                print(f"Found potential literal: {text}, type: {node.type}, parent type: {node.parent.type if node.parent else 'None'}")
                # Skip module name string, docstrings, and comparison literals
                if (text != '"__main__"' and 
                    not is_docstring(node) and 
                    not (node.parent and is_docstring(node.parent)) and
                    not (node.parent and node.parent.type == 'comparison_operator')):
                    # For string literals, keep only the content
                    if node.type in ('string_literal', 'string'):
                        text = text.strip('"').strip("'")
                    print(f"Adding literal: {text}")
                    elements['literals'].append(text)
            elif node.type in ('class_definition', 'class_declaration', 'class', 'class_specifier'):
                # For classes, only store the class name from the identifier node
                for child in node.children:
                    if child.type == 'identifier':
                        elements['classes'].add(child.text.decode('utf8'))
                        break  # Only get the first identifier (class name)
            elif node.type in ('function_definition', 'method_definition', 'function_declaration', 'method_declaration'):
                # Get the function name from the identifier child
                for child in node.children:
                    if child.type == 'identifier':
                        elements['functions'].append(child.text.decode('utf8'))
                        break
            
            # Variable detection
            elif node.type == 'assignment':
                # Get the left side of the assignment
                if node.children:
                    left_side = node.children[0]
                    if left_side.type == 'identifier':
                        var_name = left_side.text.decode('utf8')
                        if var_name != 'self':  # Exclude 'self'
                            elements['variables'].add(var_name)
                    elif left_side.type == 'attribute':
                        # Handle attribute assignments (e.g., self.var = ...)
                        for child in left_side.children:
                            if child.type == 'identifier':
                                var_name = child.text.decode('utf8')
                                if var_name != 'self':  # Exclude 'self'
                                    elements['variables'].add(var_name)
            elif node.type == 'global_statement':
                # Get global variables
                for child in node.children:
                    if child.type == 'identifier':
                        var_name = child.text.decode('utf8')
                        if var_name != 'self':  # Exclude 'self'
                            elements['variables'].add(var_name)
            elif node.type == 'augmented_assignment':
                # Get variables from augmented assignments (+=, -=, etc.)
                if node.children:
                    left_side = node.children[0]
                    if left_side.type == 'identifier':
                        var_name = left_side.text.decode('utf8')
                        if var_name != 'self':  # Exclude 'self'
                            elements['variables'].add(var_name)
            elif node.type == 'for_statement':
                # Get loop variables
                if node.children:
                    target = node.children[1]  # The loop variable is typically the second child
                    if target.type == 'identifier':
                        var_name = target.text.decode('utf8')
                        if var_name != 'self':  # Exclude 'self'
                            elements['variables'].add(var_name)
            
            # Docstring detection
            if is_docstring(node):
                if node.type == 'string':
                    docstring = node.text.decode('utf8')
                else:
                    docstring = node.children[0].text.decode('utf8')
                # Remove common string delimiters
                docstring = docstring.strip('"""').strip("'''").strip('"').strip("'")
                elements['docstrings'].append(docstring)
            
            # Recursively visit all children
            for child in node.children:
                visit_node(child)
        
        visit_node(node)
        
        # # Print all unique node types we found
        # print("\nAll node types found:")
        # for node_type in sorted(seen_node_types):
        #     print(f"- {node_type}")
        
        # Convert sets back to lists for consistent interface
        elements['classes'] = list(elements['classes'])
        elements['variables'] = list(elements['variables'])
        elements['identifiers'] = list(elements['identifiers'])  # Convert identifiers set to list
        return elements

    def parse_file(self, file_path):
        """Parse a single file and return its AST information."""
        try:
            _, ext = os.path.splitext(file_path)
            parser, lang_name = get_parser(ext)
            
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            tree = parser.parse(source_code)
            elements = self.extract_elements(tree.root_node, source_code)
            
            return {
                'file_path': file_path,
                'language': lang_name,
                'ast': tree.root_node,
                'elements': elements,
                'success': True
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'success': False
            }

    def analyze_repo(self, repo_url):
        """Clone and analyze a repository."""
        # Clone the repository
        repo_path = self.clone_repo(repo_url)
        if not repo_path:
            return None

        # Find all supported files
        files = self.find_supported_files(repo_path)
        print(f"\nFound {len(files)} supported files")

        # Parse each file
        results = []
        for file_path in files:
            print(f"\nParsing: {os.path.relpath(file_path, repo_path)}")
            result = self.parse_file(file_path)
            results.append(result)

        return results

def main():
    parser = RepoParser()
    
    # # Test files
    # test_files = [
    #     "test_files/test_with_docstrings.py",

    # ]
    
    # for test_file in test_files:
    #     print(f"\nTesting file: {test_file}")
    #     result = parser.parse_file(test_file)
    #     if result['success']:
    #         print(f"\nFile: {os.path.basename(test_file)}")
    #         print(f"Language: {result['language']}")
    #         elements = result['elements']
    #         print(f"Found:")
    #         print(f"- {len(elements['keywords_argument'])} keywords_argument")
    #         print(f"- {len(elements['identifiers'])} unique identifiers")
    #         print(f"Identifiers found: {sorted(elements['identifiers'])}")
    #         print(f"- {len(elements['comments'])} comments")
    #         print(f"- {len(elements['literals'])} literals")
    #         print(f"- {len(elements['classes'])} classes")
    #         if elements['classes']:
    #             print(f"Classes found: {sorted(elements['classes'])}")
    #         print(f"- {len(elements['functions'])} functions")
    #         if elements['functions']:
    #             print(f"Functions found: {sorted(elements['functions'])}")
    #         print(f"- {len(elements['variables'])} variables")
    #         if elements['variables']:
    #             print(f"Variables found: {sorted(elements['variables'])}")
    #         print(f"- {len(elements['docstrings'])} docstrings")
    #         if elements['docstrings']:
    #             print("Docstrings found:")
    #             for ds in elements['docstrings']:
    #                 print(f"  - {ds}")
    
    # Example repositories to parse
    repos = [
        "https://github.com/fighting41love/funNLP",
        "https://github.com/modood/Administrative-divisions-of-China",
        "https://github.com/cxasm/notepad--",
        "https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov",
        "https://github.com/mumuy/data_location",
        "https://github.com/doublechaintech/scm-biz-suite",
        "https://github.com/BinNong/meet-libai",
        "https://github.com/cn/GB2260",
        "https://github.com/mc-zone/IDValidator",
        "https://github.com/atguigu01/Shopping",
        "https://github.com/LCTT/LCBot",
        "https://github.com/alantang1977/X",
        "https://github.com/ethan-li-coding/AD-Census",
        "https://github.com/jxlwqq/id-validator.py",
        "https://github.com/yxcs/poems-db",
        "https://github.com/lichao315/Calendar",
        "https://github.com/risesoft-y9/Network-Drive",
        "https://github.com/GuidoPaul/CAIL2019",
        "https://github.com/chenluyong/OEasyScreenshot",
        "https://github.com/Tele-AI/TeleChat2",
    ]
    
    for repo_url in repos:
        print(f"\nProcessing repository: {repo_url}")
        results = parser.analyze_repo(repo_url)
        
        if results:
            # Print summary
            successful = sum(1 for r in results if r['success'])
            print(f"\nResults for {repo_url}:")
            print(f"Total files processed: {len(results)}")
            print(f"Successfully parsed: {successful}")
            print(f"Failed to parse: {len(results) - successful}")
            
            # Print detailed elements for each successful file
            for result in results:
                if result['success']:
                    print(f"\nFile: {os.path.basename(result['file_path'])}")
                    print(f"Language: {result['language']}")
                    elements = result['elements']
                    print(f"Found:")
                    print(f"- {len(elements['keywords_argument'])} keywords_argument")
                    print(f"Keywords found: {sorted(elements['keywords_argument'])}")
                    print(f"- {len(elements['identifiers'])} unique identifiers")
                    print(f"Identifiers found: {sorted(elements['identifiers'])}")
                    print(f"- {len(elements['comments'])} comments")
                    print(f"- {(elements['comments'])} comments")
                    print(f"- {len(elements['literals'])} literals")
                    print(f"Literals found: {sorted(elements['literals'])}")
                    print(f"- {len(elements['classes'])} classes")
                    print(f"Classes found: {sorted(elements['classes'])}")
                    print(f"- {len(elements['functions'])} functions")
                    print(f"Functions found: {sorted(elements['functions'])}")
                    print(f"- {len(elements['variables'])} variables")
                    if elements['variables']:
                        print(f"Variables found: {sorted(elements['variables'])}")
                    print(f"- {len(elements['docstrings'])} docstrings")
                    if elements['docstrings']:
                        print("Docstrings found:")
                        for ds in elements['docstrings']:
                            print(f"  - {ds}")

if __name__ == "__main__":
    # Only try to clean up if the directory exists
    if os.path.exists("cloned_repos"):
        shutil.rmtree("cloned_repos")
    main()
#Output in JSON format