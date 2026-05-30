"""
Extract inline Pydantic schema classes from endpoint files to proper schema files.

For each endpoint file with 3+ inline schemas:
1. Find all class definitions ending in Out/In/Response/Request/Create/Update/DTO
2. Extract them (with their full source) to app/api/v1/schemas/<domain>_schemas.py
3. Add import in the endpoint file
4. Remove the inline class definitions

Handles simple cases; complex cross-dependencies are left in place.
"""
from __future__ import annotations
import re
import ast
from pathlib import Path

ENDPOINTS = Path("app/api/v1/endpoints")
SCHEMAS = Path("app/api/v1/schemas")

# Schema suffix patterns to extract
SCHEMA_SUFFIXES = re.compile(
    r"^class (\w+(?:Out|In|Response|Request|Create|Update|DTO|Payload|Schema))\s*\(",
    re.MULTILINE
)

# Pattern to match a complete class definition
def extract_class_source(text: str, class_name: str) -> str | None:
    """Extract the full source of a class definition."""
    pattern = re.compile(
        rf"^(class {re.escape(class_name)}\b[^\n]*\n(?:[ \t][^\n]*\n|[ \t]*\n)*)",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if m:
        return m.group(1)
    return None


def get_class_bases(class_source: str) -> list[str]:
    """Get base class names from a class definition."""
    m = re.match(r"class \w+\(([^)]+)\)", class_source)
    if m:
        return [b.strip() for b in m.group(1).split(",")]
    return []


def process_file(fpath: Path) -> int:
    """Extract schemas from a file. Returns number of classes extracted."""
    text = fpath.read_text(encoding="utf-8-sig")
    domain = fpath.stem

    # Find all schema class names in this file
    class_names = SCHEMA_SUFFIXES.findall(text)
    if not class_names:
        return 0

    # Check which classes actually have extractable definitions
    extractable = {}
    for name in class_names:
        source = extract_class_source(text, name)
        if source:
            extractable[name] = source

    if len(extractable) < 3:
        return 0

    schema_module = f"{domain}_schemas"
    schema_path = SCHEMAS / f"{schema_module}.py"

    # Read existing schema file if it exists
    if schema_path.exists():
        existing_schema_text = schema_path.read_text(encoding="utf-8")
        # Don't add classes that are already there
        existing_classes = set(re.findall(r"^class (\w+)\b", existing_schema_text, re.MULTILINE))
    else:
        existing_schema_text = None
        existing_classes = set()

    # Determine which classes to extract (not already in schema file)
    to_extract = {k: v for k, v in extractable.items() if k not in existing_classes}

    if not to_extract:
        return 0

    # Build the schema file content
    # Collect all imports needed by the extracted classes
    pydantic_types_used = set()
    for source in to_extract.values():
        pydantic_types_used.update(re.findall(r"\b(BaseModel|Field|validator|field_validator|model_validator|ConfigDict)\b", source))

    # Check for cross-references between schema classes in this file
    all_schema_names = set(extractable.keys())
    cross_refs = {}  # class -> set of referenced class names
    for name, source in to_extract.items():
        refs = set()
        for other in all_schema_names:
            if other != name and re.search(r"\b" + re.escape(other) + r"\b", source):
                refs.add(other)
        if refs:
            cross_refs[name] = refs

    # Build schema file
    lines = []
    if existing_schema_text:
        # Append to existing
        lines.append(existing_schema_text.rstrip())
        lines.append("")
        lines.append("")
        lines.append("# --- Extracted from endpoint file ---")
    else:
        lines.append(f'"""Pydantic schemas for the {domain.replace("_", " ")} domain."""')
        lines.append("from __future__ import annotations")
        lines.append("")
        lines.append("from typing import Any, Optional, List")
        lines.append("from pydantic import BaseModel, Field, ConfigDict")
        lines.append("from app.api.v1.schemas.base import BaseSchema")
        lines.append("")
        lines.append("")

    for name, source in to_extract.items():
        lines.append(source.rstrip())
        lines.append("")
        lines.append("")

    schema_content = "\n".join(lines)

    # Validate syntax
    try:
        ast.parse(schema_content)
    except SyntaxError:
        return 0

    schema_path.write_text(schema_content, encoding="utf-8")

    # Now update the endpoint file: add import, remove class definitions
    new_text = text

    # Add import line (after existing base imports)
    import_line = f"from app.api.v1.schemas.{schema_module} import (\n"
    import_line += "    " + ",\n    ".join(sorted(to_extract.keys()))
    import_line += ",\n)\n"

    # Check if import already exists
    if f"from app.api.v1.schemas.{schema_module} import" in new_text:
        pass  # Already imported
    else:
        # Find insertion point after last "from app." import
        m = None
        for m in re.finditer(r"from app\.[^\n]+\n", new_text):
            pass
        if m:
            new_text = new_text[:m.end()] + import_line + new_text[m.end():]
        else:
            new_text = import_line + new_text

    # Remove extracted class definitions from endpoint file
    for name, source in to_extract.items():
        # Remove the class definition (with surrounding blank lines)
        escaped = re.escape(source.rstrip())
        new_text = re.sub(r"\n*" + escaped + r"\n*", "\n\n", new_text)

    # Validate endpoint file
    try:
        ast.parse(new_text)
        fpath.write_text(new_text, encoding="utf-8")
        return len(to_extract)
    except SyntaxError:
        # Don't write if we broke something
        return 0


def main():
    schema_files_exist = {f.stem.replace("_schemas", "") for f in SCHEMAS.glob("*_schemas.py")}

    total_extracted = 0
    processed_files = []

    # Sort by number of inline schemas (descending)
    candidates = []
    for f in sorted(ENDPOINTS.glob("*.py")):
        text = f.read_text(encoding="utf-8-sig")
        count = len(SCHEMA_SUFFIXES.findall(text))
        if count >= 3:
            candidates.append((count, f))

    for count, fpath in sorted(candidates, reverse=True):
        extracted = process_file(fpath)
        if extracted > 0:
            total_extracted += extracted
            processed_files.append((fpath.name, extracted))
            print(f"  {fpath.name}: extracted {extracted} schemas")

    print(f"\nTotal schemas extracted: {total_extracted} from {len(processed_files)} files")


if __name__ == "__main__":
    main()
