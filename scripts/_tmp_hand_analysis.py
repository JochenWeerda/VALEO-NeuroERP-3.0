"""Analyze remaining hand_built pages."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
from app.core.screen_definitions_beleg import BELEGARTEN, screen_id as beleg_screen_id

PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"

ALL_SIDS = set(SCREEN_DEFINITION_BUILDERS) | {beleg_screen_id(a) for a in BELEGARTEN}

RUNTIME_MARKERS = (
    "useUniversalMaskRuntime",
    "UniversalMaskRenderer",
    "UniversalNativeDetailPage",
    "NativeListPage",
    "UniversalNativeCockpitPage",
    "createStammNativeDetailPage",
    "MadeByStudioListRuntimeWire",
    "MadeByStudioDetailRuntimeWire",
    "MadeByStudioCockpitRuntimeWire",
    "DocumentControlScopePage",
    "SanktionsScopePage",
)


def classify(text: str, filename: str) -> str:
    if filename.endswith("-legacy.tsx"):
        return "legacy_create"
    if any(x in text for x in RUNTIME_MARKERS):
        return "wired"
    if re.search(r"\bObjectPage\b", text) or re.search(r"\bListReport\b", text):
        return "legacy"
    return "hand"


def main() -> None:
    hand: list[tuple[str, set[str]]] = []
    for p in sorted(PAGES.rglob("*.tsx")):
        if "__tests__" in str(p) or ".test." in p.name or ".spec." in p.name:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if classify(text, p.name) != "hand":
            continue
        sids = set(re.findall(r"""['"]([a-z][a-z0-9-]+/[a-z0-9-./-]+)['"]""", text))
        reg = {s for s in sids if s in ALL_SIDS}
        hand.append((str(p.relative_to(PAGES)).replace("\\", "/"), reg))

    print("hand pages", len(hand))
    with_reg = [(r, s) for r, s in hand if s]
    print("with registered sid", len(with_reg))
    for rel, sids in with_reg[:15]:
        print(rel, "->", sorted(sids)[:3])


if __name__ == "__main__":
    main()
