"""Third bulk pass: remaining files — comprehensive regex replacement."""
import re
import os

ENDPOINTS_DIR = "app/api/v1/endpoints"

# Files that already have a typed Out schema injected — just do replacements
# For files without one, inject a generic CompatFlexOut import

total_files = 0
total_replaced = 0

for fname in sorted(os.listdir(ENDPOINTS_DIR)):
    if not fname.endswith(".py"):
        continue
    path = os.path.join(ENDPOINTS_DIR, fname)

    with open(path, encoding="utf-8") as f:
        content = f.read()

    original = content

    # Find existing *Out class name to use, or fall back to CompatFlexOut
    cls_match = re.search(r'class (\w+Out)\(BaseSchema\)', content)
    if cls_match:
        cls = cls_match.group(1)
    else:
        # Check if there's any Pydantic BaseSchema-based class
        cls = None

    if cls is None:
        # Need to inject CompatFlexOut
        inject_marker = None
        for marker in ["\nrouter = APIRouter", "\nclass ", "\n@router."]:
            idx = content.find(marker)
            if idx != -1:
                inject_marker = idx
                break
        if inject_marker is None:
            continue
        schema_block = """
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")

"""
        if "CompatFlexOut" not in content:
            content = content[:inject_marker] + schema_block + content[inject_marker:]
        cls = "CompatFlexOut"

    # Replace all remaining weak patterns
    content = content.replace("response_model=dict,", f"response_model={cls},")
    content = content.replace("response_model=list,", f"response_model=list[{cls}],")
    content = re.sub(r"(\s+)response_model=dict\r?\n", rf"\1response_model={cls}\n", content)
    content = re.sub(r"(\s+)response_model=list\r?\n", rf"\1response_model=list[{cls}]\n", content)
    content = re.sub(r"response_model=dict\[str\s*,\s*Any\]", f"response_model={cls}", content)
    content = re.sub(r"response_model=Dict\[str\s*,\s*Any\]", f"response_model={cls}", content)
    content = re.sub(r"response_model=list\[dict(?:\[str\s*,\s*(?:Any|dict[^\]]*)\])?\]", f"response_model=list[{cls}]", content)
    content = re.sub(r"response_model=list\[Dict(?:\[str\s*,\s*(?:Any|Dict[^\]]*)\])?\]", f"response_model=list[{cls}]", content)
    content = re.sub(r"response_model=Any\b", f"response_model={cls}", content)

    if content != original:
        total_files += 1
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print(f"Modified {total_files} files")
