"""
Script to identify and analyze any remaining files in the scanner_adapters folder
that need to be migrated to the adapters folder.
"""

import os
import sys
from pathlib import Path

def scan_legacy_folder(legacy_folder='scanner_adapters', target_folder='adapters'):
    """Scan the legacy folder and compare with target folder to identify migration status."""
    
    base_dir = Path(__file__).parent
    legacy_path = base_dir / legacy_folder
    target_path = base_dir / target_folder
    
    if not legacy_path.exists():
        print(f"Legacy folder '{legacy_folder}' does not exist - no migration needed.")
        return
    
    print(f"Scanning legacy folder: {legacy_path}")
    
    legacy_files = list(legacy_path.glob('**/*.py'))
    if not legacy_files:
        print(f"No Python files found in {legacy_folder} - folder can be safely removed.")
        return
    
    print(f"Found {len(legacy_files)} Python files in {legacy_folder}:")
    
    for file in legacy_files:
        rel_path = file.relative_to(legacy_path)
        potential_target = target_path / rel_path
        
        print(f"\n{file}:")
        print(f"  Target location: {potential_target}")
        
        if potential_target.exists():
            print(f"  ✓ Target file exists")
            # Compare files to see if they have the same functionality
            with open(file, 'r') as f_legacy, open(potential_target, 'r') as f_target:
                legacy_content = f_legacy.read()
                target_content = f_target.read()
                
                if "class" in legacy_content:
                    # Extract class names from legacy file
                    legacy_classes = [line.split('class ')[1].split('(')[0].strip() 
                                     for line in legacy_content.split('\n') 
                                     if line.strip().startswith('class ')]
                    
                    # Check if these classes are in the target file
                    for cls in legacy_classes:
                        if cls in target_content:
                            print(f"  ✓ Class {cls} exists in target file")
                        else:
                            print(f"  ✗ Class {cls} NOT found in target file")
                
                # Check if the legacy file is just a redirect
                if "import warnings" in legacy_content and "DeprecationWarning" in legacy_content:
                    print(f"  ✓ Legacy file is already a redirect")
                else:
                    print(f"  ✗ Legacy file needs to be converted to a redirect")
        else:
            print(f"  ✗ Target file does not exist - migration needed")

if __name__ == "__main__":
    scan_legacy_folder()
