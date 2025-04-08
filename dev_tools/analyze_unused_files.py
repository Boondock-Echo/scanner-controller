import os
import subprocess

def find_python_files(directory, excluded_dirs=None):
    """Recursively find all Python files in the given directory, excluding certain folders."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        if excluded_dirs:
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def analyze_file_with_vulture(filepath):
    """Run vulture on a single file and return whether it contains unused code."""
    result = subprocess.run(["vulture", filepath], capture_output=True, text=True)
    return "unused" in result.stdout

def find_unused_files(directory):
    """Identify files where all code is unused."""
    python_files = find_python_files(directory)
    unused_files = []
    for file in python_files:
        if analyze_file_with_vulture(file):
            unused_files.append(file)
    return unused_files

def save_unused_files(unused_files, output_file="unused_files.txt"):
    """Save the list of unused files to a file."""
    with open(output_file, "w") as f:
        for file in unused_files:
            f.write(file + "\n")

if __name__ == "__main__":
    # Use relative path to work regardless of where script is called from
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    unused_files = find_unused_files(project_dir)

    print("\nUnused Files:")
    for file in unused_files:
        print(file)

    # Save unused files to a file
    save_unused_files(unused_files)