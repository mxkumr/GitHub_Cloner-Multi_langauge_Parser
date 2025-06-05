from tree_sitter import Language, Parser
import tree_sitter
import os

# Make sure the build directory exists
os.makedirs('build', exist_ok=True)
# print(Language.)
# # Build the languages
Language.build_library(
    'build/my-languages.so',
    [
        './tree-sitter-c',
        './tree-sitter-cpp',
        './tree-sitter-python',
        './tree-sitter-javascript',
        './tree-sitter-java'
    ]
)

# Load the languages
CGRAMMAR = Language('build/my-languages.so', 'c')
CPPGRAMMAR = Language('build/my-languages.so', 'cpp')
PYTHONGRAMMAR = Language('build/my-languages.so', 'python')
JAVASCRIPTGRAMMAR = Language('build/my-languages.so', 'javascript')
JAVAGRAMMAR = Language('build/my-languages.so', 'java')

# Create a parser
PARSERS = {
    '.c': (CGRAMMAR, 'c'),
    '.cpp': (CPPGRAMMAR, 'cpp'),
    '.py': (PYTHONGRAMMAR, 'python'),
    '.js': (JAVASCRIPTGRAMMAR, 'javascript'),
    '.java': (JAVAGRAMMAR, 'java'),
}

# Parser function
def get_parser(file_extension):
    if file_extension in PARSERS:
        lang_obj, lang_name = PARSERS[file_extension]
        parser = Parser()
        parser.set_language(lang_obj)
        return parser, lang_name
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
    
    
