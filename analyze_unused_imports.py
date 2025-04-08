import os
import ast

def find_unused_imports(file_path):
    """
    Analyzes a Python file to find unused imports.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=file_path)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return []

    # Collect all imported names
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports[alias.asname or alias.name] = node.lineno

    # Collect all used names
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)

    # Find unused imports
    unused_imports = [name for name in imports if name not in used_names]
    return [(name, imports[name]) for name in unused_imports]

def scan_directory_for_unused_imports(directory, output_file):
    """
    Recursively scans a directory for Python files and checks for unused imports.
    Outputs the results to a file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(directory):
            # Skip the venv folder
            dirs[:] = [d for d in dirs if d != "venv"]
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    unused_imports = find_unused_imports(file_path)
                    if unused_imports:
                        f.write(f"\nUnused imports in {file_path}:\n")
                        for name, lineno in unused_imports:
                            f.write(f"  Line {lineno}: {name}\n")
                        print(f"Logged unused imports in {file_path}")

if __name__ == "__main__":
    # Specify the directory to scan
    directory_to_scan = "./"  # Change this to the desired directory
    output_file = "unused_imports.txt"
    print(f"Scanning directory: {directory_to_scan}")
    scan_directory_for_unused_imports(directory_to_scan, output_file)
    print(f"Results saved to {output_file}")