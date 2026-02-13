"""
Fail if core package imports vertical modules directly.
"""

from pathlib import Path
import re
import sys


CORE_DIR = Path("app/core")
FORBIDDEN_IMPORT_PATTERNS = [
    re.compile(r"^\s*from\s+modules\.", re.MULTILINE),
    re.compile(r"^\s*import\s+modules\.", re.MULTILINE),
]


def main() -> int:
    violations: list[tuple[str, str]] = []

    for file_path in CORE_DIR.rglob("*.py"):
        text = file_path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_IMPORT_PATTERNS:
            if pattern.search(text):
                violations.append((str(file_path), pattern.pattern))

    if violations:
        print("Core contamination check failed:")
        for file_name, pattern in violations:
            print(f"- {file_name}: matches forbidden pattern {pattern}")
        return 1

    print("Core contamination check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

