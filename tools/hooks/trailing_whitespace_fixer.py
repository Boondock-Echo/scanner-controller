#!/usr/bin/env python3
"""Strip trailing whitespace from files.

This is a minimal replacement for the upstream trailing-whitespace pre-commit
hook. It updates files in place and returns a non-zero exit status if any file
was modified.
"""
from __future__ import annotations

import sys
from pathlib import Path


def fix_file(path: Path) -> bool:
    """Remove trailing whitespace from *path*.

    Returns True if the file was modified.
    """
    original = path.read_text()
    lines = original.splitlines()
    stripped_lines = [line.rstrip(" \t") for line in lines]
    stripped = "\n".join(stripped_lines)
    if original.endswith("\n"):
        stripped += "\n"
    if original != stripped:
        path.write_text(stripped)
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    paths = [Path(p) for p in (argv or sys.argv[1:])]
    modified = [str(p) for p in paths if p.is_file() and fix_file(p)]
    for name in modified:
        print(f"Fixed trailing whitespace: {name}")
    return 1 if modified else 0


if __name__ == "__main__":
    raise SystemExit(main())
