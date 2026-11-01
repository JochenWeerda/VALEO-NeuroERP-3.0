import re
from pathlib import Path

FE = Path("packages/frontend-web")
PAGES = FE / "src" / "pages"

def classify_source(text):
    if any(x in text for x in ("useUniversalMaskRuntime", "UniversalMaskRenderer", "UniversalNativeDetailPage", "NativeListPage", "UniversalNativeCockpitPage")):
        return "runtime_wired"
    if re.search(r"\bObjectPage\b", text) or re.search(r"\bListReport\b", text):
        return "legacy_mask_pattern"
    return "hand_built"

from app.core.screen_definitions_kontrolle import KONTROLLE_SCREEN_BUILDERS

for sid in sorted(KONTROLLE_SCREEN_BUILDERS):
    found = []
    for p in PAGES.rglob("*.tsx"):
        if "__tests__" in str(p):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if f'"{sid}"' in t or f"'{sid}'" in t:
            found.append(p)
    if not found:
        print("NO PAGE", sid)
        continue
    statuses = set()
    for p in found:
        statuses.add(classify_source(p.read_text(encoding="utf-8", errors="replace")))
    if statuses != {"runtime_wired"}:
        print(sid, statuses, [str(x.relative_to(FE)) for x in found[:3]])
