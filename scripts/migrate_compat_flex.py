"""
Migrate CompatFlexOut routes to proper response types.

Phase 1: 204 routes       -> response_model=None  (safe, no new imports)
Phase 2: status dict      -> response_model=StatusResponse
Phase 3: id dict          -> response_model=IDResponse

Strategy: line-level replacement only — no structural changes to decorators.
"""
from __future__ import annotations
import re
from pathlib import Path

ENDPOINTS = Path("app/api/v1/endpoints")


def get_func_body_for_compat_line(lines: list[str], compat_idx: int) -> str:
    """Return function body lines starting from CompatFlexOut decorator line."""
    for j in range(compat_idx, min(compat_idx + 10, len(lines))):
        if re.match(r"\s*(async )?def ", lines[j]):
            return "\n".join(lines[j + 1 : j + 60])
    return ""


def get_http_method(lines: list[str], compat_idx: int) -> str:
    for j in range(compat_idx, max(0, compat_idx - 10), -1):
        m = re.match(r"\s*@router\.(get|post|put|patch|delete)", lines[j])
        if m:
            return m.group(1).upper()
    return "GET"


def categorize(body: str, method: str) -> str:
    """Categorize route by what it returns."""
    if "Response(status_code=204)" in body or (
        "status_code=204" in body and method in ("DELETE", "PATCH", "PUT")
    ):
        return "204"
    if re.search(r'return\s+\{["\'](?:status|ok|success|deleted|message)["\']', body):
        return "status_dict"
    if re.search(r'return\s+\{["\']id["\']', body):
        return "id_dict"
    return "data"


def ensure_base_import(text: str, name: str) -> str:
    """Add name to the existing base import line, or create one."""
    if name in text:
        return text
    pattern = re.compile(r"from app\.api\.v1\.schemas\.base import ([^\n]+)")
    m = pattern.search(text)
    if m:
        existing = m.group(1).strip()
        if name not in existing:
            replacement = f"from app.api.v1.schemas.base import {existing}, {name}"
            text = text[: m.start()] + replacement + text[m.end():]
    else:
        # Add after CompatFlexOut import
        ci = text.find("from app.api.v1.schemas.base import CompatFlexOut\n")
        if ci >= 0:
            end = ci + len("from app.api.v1.schemas.base import CompatFlexOut\n")
            text = text[:end] + f"from app.api.v1.schemas.base import {name}\n" + text[end:]
    return text


def process_file(fpath: Path) -> tuple[int, str]:
    text = fpath.read_text(encoding="utf-8-sig")
    if "CompatFlexOut" not in text:
        return 0, text

    lines = text.split("\n")
    changes = 0
    needs_status = False
    needs_id = False

    # Find all CompatFlexOut lines (work in reverse to preserve indices)
    compat_indices = [
        i for i, line in enumerate(lines)
        if "CompatFlexOut" in line and "response_model" in line
    ]

    for idx in reversed(compat_indices):
        body = get_func_body_for_compat_line(lines, idx)
        method = get_http_method(lines, idx)
        cat = categorize(body, method)

        if cat == "204":
            # Simple line replacement: response_model=CompatFlexOut -> response_model=None
            new_line = re.sub(
                r"response_model\s*=\s*CompatFlexOut\b",
                "response_model=None",
                lines[idx],
            )
            if new_line != lines[idx]:
                lines[idx] = new_line
                changes += 1

        elif cat == "status_dict":
            new_line = re.sub(
                r"response_model\s*=\s*CompatFlexOut\b",
                "response_model=StatusResponse",
                lines[idx],
            )
            if new_line != lines[idx]:
                lines[idx] = new_line
                changes += 1
                needs_status = True

        elif cat == "id_dict":
            new_line = re.sub(
                r"response_model\s*=\s*CompatFlexOut\b",
                "response_model=IDResponse",
                lines[idx],
            )
            if new_line != lines[idx]:
                lines[idx] = new_line
                changes += 1
                needs_id = True
        # else data — leave for schema generation wave

    if changes == 0:
        return 0, text

    new_text = "\n".join(lines)

    if needs_status:
        new_text = ensure_base_import(new_text, "StatusResponse")
    if needs_id:
        new_text = ensure_base_import(new_text, "IDResponse")

    return changes, new_text


if __name__ == "__main__":
    total_changes = 0
    changed_files = []

    for fpath in sorted(ENDPOINTS.glob("*.py")):
        changes, new_text = process_file(fpath)
        if changes > 0:
            fpath.write_text(new_text, encoding="utf-8")
            changed_files.append((fpath.name, changes))
            total_changes += changes
            print(f"  Fixed {changes:2d}x: {fpath.name}")

    print(f"\nTotal: {total_changes} routes migrated in {len(changed_files)} files")
