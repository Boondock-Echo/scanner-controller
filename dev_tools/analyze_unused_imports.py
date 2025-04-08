import os
import ast

def find_unused_imports(file_path):
    """
    Analyzes a Python file to find unused imports.
    """
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]
    used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    unused_imports = [imp for imp in imports if not any(alias.name in used_names for alias in imp.names)]
    return unused_imports

def scan_directory_for_unused_imports(directory, output_file):
    """
    Recursively scans a directory for Python files and checks for unused imports.
    Outputs the results to a file.
    """
    with open(output_file, "w") as output:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    unused_imports = find_unused_imports(file_path)
                    if unused_imports:
                        output.write(f"{file_path}:\n")
                        for imp in unused_imports:
                            output.write(f"  {imp.lineno}: {ast.dump(imp)}\n")
                        output.write("\n")

if __name__ == "__main__":
    # Use relative path to work regardless of where script is called from
    directory_to_scan = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_file = "unused_imports.txt"
    print(f"Scanning directory: {directory_to_scan}")
    scan_directory_for_unused_imports(directory_to_scan, output_file)
    print(f"Results saved to {output_file}")