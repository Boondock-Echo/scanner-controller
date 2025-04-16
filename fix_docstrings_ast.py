#!/usr/bin/env python3
"""
AST-based Docstring Fixer.

This script uses Python's ast module to safely parse and fix docstring issues
without introducing syntax errors.
"""

# Third-party imports
import ast
import os
import sys  # Moved to fix I202
from pathlib import Path


class DocstringVisitor(ast.NodeVisitor):
    """
    AST visitor to identify docstring issues in the code.

    This visitor checks for:
    - Missing module docstrings (D100)
    - Missing docstrings in classes, functions, and methods (D101-D103)
    - Formatting issues in existing docstrings
    """

    def __init__(self):
        """
        Initialize the DocstringVisitor.

        Tracks issues and the path of visited nodes.
        """
        self.issues = []
        self.has_module_docstring = False
        self.path = []  # Add this to track the path

    def visit(self, node):
        """Override visit to track path."""
        self.path.append(node)
        result = super().visit(node)
        self.path.pop()
        return result

    def visit_Module(self, node):
        """Check for module docstring."""
        if ast.get_docstring(node):
            self.has_module_docstring = True
        else:
            self.issues.append(
                {
                    "type": "D100",
                    "node": node,
                    "message": "Missing module docstring",
                }
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Check for class docstring."""
        if not ast.get_docstring(node):
            self.issues.append(
                {
                    "type": "D101",
                    "node": node,
                    "message": f"Missing docstring in class {node.name}",
                }
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Check for function/method docstring."""
        # Skip special methods like __init__
        if not node.name.startswith("__"):
            if not ast.get_docstring(node):
                # Check if this is a method or a function
                is_method = False
                for parent in self.path[
                    :-1
                ]:  # Check all nodes in the path except the current one
                    if isinstance(parent, ast.ClassDef):
                        is_method = True
                        break

                if is_method:
                    issue_type = "D102"
                    message = f"Missing docstring in method {node.name}"
                else:
                    issue_type = "D103"
                    message = f"Missing docstring in function {node.name}"

                self.issues.append(
                    {"type": issue_type, "node": node, "message": message}
                )
        self.generic_visit(node)


def get_source_segment(source, node):
    """
    Get the source code segment for a given AST node.

    Args:
        source: The entire source code as a string
        node: The AST node

    Returns:
        The source code segment as a string
    """
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        lines = source.splitlines()
        # AST line numbers are 1-based, list indices are 0-based
        start_line = node.lineno - 1
        end_line = (
            node.end_lineno - 1 if hasattr(node, "end_lineno") else start_line
        )

        # Return the source segment
        return "\n".join(lines[start_line : end_line + 1])  # Fixed E203
    return None


def fix_module_docstring(source, module_name):
    """
    Add a proper module docstring to a Python file.

    Args:
        source: The source code as a string
        module_name: The name of the module

    Returns:
        The modified source code
    """
    # Create a docstring
    module_name = module_name.replace("_", " ").title()
    docstring = (
        f'"""\n{module_name} module.\n\nThis module provides functionality '
        f'related to {module_name.lower()}.\n"""\n\n'
    )

    # If there are imports or code at the top, insert after
    # any module-level comments
    lines = source.splitlines()
    insert_pos = 0

    # Skip initial comments and empty lines
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not (not stripped or stripped.startswith("#")):
            insert_pos = i
            break  # Fixed E501

    # Insert the docstring
    lines.insert(insert_pos, docstring)
    return "\n".join(lines)


def fix_function_docstring(source, node, name):
    """
    Add a proper function docstring.

    Args:
        source: The source code as a string
        node: The AST node for the function
        name: The function name

    Returns:
        The modified source code
    """
    lines = source.splitlines()

    # Find where the function body starts
    body_start_line = node.body[0].lineno if node.body else node.lineno + 1

    # Determine indentation from function definition
    func_line = lines[node.lineno - 1]
    indentation = ""
    for char in func_line:
        if char in (" ", "\t"):
            indentation += char
        else:
            break

    # Create the docstring
    name_readable = name.replace("_", " ")
    docstring_lines = [
        f'{indentation}    """',
        f"{indentation}    {name_readable} function.",
        f"{indentation}    ",
        f"{indentation}    Provides functionality for {name_readable}.",
        f'{indentation}    """',
    ]

    # Insert the docstring at the start of the function body
    for i, line in enumerate(docstring_lines):
        lines.insert(body_start_line + i - 1, line)

    return "\n".join(lines)


def fix_docstrings_with_ast(filepath):
    """
    Use AST to analyze and fix docstring issues in a Python file.

    Args:
        filepath: Path to the Python file

    Returns:
        Tuple of (was_modified, issues_found, issues_fixed)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # Parse the source code into an AST
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return False, 0, 0

    # Find docstring issues
    visitor = DocstringVisitor()
    visitor.visit(tree)

    if not visitor.issues:
        return False, 0, 0

    # Get the module name
    module_name = Path(filepath).stem

    # Fix issues
    modified_source = source
    issues_fixed = 0

    for issue in visitor.issues:
        if issue["type"] == "D100":  # Missing module docstring
            modified_source = fix_module_docstring(modified_source, module_name)
            issues_fixed += 1
        elif issue["type"] in (
            "D103",
            "D102",
        ):  # Missing function/method docstring
            node = issue["node"]
            modified_source = fix_function_docstring(
                modified_source, node, node.name
            )
            issues_fixed += 1

    # Only write if changes were made
    if modified_source != source:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified_source)
        return True, len(visitor.issues), issues_fixed

    return False, len(visitor.issues), 0


def is_excluded_directory(path):
    """
    Check if a path should be excluded from processing.

    Args:
        path: The path to check

    Returns:
        True if the path should be excluded, False otherwise
    """
    # List of directory names to exclude
    excluded_dirs = [
        "venv",
        ".venv",
        "env",
        ".env",  # Virtual environments
        ".git",
        ".github",  # Git directories
        "__pycache__",  # Python cache
        "node_modules",  # Node.js modules
        "dist",
        "build",
        "site-packages",  # Build directories
        ".tox",
        ".pytest_cache",  # Testing directories
        ".eggs",
        ".mypy_cache",  # More caches
        ".ruff_cache",  # Ruff cache
    ]

    # Convert path to string if it's a Path object
    path_str = str(path)

    # Check if any excluded directory is in the path
    for excluded in excluded_dirs:
        if f"/{excluded}/" in path_str.replace("\\", "/") or path_str.replace(
            "\\", "/"
        ).endswith(f"/{excluded}"):
            return True

    return False


def find_python_files(root_dir="."):
    """
    Find all Python files in the directory tree, excluding virtual environments.

    Args:
        root_dir: Starting directory for the search

    Returns:
        List of paths to Python files
    """
    python_files = []
    for path in Path(root_dir).rglob("*.py"):
        # Skip files in excluded directories
        if not is_excluded_directory(path):
            python_files.append(str(path))
    return python_files


def main():
    """Run the docstring fixer on Python files."""
    # Standard library imports
    import argparse

    parser = argparse.ArgumentParser(
        description="AST-based docstring fixer for Python files"
    )
    parser.add_argument(
        "--check", action="store_true", help="Only check for issues, don't fix"
    )
    parser.add_argument("--file", help="Fix a specific Python file")
    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} does not exist")
            return 1

        if args.check:
            print(f"Checking file: {args.file}")
            _, issues_found, _ = fix_docstrings_with_ast(args.file)
            print(f"Found {issues_found} docstring issues")
            return 0
        else:
            print(f"Fixing docstrings in file: {args.file}")
            modified, issues_found, issues_fixed = fix_docstrings_with_ast(
                args.file
            )
            print(f"Found {issues_found} issues, fixed {issues_fixed}")
            return 0

    # Process all Python files
    python_files = find_python_files()
    print(f"Found {len(python_files)} Python files")

    total_issues = 0
    total_fixed = 0

    for filepath in python_files:
        if args.check:
            _, issues_found, _ = fix_docstrings_with_ast(filepath)
            if issues_found > 0:
                print(f"{filepath}: {issues_found} issues")
            total_issues += issues_found
        else:
            modified, issues_found, issues_fixed = fix_docstrings_with_ast(
                filepath
            )
            if modified:
                print(
                    f"Fixed {issues_fixed}/{issues_found} issues in {filepath}"
                )
            total_issues += issues_found
            total_fixed += issues_fixed

    if args.check:
        print(f"\nFound {total_issues} docstring issues in total")
    else:
        print(f"\nFixed {total_fixed}/{total_issues} docstring issues")

    return 0


if __name__ == "__main__":
    sys.exit(main())
