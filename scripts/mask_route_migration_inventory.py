"""Temporary inventory: classify frontend routes by mask migration status."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FE = ROOT / "packages" / "frontend-web"
PAGES = FE / "src" / "pages"
INV = FE / "src" / "app" / "routing" / "route-inventory.gen.json"
OUT = ROOT / "docs" / "architecture" / "uix" / "mask-route-migration-inventory.md"


def classify_source(text: str, *, filename: str = "") -> str:
    from app.core.mask_runtime_evidence import has_visible_runtime
    # A lazy wrapper still runs the previous page; its name proves no migration.
    if "createLegacyMaskPage" in text:
        return "legacy_wrapper"
    if filename in ("NotFound.tsx", "Login.tsx", "Callback.tsx"):
        return "technical_page"
    if filename == "FibuSuiteRuntime.tsx":
        return "runtime_wired"
    if filename == "MaskRolloutRoute.tsx" and "UniversalMaskRolloutPilotPage" in text:
        return "runtime_wired"
    if has_visible_runtime(text):
        return "runtime_wired"
    if re.search(r"\bObjectPage\b", text) or re.search(r"\bListReport\b", text):
        return "legacy_mask_pattern"
    # thin re-exports / redirects still count as hand-built until runtime-wired
    return "hand_built"


RUNTIME_MODULE_FILES: dict[str, Path] = {
    "@runtime/fibu-suite": FE / "src/app/FibuSuiteRuntime.tsx",
}


def resolve_module(module: str) -> Path | None:
    if module in RUNTIME_MODULE_FILES:
        path = RUNTIME_MODULE_FILES[module]
        return path if path.exists() else None
    # "@/pages/foo/bar" -> pages/foo/bar.tsx
    if not module.startswith("@/pages/"):
        return None
    rel = module[len("@/pages/") :]
    base = PAGES / rel.replace("/", "\\") if False else PAGES / Path(*rel.split("/"))
    for ext in (".tsx", ".ts", "/index.tsx", "/index.ts"):
        cand = Path(str(base) + ext) if not ext.startswith("/") else base / ext[1:]
        if cand.exists():
            return cand
    return None


def main() -> None:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    routes = inv["routes"]
    by_class: Counter[str] = Counter()
    unresolved = []
    legacy_paths = []
    runtime_paths = []
    hand_paths = []
    file_cache: dict[Path, str] = {}

    for r in routes:
        module = r.get("module", "")
        path = r.get("path", "")
        src = resolve_module(module)
        if src is None:
            # non-page modules (layouts, redirects) — treat separately
            by_class["non_page_module"] += 1
            unresolved.append({"path": path, "module": module})
            continue
        if src not in file_cache:
            file_cache[src] = src.read_text(encoding="utf-8", errors="replace")
        klass = classify_source(file_cache[src], filename=src.name)
        by_class[klass] += 1
        entry = {"path": path or "/", "module": module, "file": str(src.relative_to(FE)).replace("\\", "/")}
        if klass == "runtime_wired":
            runtime_paths.append(entry)
        elif klass == "legacy_mask_pattern":
            legacy_paths.append(entry)
        else:
            hand_paths.append(entry)

    # page-file inventory (unique files)
    page_files = [
        p
        for p in PAGES.rglob("*.tsx")
        if "__tests__" not in str(p) and ".test." not in p.name and ".spec." not in p.name
    ]
    page_by = Counter()
    for p in page_files:
        page_by[classify_source(p.read_text(encoding="utf-8", errors="replace"), filename=p.name)] += 1

    # ScreenDefinition registry keys in screen_definitions.py
    sd_text = (ROOT / "app" / "core" / "screen_definitions.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"_SCREEN_DEFINITIONS:\s*dict\[str,\s*Any\]\s*=\s*\{", sd_text)
    sd_ids: set[str] = set()
    if m:
        depth = 1
        i = m.end()
        while i < len(sd_text) and depth:
            if sd_text[i] == "{":
                depth += 1
            elif sd_text[i] == "}":
                depth -= 1
            i += 1
        body = sd_text[m.end() : i - 1]
        sd_ids = set(re.findall(r'(?m)^    ["\']([^"\']+)["\']\s*:', body))

    # Studio: count published_temp / draft mentions is DB-only; inventory TS capture screens
    capture = list((FE / "src" / "masks").rglob("*.ts")) if (FE / "src" / "masks").exists() else []
    capture_screens = 0
    for f in capture:
        t = f.read_text(encoding="utf-8", errors="replace")
        capture_screens += len(re.findall(r"export const \w+Screen\b", t))

    lines = [
        "# Masken-Routen-Migrationsinventar",
        "",
        "Stand: 2026-10-22 (Messung aus `route-inventory.gen.json` + Seitenquelltext).",
        "",
        "> Studio-Entwuerfe in der DB sind **kein** Nachweis produktiver Ablösung.",
        "> Nur `runtime_wired` (ScreenDefinition → RenderPlan → useUniversalMaskRuntime /",
        "> UniversalMaskRenderer / UniversalNativeDetailPage) zaehlt als zentrale Steuerung.",
        "",
        "## Routen (route-inventory)",
        "",
        f"| Klasse | Anzahl |",
        f"|--------|--------|",
        f"| Gesamt Routen | {len(routes)} |",
        f"| runtime_wired (UniversalMaskRuntime-Pfad) | {by_class['runtime_wired']} |",
        f"| legacy_mask_pattern (ObjectPage/ListReport ohne Runtime) | {by_class['legacy_mask_pattern']} |",
        f"| legacy_wrapper (laedt weiter die Altoberflaeche) | {by_class['legacy_wrapper']} |",
        f"| technical_page (Anmeldung/Fehlerseite, keine Fachmaske) | {by_class['technical_page']} |",
        f"| hand_built (weder Runtime noch ObjectPage/ListReport) | {by_class['hand_built']} |",
        f"| non_page_module (Layout/Redirect/sonstiges) | {by_class['non_page_module']} |",
        "",
        "## Seiten-Dateien (`src/pages/**/*.tsx`)",
        "",
        f"| Klasse | Anzahl |",
        f"|--------|--------|",
        f"| Gesamt TSX-Seiten | {len(page_files)} |",
        f"| runtime_wired | {page_by['runtime_wired']} |",
        f"| legacy_mask_pattern | {page_by['legacy_mask_pattern']} |",
        f"| hand_built | {page_by['hand_built']} |",
        "",
        "## ScreenDefinitions / Studio",
        "",
        f"- Registrierte ScreenDefinition-Builder (`_SCREEN_DEFINITIONS`): **{len(sd_ids)}**",
        f"- Frontend capture/mask TS-Exports (`export const *Screen`): **{capture_screens}**",
        "- Studio-Draft-Zaehlung erfordert Live-DB (`screen_definition_drafts`); ohne DB hier nicht gemessen.",
        "",
        "### Vergleich zum frueheren Stand",
        "",
        "| Metrik | Frueher | Jetzt (2026-10-22) |",
        "|--------|---------|---------------------|",
        f"| handgebaute Routen | 442 | {by_class['hand_built']} |",
        f"| Routen mit alten Maskenmustern | 80 | {by_class['legacy_mask_pattern']} |",
        f"| Runtime-verdrahtet | — | {by_class['runtime_wired']} |",
        "| Studio-Entwuerfe | 154 | (DB, nicht gemessen) |",
        "",
        "Hinweis: Fruehere 442/80 bezogen sich vermutlich auf eine engere Routen-/Seitenbasis;",
        f"aktuell sind **{len(routes)}** generierte Routen inventarisiert. Die Absolute `hand_built`",
        "ist deshalb nicht 1:1 vergleichbar, aber die Luecke zur Runtime bleibt gross.",
        "",
        "## Dual-Pfad (Native Wrapper existiert, Primaernav oft Legacy)",
        "",
        "Siehe UIX-057, MASK-PRIMARY-NAV-NATIVE-20261022 und MASK-BESTELLUNG-NAV-NATIVE-20261022:",
        "Listen oeffneten teilweise `*-stamm` / Plural-Legacy, waehrend `*-native` unter der",
        "kanonischen `/:id`-Route lag. Stammdaten (Saatgut, Duenger, Lieferant) und Bestellung-",
        "Detailnav sind auf Native umgehaengt; Neuanlage bleibt Legacy. Paritaetsluecken Bestellung",
        "(CaseBand, Allokation, Freigabe-Detail, Komm-Senden) und Beleg-Alt-Einstiege bleiben offen.",
        "",
        "## Legacy ObjectPage/ListReport (erste 40)",
        "",
    ]
    for e in sorted(legacy_paths, key=lambda x: x["path"])[:40]:
        lines.append(f"- `{e['path']}` ← `{e['file']}`")
    lines += ["", "## Runtime-verdrahtet (alle)", ""]
    for e in sorted(runtime_paths, key=lambda x: x["path"]):
        lines.append(f"- `{e['path']}` ← `{e['file']}`")
    lines += ["", "## Handgebaut — Migrationskandidaten (erste 60, alphabetisch)", ""]
    for e in sorted(hand_paths, key=lambda x: x["path"])[:60]:
        lines.append(f"- `{e['path']}` ← `{e['file']}`")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "routes_total": len(routes),
        "runtime_wired": by_class["runtime_wired"],
        "legacy_mask_pattern": by_class["legacy_mask_pattern"],
        "hand_built": by_class["hand_built"],
        "non_page_module": by_class["non_page_module"],
        "pages_total": len(page_files),
        "pages_runtime": page_by["runtime_wired"],
        "pages_legacy": page_by["legacy_mask_pattern"],
        "legacy_wrapper": by_class["legacy_wrapper"],
        "pages_legacy_wrapper": page_by["legacy_wrapper"],
        "pages_hand": page_by["hand_built"],
        "screen_ids": len(sd_ids),
        "capture_screens": capture_screens,
        "out": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
