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
                shutil.rmtree(repo_path)
            
            # Clone the repository
            print(f"Cloning {repo_url}...")
            git.Repo.clone_from(repo_url, repo_path)
            return repo_path
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
            'keywords': [],
            'identifiers': [],
            'comments': [],
            'keywords': [],
            'literals': [],
            'classes': [],
            'functions': []
        }
        
        def visit_node(node):
            # Handle different node types based on language
            if node.type == 'keyword':
                elements['keywords'].append(node.text.decode('utf8'))
            if node.type == 'identifier':
                elements['identifiers'].append(node.text.decode('utf8'))
            elif node.type in ('comment', 'line_comment', 'block_comment'):
                elements['comments'].append(node.text.decode('utf8'))
            elif node.type in ('string_literal', 'number_literal', 'string', 'number'):
                elements['literals'].append(node.text.decode('utf8'))
            elif node.type in ('class_definition', 'class_declaration', 'class'):
                elements['classes'].append(node.text.decode('utf8'))
            elif node.type in ('function_definition', 'method_definition', 'function_declaration', 'method_declaration'):
                elements['functions'].append(node.text.decode('utf8'))
            
            # Recursively visit all children
            for child in node.children:
                visit_node(child)
        
        visit_node(node)
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
    
    # Example repositories to parse
    repos = [
        "https://github.com/leifengwl/MoGuDing-Auto",
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
                    print(f"- {len(elements['keywords'])} keywords")
                    print(f"- {len(elements['identifiers'])} identifiers")
                    print(f"- {(elements['identifiers'])} identifiers")
                    print(f"- {len(elements['comments'])} comments")
                    print(f"- {(elements['comments'])} comments")
                    print(f"- {len(elements['literals'])} literals")
                    print(f"- {len(elements['classes'])} classes")
                    print(f"- {len(elements['functions'])} functions")

if __name__ == "__main__":
    main()
