"""
Utility script to identify and clean up legacy module redirections.

This tool helps identify where legacy module redirects are being used in the codebase,
making it easier to plan deprecation and removal of these redirects.
"""

import os
import re
import sys
import ast
import argparse
from pathlib import Path

# Mapping of legacy modules to their new locations
LEGACY_MODULES = {
    "adapter_scanner.scanner_utils": "utilities.scanner_utils",
    "adapter_scanner.base_adapter": "adapters.base_adapter",
    "adapter_scanner.adapter_bc125at": "adapters.uniden.bc125at_adapter",
    "adapter_scanner.adapter_bcd325p2": "adapters.uniden.bcd325p2_adapter",
    "library_scanner.bcd325p2_command_library": "command_libraries.uniden.bcd325p2_commands",
    # Scanner_adapters legacy modules
    "scanner_adapters.baseAdapter": "adapters.base_adapter",
    "scanner_adapters.bc125atAdapter": "adapters.uniden.bc125at_adapter",
    "scanner_adapters.bcd325p2Adapter": "adapters.uniden.bcd325p2_adapter",
    "scanner_adapters.sds100Adapter": "adapters.uniden.sds100_adapter",
    # Add other legacy modules as they're identified
}

class ImportVisitor(ast.NodeVisitor):
    """AST visitor to find imports of legacy modules"""
    
    def __init__(self):
        self.legacy_imports = []
    
    def visit_Import(self, node):
        for name in node.names:
            if name.name in LEGACY_MODULES or any(name.name.startswith(m + ".") for m in LEGACY_MODULES):
                self.legacy_imports.append((name.name, node.lineno))
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        # Handle case where module is None (from . import something)
        if node.module is None:
            return self.generic_visit(node)
            
        module = node.module
        if module in LEGACY_MODULES or any(module.startswith(m + ".") for m in LEGACY_MODULES):
            self.legacy_imports.append((module, node.lineno))
        self.generic_visit(node)


def find_legacy_usages(directory="."):
    """Find all Python files that import legacy modules"""
    results = {}
    
    for filepath in Path(directory).glob("**/*.py"):
        filepath_str = str(filepath)
        
        # Skip the legacy modules themselves and this script
        if any(legacy in filepath_str for legacy in LEGACY_MODULES.keys()) or "cleanup_legacy.py" in filepath_str:
            continue
        
        # Skip virtual environment files
        if "venv" in filepath_str.split(os.sep):
            continue
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                visitor = ImportVisitor()
                visitor.visit(tree)
                
                if visitor.legacy_imports:
                    results[filepath_str] = visitor.legacy_imports
            except SyntaxError:
                print(f"Warning: Syntax error in {filepath}")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    return results


def report_legacy_usages(usages):
    """Generate a report of legacy module usages"""
    if not usages:
        print("No legacy module usages found!")
        return
    
    print(f"Found {len(usages)} files using legacy modules:")
    
    for filepath, imports in sorted(usages.items()):
        print(f"\n{filepath}:")
        for module, lineno in imports:
            replacement = next((new for old, new in LEGACY_MODULES.items() 
                               if module == old or module.startswith(old + ".")), "unknown")
            print(f"  Line {lineno}: {module} -> {replacement}")


def main():
    parser = argparse.ArgumentParser(description="Find and report on legacy module usages")
    parser.add_argument("--directory", "-d", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("--report-file", "-o", help="Output report to this file instead of stdout")
    
    args = parser.parse_args()
    
    usages = find_legacy_usages(args.directory)
    
    if args.report_file:
        original_stdout = sys.stdout
        with open(args.report_file, 'w') as f:
            sys.stdout = f
            report_legacy_usages(usages)
            sys.stdout = original_stdout
        print(f"Report written to {args.report_file}")
    else:
        report_legacy_usages(usages)


if __name__ == "__main__":
    main()
