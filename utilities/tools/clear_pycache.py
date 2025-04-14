"""
Module to clear all __pycache__ directories in the project.

This script recursively deletes all __pycache__ directories starting from
the specified root directory.
"""

import os
import shutil


def clear_pycache(directory):
    """Recursively delete all __pycache__ directories."""
    for root, dirs, _files in os.walk(directory):  # Rename 'files' to '_files'
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                print(f"Deleting: {pycache_path}")
                shutil.rmtree(pycache_path)


if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))
    clear_pycache(project_dir)
