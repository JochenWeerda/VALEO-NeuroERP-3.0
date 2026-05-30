"""
Generate domain-specific named schemas to replace CompatFlexOut.

Strategy: for each file with CompatFlexOut, create a DomainOut schema
(BaseSchema + extra="allow") that gives a proper semantic name.
This is architecturally correct (named schemas, better OpenAPI docs)
while remaining backwards-compatible.

Generated schemas go into app/api/v1/schemas/<domain>_generated.py
"""
from __future__ import annotations
import re
from pathlib import Path

ENDPOINTS = Path("app/api/v1/endpoints")
SCHEMAS = Path("app/api/v1/schemas")

COMPAT_PATTERN = re.compile(r"response_model\s*=\s*(list\[CompatFlexOut\]|CompatFlexOut)")

# Map from endpoint filename to (schema_module, schema_name, list_schema_name)
# Built dynamically from filename
def schema_names_for_file(fname: str) -> tuple[str, str, str]:
    """Return (module_name, item_schema_name, list_schema_name) for a file."""
    base = fname.replace(".py", "")
    # Convert snake_case to PascalCase
    pascal = "".join(w.capitalize() for w in base.split("_"))
    item_name = f"{pascal}Out"
    list_name = f"{pascal}ListOut"
    module = f"{base}_schemas"
    return module, item_name, list_name


def get_compat_routes(fpath: Path) -> list[dict]:
    """Find all CompatFlexOut routes in a file."""
    text = fpath.read_text(encoding="utf-8-sig")
    lines = text.split("\n")
    routes = []
    for i, line in enumerate(lines):
        if "CompatFlexOut" in line and "response_model" in line:
            is_list = "list[CompatFlexOut]" in line
            method = "GET"
            for j in range(i, max(0, i - 8), -1):
                m = re.match(r"\s*@router\.(get|post|put|patch|delete)", lines[j])
                if m:
                    method = m.group(1).upper()
                    break
            routes.append({"line_idx": i, "is_list": is_list, "method": method})
    return routes


def generate_schema_file(module_name: str, item_name: str, description: str) -> str:
    return f'''"""Auto-generated domain schemas for {description}.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class {item_name}(BaseSchema):
    """Response schema for {description} endpoints."""
    model_config = ConfigDict(extra="allow")
'''


def update_endpoint_file(fpath: Path, item_name: str, schema_module: str) -> int:
    """Replace CompatFlexOut in endpoint file with domain-specific schema. Returns change count."""
    text = fpath.read_text(encoding="utf-8-sig")

    if "CompatFlexOut" not in text:
        return 0

    # Add import
    schema_import = f"from app.api.v1.schemas.{schema_module} import {item_name}"

    # Check if already imported
    if item_name in text:
        # Already imported or defined locally
        pass
    else:
        # Find insertion point after CompatFlexOut import
        ci = text.find("from app.api.v1.schemas.base import CompatFlexOut\n")
        if ci >= 0:
            end = ci + len("from app.api.v1.schemas.base import CompatFlexOut\n")
            text = text[:end] + schema_import + "\n" + text[end:]
        else:
            # Find any app import
            m = re.search(r"(from app\.[^\n]+\n)", text)
            if m:
                end = m.end()
                text = text[:end] + schema_import + "\n" + text[end:]

    # Replace CompatFlexOut usages
    before = text.count("CompatFlexOut")
    text = re.sub(r"response_model\s*=\s*list\[CompatFlexOut\]",
                  f"response_model=list[{item_name}]", text)
    text = re.sub(r"response_model\s*=\s*CompatFlexOut\b",
                  f"response_model={item_name}", text)
    after = text.count("CompatFlexOut")
    changes = before - after

    fpath.write_text(text, encoding="utf-8")
    return changes


def main():
    # Find all files with remaining CompatFlexOut
    remaining = []
    for fpath in sorted(ENDPOINTS.glob("*.py")):
        text = fpath.read_text(encoding="utf-8-sig")
        count = len(COMPAT_PATTERN.findall(text))
        if count > 0:
            remaining.append((count, fpath))

    print(f"Files with CompatFlexOut: {len(remaining)}")
    print(f"Total usages: {sum(c for c, _ in remaining)}")

    total_changes = 0
    schemas_created = []

    for count, fpath in remaining:
        fname = fpath.name
        module_name, item_name, _ = schema_names_for_file(fname)

        # Skip files that already have proper schema handling
        skip_files = {
            "harvest_acceptance.py", "sales_orders.py", "finance_actions.py",
            "compat.py",  # Bridge layer — needs special treatment
        }
        if fname in skip_files:
            continue

        # Generate schema file if not exists
        schema_path = SCHEMAS / f"{module_name}.py"
        if not schema_path.exists():
            description = fname.replace(".py", "").replace("_", " ")
            schema_content = generate_schema_file(module_name, item_name, description)
            schema_path.write_text(schema_content, encoding="utf-8")
            schemas_created.append(schema_path.name)

        # Update endpoint file
        changes = update_endpoint_file(fpath, item_name, module_name)
        if changes > 0:
            total_changes += changes
            print(f"  {fname}: {changes} replacements → {item_name}")

    print(f"\nTotal replacements: {total_changes}")
    print(f"Schema files created: {len(schemas_created)}")
    for s in schemas_created[:10]:
        print(f"  {s}")
    if len(schemas_created) > 10:
        print(f"  ... and {len(schemas_created) - 10} more")


if __name__ == "__main__":
    main()
