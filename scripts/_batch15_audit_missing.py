import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS

PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"
START = "einkauf/preisspiegel.tsx"
pat = re.compile(r"""screenId=["']([^"']+)["']""")


def in_range(rel: str) -> bool:
    if "/" in rel and rel < START:
        return False
    if "/" not in rel and rel < "Home.tsx":
        return False
    return True


missing: set[str] = set()
wired = 0
for p in PAGES.rglob("*.tsx"):
    if "__tests__" in str(p) or "-legacy" in p.name:
        continue
    rel = p.relative_to(PAGES).as_posix()
    if not in_range(rel):
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    if not any(
        x in t
        for x in (
            "NativeListPage",
            "UniversalNativeCockpitPage",
            "createStammNativeDetailPage",
            "UniversalNativeDetailPage",
        )
    ):
        continue
    wired += 1
    for m in pat.finditer(t):
        sid = m.group(1)
        if sid not in SCREEN_DEFINITION_BUILDERS:
            missing.add(sid)

print("wired pages", wired)
print("missing screen defs", len(missing))
for s in sorted(missing):
    print(s)
