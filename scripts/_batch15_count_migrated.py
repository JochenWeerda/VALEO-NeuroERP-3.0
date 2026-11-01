import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"
START = "einkauf/preisspiegel.tsx"
INV = json.loads(
    (ROOT / "packages/frontend-web/src/app/routing/route-inventory.gen.json").read_text(encoding="utf-8")
)
import sys

sys.path.insert(0, str(ROOT))
from app.core.screen_definitions_domain_batch15 import BATCH15_SCREEN_BUILDERS


def in_range(rel: str) -> bool:
    if "-legacy" in rel:
        return False
    if "/" not in rel:
        return rel >= "Home.tsx"
    return rel >= START


def is_wired(text: str) -> bool:
    return any(
        x in text
        for x in (
            "NativeListPage",
            "UniversalNativeCockpitPage",
            "createStammNativeDetailPage",
            "UniversalNativeDetailPage",
        )
    )


routes: dict[str, str] = {}
for route in INV["routes"]:
    mod = route.get("module", "")
    if not mod.startswith("@/pages/"):
        continue
    rel = f"{mod[len('@/pages/') :]}.tsx"
    if not in_range(rel):
        continue
    routes[rel] = (route.get("path") or mod[len("@/pages/") :]).lstrip("/")

migrated = 0
for rel, sid in routes.items():
    path = PAGES / rel
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if sid in BATCH15_SCREEN_BUILDERS and is_wired(text):
        migrated += 1

print("batch15_migrated_routable", migrated)
print("batch15_builders", len(BATCH15_SCREEN_BUILDERS))
