import ast
import os
from collections import defaultdict


def find_python_files(directory):
    """Recursively find all Python files in the given directory, excluding certain folders."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Exclude certain folders
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "venv"]]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def extract_imports(filepath):
    """Extract all imports from a Python file."""
    with open(filepath, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=filepath)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def extract_dynamic_imports(filepath):
    """Detect dynamic imports in a Python file."""
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
    dynamic_imports = []
    for node in ast.walk(ast.parse(content)):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "__import__"
        ):
            if isinstance(node.args[0], ast.Str):
                dynamic_imports.append(node.args[0].s)
    return dynamic_imports


def categorize_imports(imports, file_to_module):
    """Categorize imports as local, third-party, or unresolved."""
    local_imports = []
    third_party_imports = []
    unresolved_imports = []
    for imp in imports:
        if imp in file_to_module:
            local_imports.append(imp)
        else:
            try:
                __import__(imp)
                third_party_imports.append(imp)
            except ImportError:
                unresolved_imports.append(imp)
    return local_imports, third_party_imports, unresolved


def build_dependency_graph(directory):
    """Build a dependency graph for all Python files in the directory."""
    file_to_module = {}
    for filepath in find_python_files(directory):
        module_name = os.path.relpath(filepath, directory).replace(os.sep, ".")[:-3]
        file_to_module[module_name] = filepath

    dependency_graph = defaultdict(set)
    unresolved_imports = defaultdict(set)
    for module, filepath in file_to_module.items():
        imports = extract_imports(filepath) + extract_dynamic_imports(filepath)
        local_imports, third_party_imports, unresolved = categorize_imports(
            imports, file_to_module
        )
        for imp in local_imports:
            dependency_graph[module].add(imp)
        for imp in unresolved:
            unresolved_imports[module].add(imp)
    return dependency_graph, unresolved_imports


def print_dependency_graph(graph, unresolved, base_dir):
    """Print the dependency graph and unresolved imports."""
    print("Dependency Graph:")
    for module, dependencies in graph.items():
        print(f"{module}:")
        for dep in dependencies:
            print(f"  - {dep}")
    print("\nUnresolved Imports:")
    for module, imports in unresolved.items():
        print(f"{module}:")
        for imp in imports:
            print(f"  - {imp}")


def print_grouped_files(
    referenced_files, unreferenced_files, base_dir, tree_view=False
):
    """Print referenced and unreferenced files, optionally in a tree view."""
    print("Referenced Files:")
    for file in sorted(referenced_files):
        print(f"  - {os.path.relpath(file, base_dir)}")
    print("\nUnreferenced Files:")
    for file in sorted(unreferenced_files):
        print(f"  - {os.path.relpath(file, base_dir)}")


def save_unused_files(unreferenced_files, base_dir, output_file="unused_files.txt"):
    """Save the list of unused files to a file."""
    with open(output_file, "w", encoding="utf-8") as file:
        for unreferenced_file in sorted(unreferenced_files):
            file.write(f"{os.path.relpath(unreferenced_file, base_dir)}\n")


if __name__ == "__main__":
    # Use relative path to work regardless of where script is called from
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dependency_graph, unresolved_imports = build_dependency_graph(project_dir)
    print_dependency_graph(dependency_graph, unresolved_imports, project_dir)

    all_files = find_python_files(project_dir)
    referenced_files = set(dependency_graph.keys()).union(
        {dep for deps in dependency_graph.values() for dep in deps}
    )
    unreferenced_files = set(all_files) - referenced_files

    # Set `tree_view=True` to enable tree view output
    print_grouped_files(
        referenced_files, unreferenced_files, project_dir, tree_view=False
    )

    # Save unused files to a file
    save_unused_files(unreferenced_files, project_dir)
