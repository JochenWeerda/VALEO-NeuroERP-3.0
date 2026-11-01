"""Restore page TSX outside Batch-15 range if auto-migration touched them."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"
START = "einkauf/preisspiegel.tsx"


def in_batch15_rel(rel: str) -> bool:
    if "-legacy" in rel:
        return False
    if "/" not in rel:
        return rel >= "Home.tsx"
    return rel >= START


def is_thin_native_wrapper(text: str) -> bool:
    markers = ("NativeListPage", "UniversalNativeCockpitPage", "createStammNativeDetailPage")
    return any(m in text for m in markers) and len(text) < 650


def main() -> None:
    restored: list[str] = []
    for path in PAGES.rglob("*.tsx"):
        if "__tests__" in str(path):
            continue
        rel = path.relative_to(PAGES).as_posix()
        if in_batch15_rel(rel):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not is_thin_native_wrapper(text):
            continue
        git_path = f"packages/frontend-web/src/pages/{rel}"
        try:
            data = subprocess.check_output(["git", "show", f"HEAD:{git_path}"], cwd=ROOT, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            continue
        path.write_bytes(data)
        restored.append(rel)
    print(f"restored {len(restored)} files")
    for r in restored[:20]:
        print(" ", r)
    if len(restored) > 20:
        print("  ...")


if __name__ == "__main__":
    main()
