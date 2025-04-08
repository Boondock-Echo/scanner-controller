# Development Tools

This directory contains utility scripts for code analysis, cleanup, and maintenance of the scanner-controller project.

## Available Tools

### Code Analysis
- `analyze_unused_files.py` - Find completely unused Python files using Vulture
- `analyze_unused_imports.py` - Detect unused imports in Python files
- `build_dependency_graph.py` - Build and visualize the project's module dependency graph

### Code Migration and Cleanup
- `cleanup_legacy.py` - Identify usages of legacy module imports that need updating
- `migrate_legacy_adapters.py` - Help migrate scanner adapters from old to new structure

## Usage

Most scripts can be run directly from the project root:

```bash
# Find unused imports
python -m dev_tools.analyze_unused_imports

# Find unused files
python -m dev_tools.analyze_unused_files

# Generate dependency graph
python -m dev_tools.build_dependency_graph

# Find legacy module usages
python -m dev_tools.cleanup_legacy --report-file legacy_report.txt

# Migrate legacy adapters (dry run)
python -m dev_tools.migrate_legacy_adapters --dry-run
```
