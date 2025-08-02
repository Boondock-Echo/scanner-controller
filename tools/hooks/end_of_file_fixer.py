#!/usr/bin/env python3
"""Ensure files end with a single newline."""
from __future__ import annotations

import sys
from pathlib import Path


def fix_file(path: Path) -> bool:
    original = path.read_text()
    if not original.endswith("\n"):
        path.write_text(original + "\n")
        return True
    # Collapse multiple trailing newlines to a single newline
    stripped = original.rstrip("\n") + "\n"
    if stripped != original:
        path.write_text(stripped)
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    paths = [Path(p) for p in (argv or sys.argv[1:])]
    modified = [str(p) for p in paths if p.is_file() and fix_file(p)]
    for name in modified:
        print(f"Fixed end-of-file newline: {name}")
    return 1 if modified else 0


if __name__ == "__main__":
    raise SystemExit(main())
