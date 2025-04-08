"""
Migration tool to convert scanner_adapters files to redirects to the adapters folder.
"""

import os
import sys
from pathlib import Path

def get_redirect_template(legacy_module, target_module, import_names):
    """Generate redirect template code for legacy modules."""
    
    redirect_template = f'''"""
LEGACY SCANNER ADAPTER - REDIRECTS TO NEW LOCATION
This file is kept for backward compatibility and redirects to {target_module}
"""

import warnings
warnings.warn(
    "Using {legacy_module} is deprecated. "
    "Please use {target_module} instead.",
    DeprecationWarning, 
    stacklevel=2
)

from {target_module} import {", ".join(import_names)}
'''
    return redirect_template

def migrate_file(legacy_file, target_module, class_names):
    """Migrate a legacy file to a redirect to the new location."""
    
    with open(legacy_file, 'r') as f:
        content = f.read()
        
    # Skip if already migrated
    if "LEGACY SCANNER ADAPTER" in content and "DeprecationWarning" in content:
        print(f"Skipping {legacy_file} - already migrated")
        return False
        
    # Get relative module path
    rel_path = os.path.relpath(legacy_file, Path(__file__).parent)
    module_path = rel_path.replace(os.sep, '.').replace('.py', '')
    
    # Create redirect
    redirect_code = get_redirect_template(module_path, target_module, class_names)
    
    with open(legacy_file, 'w') as f:
        f.write(redirect_code)
    
    print(f"Migrated {legacy_file} -> {target_module}")
    return True

def scan_and_migrate():
    """Scan scanner_adapters folder and migrate files to adapters."""
    
    base_dir = Path(__file__).parent
    legacy_dir = base_dir / 'scanner_adapters'
    
    if not legacy_dir.exists():
        print(f"Legacy folder 'scanner_adapters' does not exist - no migration needed.")
        return
    
    legacy_files = list(legacy_dir.glob('**/*.py'))
    
    if not legacy_files:
        print(f"No Python files found in scanner_adapters - folder can be safely removed.")
        return
    
    migrated_count = 0
    skipped_count = 0
    
    # Define known mappings (add more as needed)
    file_mappings = {
        'baseAdapter.py': ('adapters.base_adapter', ['BaseScannerAdapter']),
        'bc125atAdapter.py': ('adapters.uniden.bc125at_adapter', ['BC125ATAdapter']),
        'sds100Adapter.py': ('adapters.uniden.sds100_adapter', ['SDS100Adapter']),
        'bcd325p2Adapter.py': ('adapters.uniden.bcd325p2_adapter', ['BCD325P2Adapter']),
        # Add other mappings here
    }
    
    for file in legacy_files:
        filename = file.name
        
        if filename in file_mappings:
            target_module, class_names = file_mappings[filename]
            if migrate_file(file, target_module, class_names):
                migrated_count += 1
            else:
                skipped_count += 1
        else:
            print(f"Warning: No mapping found for {filename}")
    
    print(f"\nMigration summary:")
    print(f"  - {migrated_count} files migrated")
    print(f"  - {skipped_count} files already migrated")
    print(f"  - {len(legacy_files) - migrated_count - skipped_count} files without mappings")

if __name__ == "__main__":
    scan_and_migrate()
