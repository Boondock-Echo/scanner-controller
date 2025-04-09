import os
import shutil

# Define the source and destination directories
root_dir = os.path.dirname(os.path.abspath(__file__))
utilities_dir = os.path.join(root_dir, "utilities")

# Create the subdirectories if they don't exist
subdirs = ["core", "commands", "tools"]
for subdir in subdirs:
    subdir_path = os.path.join(utilities_dir, subdir)
    os.makedirs(subdir_path, exist_ok=True)
    # Create __init__.py in each directory if it doesn't exist
    init_path = os.path.join(subdir_path, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write(f"# {subdir} utilities package\n")

# Map of file name variations - maps normalized name to possible actual filenames
file_variations = {
    "uniden_command_finder.py": ["UnidenCommandFinder.py", "uniden_command_finder.py"],
    "command_registry.py": ["commandRegistry.py", "command_registry.py"],
    "command_library.py": ["commandLibrary.py", "command_library.py"],
    "discover_qsh_format.py": ["discoverQSHFormat.py", "discover_qsh_format.py"],
    "log_utils.py": ["logUtils.py", "log_utils.py"],
}


# Function to recursively find all Python files
def find_all_python_files(directory):
    python_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                python_files[file.lower()] = (file, rel_path)
    return python_files


# Find all Python files in utilities directory and its subdirectoriesex
print("Scanning utilities directory for existing Python files...")
all_python_files = find_all_python_files(utilities_dir)

for filename, (actual_name, rel_path) in all_python_files.items():
    if os.path.dirname(rel_path):  # If in a subdirectory
        print(f"Found: {rel_path}")
    else:
        print(f"Found: {actual_name}")

# Define file category mapping (including files in subdirectories)
file_categories = {
    "core": [
        "shared_utils.py",
        "command_library.py",
        "scanner_utils.py",
        "serial_utils.py",
        "log_trim.py",
    ],
    "commands": [
        "UnidenCommandFinder.py",
        "uniden_command_finder.py",
        "commandRegistry.py",
        "command_registry.py",
    ],
    "tools": [
        "discoverQSHFormat.py",
        "discover_qsh_format.py",
        "runFullQSHDiscovery.py",
        "run_full_qsh_discovery.py",
        "runQSHDiscovery.py",
        "readlineSetup.py",
        "logUtils.py",
        "log_utils.py",
        "validators.py",
    ],
}

# Map files to their destination folders
files_to_move = {subdir: [] for subdir in subdirs}

for filename, (actual_name, rel_path) in all_python_files.items():
    full_path = os.path.join(utilities_dir, rel_path)
    target_subdir = None

    # Determine which category this file belongs to
    for category, file_list in file_categories.items():
        if actual_name in file_list:
            target_subdir = category
            break

    # If not categorized, default to tools
    if not target_subdir:
        target_subdir = "tools"

    files_to_move[target_subdir].append((full_path, actual_name))

print("\nFiles to move by category:")
for category, file_list in files_to_move.items():
    print(f"{category}: {', '.join(name for _, name in file_list)}")

# Copy files to their new locations
for subdir, file_list in files_to_move.items():
    for source_path, filename in file_list:
        dest = os.path.join(utilities_dir, subdir, filename)
        print(f"Copying {filename} to utilities/{subdir}/")
        shutil.copy2(source_path, dest)

# Update the __init__.py file to maintain backward compatibility
with open(os.path.join(utilities_dir, "__init__.py"), "w") as f:
    f.write("# This makes the utilities directory a proper Python package\n")
    f.write("# Import commonly used utilities for easy access\n\n")

    # First import known critical modules by name that the application depends on
    f.write("# Critical imports that the application depends on\n")
    f.write(
        "from utilities.core.shared_utils import scanner_command, clear_serial_buffer\n"
    )
    if any(name == "log_trim.py" for _, name in files_to_move["core"]):
        f.write("from utilities.core.log_trim import trim_log_file\n")
    f.write("\n")

    # Then import everything else silently
    f.write("# Silently attempt to import other modules\n")
    f.write("import importlib, sys, os\n\n")

    f.write("def silent_import(module_name):\n")
    f.write("    try:\n")
    f.write("        return importlib.import_module(module_name)\n")
    f.write("    except (ImportError, ModuleNotFoundError):\n")
    f.write("        return None\n\n")

    # Create a mapping of original module paths to new paths
    f.write("# Module location mapping\n")
    f.write("module_map = {\n")

    # Add entries for the research directory files
    for filename, (actual_name, rel_path) in all_python_files.items():
        if os.path.dirname(rel_path) == "research":
            module_name = os.path.splitext(actual_name)[0]
            # Determine which subdir this file was moved to
            target_subdir = None
            for subdir, file_list in files_to_move.items():
                if any(name == actual_name for _, name in file_list):
                    target_subdir = subdir
                    break
            if target_subdir:
                f.write(
                    f"    'utilities.research.{module_name}': 'utilities.{target_subdir}.{module_name}',\n"
                )

    # Add entries for the root utilities directory files
    for filename, (actual_name, rel_path) in all_python_files.items():
        if os.path.dirname(rel_path) == "":  # Root utilities dir
            module_name = os.path.splitext(actual_name)[0]
            # Determine which subdir this file was moved to
            target_subdir = None
            for subdir, file_list in files_to_move.items():
                if any(name == actual_name for _, name in file_list):
                    target_subdir = subdir
                    break
            if target_subdir:
                f.write(
                    f"    'utilities.{module_name}': 'utilities.{target_subdir}.{module_name}',\n"
                )

    f.write("}\n\n")

    # Add code to handle imports based on the mapping
    f.write("# Import hook to redirect imports to new locations\n")
    f.write("class ImportRedirector:\n")
    f.write("    def __init__(self):\n")
    f.write("        self.module_map = module_map\n")
    f.write("        self.sys_modules = sys.modules\n\n")

    f.write("    def find_spec(self, fullname, path, target=None):\n")
    f.write("        if fullname in self.module_map:\n")
    f.write("            # If already imported, return None\n")
    f.write("            if fullname in self.sys_modules:\n")
    f.write("                return None\n")
    f.write("            # Try to import the new module location\n")
    f.write("            new_name = self.module_map[fullname]\n")
    f.write("            new_module = silent_import(new_name)\n")
    f.write("            if new_module:\n")
    f.write("                # Store it in sys.modules under both names\n")
    f.write("                self.sys_modules[fullname] = new_module\n")
    f.write("                return None  # Let the regular import mechanism proceed\n")
    f.write("        return None\n\n")

    f.write("# Register the import hook\n")
    f.write("sys.meta_path.insert(0, ImportRedirector())\n\n")

    # Now import all modules in their new locations
    for subdir, file_list in files_to_move.items():
        for _, filename in file_list:
            module_name = os.path.splitext(filename)[0]
            f.write(f"# Import {subdir}.{module_name}\n")
            f.write(f"_ = silent_import('utilities.{subdir}.{module_name}')\n")

print("Utility reorganization complete!")
print("After testing that everything works, you can remove the original files.")
