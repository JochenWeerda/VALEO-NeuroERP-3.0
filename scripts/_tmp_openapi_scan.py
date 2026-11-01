"""Scan hand_built pages for OpenAPI GET endpoints (Batch 8 helper)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "packages" / "frontend-web"
PAGES = FE / "src" / "pages"
OPENAPI = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))

GET_PATHS = {
    p for p, spec in OPENAPI.get("paths", {}).items()
    if "get" in spec and p.startswith("/api/v1/")
}

def classify_source(text: str) -> str:
    if any(x in text for x in ("NativeListPage", "UniversalNativeCockpitPage", "useUniversalMaskRuntime", "UniversalMaskRenderer", "UniversalNativeDetailPage")):
        return "runtime_wired"
    if re.search(r"\bObjectPage\b", text) or re.search(r"\bListReport\b", text):
        return "legacy"
    return "hand_built"

KW = re.compile(
    r"(worklist|queue|freigab|approval|pruef|prüf|inbox|ausnahm|kontroll|monitor|warteschl|"
    r"arbeitsliste|freigabe|genehmig|pending|exception|cockpit|leitstand|lagebild|stapel|"
    r"ruecklauf|korb|meldewesen|whistle|sanction|sanktion|docflow|capture|audit|evidence|"
    r"nachweis|reklamation|wiedervor|qualitaets|gesperrt|klaerung|gesperrt|zur-freigabe|"
    r"ai-approval|warteschlange|pruefprotokoll|export-pruef|bestell-inbox|klaerfall)",
    re.I,
)
SKIP = re.compile(r"(tour|training|bestellvorschlag|FrmCoverageMonitor|bodenprobe|consent-confirm|gdpr-request-public)", re.I)

API_RE = re.compile(r"['\"](/api/v1/[^'\"]+)['\"]")

rows = []
for p in sorted(PAGES.rglob("*.tsx")):
    rel = str(p.relative_to(FE)).replace("\\", "/")
    if "__tests__" in rel or ".test." in p.name:
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    if classify_source(text) != "hand_built":
        continue
    if SKIP.search(rel):
        continue
    if not KW.search(rel + " " + text[:500]):
        continue
    apis = sorted(set(API_RE.findall(text)))
    valid_gets = []
    for a in apis:
        base = a.split("?")[0].rstrip("/")
        if not base.endswith("}"):
            # try exact and with trailing slash variants
            for cand in (base, base + "/", base.replace("${", "{").split("{")[0].rstrip("/")):
                if cand in GET_PATHS:
                    valid_gets.append(cand)
                    break
    if valid_gets:
        rows.append((rel, valid_gets[:5]))

print(f"matches: {len(rows)}")
for rel, gets in rows:
    print(rel)
    for g in gets:
        print("  ", g)
