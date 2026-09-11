import re
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript

def extract_added_code_from_diff(diff: str) -> str:
    """Extracts only the added lines from a unified diff, stripping the '+' prefix."""
    added_lines = []
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            added_lines.append(line[1:])
    return '\n'.join(added_lines)

def get_ast_insights(diff: str) -> str:
    """
    Parses the added code using Tree-sitter and returns a summary of the AST nodes.
    Tree-sitter is resilient so it can parse partial snippets from diffs.
    """
    added_code = extract_added_code_from_diff(diff)
    if not added_code.strip():
        return ""

    # Try to guess language from diff header if possible, or just try Python and JS
    language_name = 'python'
    if 'a/' in diff and '.js' in diff or '.ts' in diff:
        language_name = 'javascript'

    parser = Parser()
    try:
        if language_name == 'python':
            parser.set_language(Language(tree_sitter_python.language(), "python"))
        else:
            parser.set_language(Language(tree_sitter_javascript.language(), "javascript"))
    except Exception:
        # Fallback if language binding fails
        return ""

    tree = parser.parse(bytes(added_code, "utf8"))
    
    # Extract unique node types
    node_types = set()
    def traverse(node):
        # Ignore basic literal and punctuation nodes to focus on structure
        if node.type.isidentifier() and len(node.type) > 1:
            node_types.add(node.type)
        for child in node.children:
            traverse(child)
            
    traverse(tree.root_node)
    
    # Filter out boring nodes
    boring_nodes = {'module', 'identifier', 'string', 'integer', 'block', 'expression_statement'}
    interesting_nodes = [nt for nt in node_types if nt not in boring_nodes]
    
    if not interesting_nodes:
        return ""
        
    return "AST Nodes detected in the added code: " + ", ".join(interesting_nodes)
