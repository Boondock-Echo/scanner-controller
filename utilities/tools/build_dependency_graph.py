import ast
import os
from collections import defaultdict


def find_python_files(directory):
    """Recursively find all Python files in the given directory, excluding certain folders."""
    python_files = []
    excluded_dirs = {"venv", "__pycache__", ".git"}  # Add directories to exclude here
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def extract_imports(filepath):
    """Extract all imports from a Python file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=filepath)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


def extract_dynamic_imports(filepath):
    """Detect dynamic imports in a Python file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=filepath)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return set()

    dynamic_imports = set()
    for node in ast.walk(tree):
        # Detect usage of importlib.import_module
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "import_module" and isinstance(
                node.func.value, ast.Name
            ):
                if node.func.value.id == "importlib" and len(node.args) > 0:
                    if isinstance(node.args[0], ast.Str):
                        dynamic_imports.add(node.args[0].s)

        # Detect usage of __import__
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "__import__" and len(node.args) > 0:
                if isinstance(node.args[0], ast.Str):
                    dynamic_imports.add(node.args[0].s)

    return dynamic_imports


def categorize_imports(imports, file_to_module):
    """Categorize imports as local, third-party, or unresolved."""
    local_imports = set()
    unresolved_imports = set()

    for imported_module in imports:
        if imported_module in file_to_module.values():
            local_imports.add(imported_module)
        else:
            unresolved_imports.add(imported_module)

    return local_imports, unresolved_imports


def build_dependency_graph(directory):
    """Build a dependency graph for all Python files in the directory."""
    python_files = find_python_files(directory)
    graph = defaultdict(list)
    unresolved = defaultdict(set)
    file_to_module = {
        file: os.path.splitext(os.path.relpath(file, directory))[0].replace(os.sep, ".")
        for file in python_files
    }

    for file, module in file_to_module.items():
        imports = extract_imports(file)
        dynamic_imports = extract_dynamic_imports(file)
        all_imports = imports.union(dynamic_imports)

        local_imports, unresolved_imports = categorize_imports(
            all_imports, file_to_module
        )
        for imported_module in local_imports:
            for other_file, other_module in file_to_module.items():
                if imported_module == other_module and file != other_file:
                    graph[file].append(other_file)
        unresolved[file].update(unresolved_imports)

    return graph, unresolved


def print_dependency_graph(graph, unresolved, base_dir):
    """Print the dependency graph and unresolved imports."""
    if not graph:
        print("No dependencies found.")
        return

    print("Dependency Graph:")
    for file, dependencies in sorted(graph.items()):
        relative_file = os.path.relpath(file, base_dir)
        print(f"{relative_file}:")
        if dependencies:
            for dependency in sorted(dependencies):
                print(f"  -> {os.path.relpath(dependency, base_dir)}")
        else:
            print("  (No dependencies)")

    print("\nUnresolved Imports:")
    for file, imports in sorted(unresolved.items()):
        if imports:
            relative_file = os.path.relpath(file, base_dir)
            print(f"{relative_file}: {', '.join(sorted(imports))}")


def print_grouped_files(
    referenced_files, unreferenced_files, base_dir, tree_view=False
):
    """Print referenced and unreferenced files, optionally in a tree view."""

    def print_tree(files):
        tree = defaultdict(list)
        for file in files:
            parts = os.path.relpath(file, base_dir).split(os.sep)
            current = tree
            for part in parts[:-1]:
                current = current[part]
            current[parts[-1]] = []

        def print_branch(branch, prefix=""):
            for key in sorted(branch):
                print(f"{prefix}{key}")
                print_branch(branch[key], prefix + "  ")

        print_branch(tree)

    print("\nReferenced Files:")
    if tree_view:
        print_tree(referenced_files)
    else:
        for file in sorted(referenced_files):
            print(os.path.relpath(file, base_dir))

    print("\nUnreferenced Files:")
    if tree_view:
        print_tree(unreferenced_files)
    else:
        for file in sorted(unreferenced_files):
            print(os.path.relpath(file, base_dir))


def save_unused_files(unreferenced_files, base_dir, output_file="unused_files.txt"):
    """Save the list of unused files to a file."""
    with open(output_file, "w", encoding="utf-8") as file:
        for unused_file in sorted(unreferenced_files):
            file.write(f"{os.path.relpath(unused_file, base_dir)}\n")
    print(f"\nUnused files saved to {output_file}")


if __name__ == "__main__":
    project_dir = r"c:\Users\mjhug\Documents\GitHub\scanner-controller"
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
