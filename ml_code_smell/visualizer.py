import ast
import sys
import os

def print_tree(node, indent=0):
    """
    Recursively prints the AST structure in a human-readable indented format.
    
    Args:
        node: The current AST node or value to print.
        indent: Current indentation level.
    """
    if isinstance(node, ast.AST):
        # Print the name of the AST node class (e.g., Module, Assign, BinOp)
        node_name = node.__class__.__name__
        print("  " * indent + f"[{node_name}]")
        
        # Iterate over all fields of the node (e.g., targets and value for an Assign node)
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                # If the field is a list (like a block of code), visit each item
                for item in value:
                    print_tree(item, indent + 1)
            else:
                # Otherwise, visit the single child node
                print_tree(value, indent + 1)
    else:
        # If it's not an AST node, it's a leaf value (like a variable name or constant)
        if node is not None:
             print("  " * (indent) + f"-> {repr(node)}")

def visualize_file(file_path):
    """
    Parses a Python file and prints its Abstract Syntax Tree (AST).
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
        # Convert source code into an AST
        tree = ast.parse(source)
        
    print(f"AST Visualization for: {file_path}")
    print("=" * 40)
    print_tree(tree)
    print("=" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        visualize_file(sys.argv[1])
    else:
        code = "x = 1 + 2\ndef hello(): print('world')"
        tree = ast.parse(code)
        print("Example AST Visualization:")
        print_tree(tree)
