from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "packages/frontend-web"
data = json.loads((ROOT / ".cursor/hand_built_analysis.json").read_text(encoding="utf-8"))
OPENAPI = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
GET_PATHS = {p for p, spec in OPENAPI.get("paths", {}).items() if "get" in spec}

KW = re.compile(
    r"(worklist|queue|freigab|approval|pruef|prüf|inbox|ausnahm|kontroll|monitor|warteschl|"
    r"arbeitsliste|freigabe|genehmig|exception|cockpit|leitstand|lagebild|stapel|ruecklauf|"
    r"korb|meldewesen|whistle|sanction|sanktion|docflow|audit|evidence|nachweis|reklamation|"
    r"wiedervor|qualitaets|gesperrt|klaerung|ai-approval|warteschlange|pruefprotokoll|"
    r"bestell-inbox|klaerfall|gobd|artefakt|whistle|enni|pcn|gdpr|capture|export-pruef|"
    r"rechnungseingang|freigaben|approvals|command-monitor|workflow-monitoring|alerts)",
    re.I,
)
SKIP = re.compile(r"(tour|training|bestellvorschlag|FrmCoverageMonitor|consent-confirm|gdpr-request-public|bodenprobe)", re.I)

def norm_path(p: str) -> str:
    if not p.startswith("/api/"):
        return p
    if p.startswith("/api/v1"):
        return p.split("?")[0].rstrip("/")
    return "/api/v1" + p[len("/api") :].split("?")[0].rstrip("/")

def is_get(path: str) -> bool:
    p = norm_path(path)
    if p in GET_PATHS:
        return True
    # prefix match for list endpoints ending with /
    if (p + "/") in GET_PATHS:
        return True
    return False

rows = []
for x in data:
    f = x["file"]
    if SKIP.search(f):
        continue
    hits = x.get("oa_hits") or []
    if not hits and x.get("family") not in ("b_kontroll_worklist", "d_cockpit_dashboard"):
        continue
    if not (KW.search(f) or x.get("family") == "b_kontroll_worklist"):
        continue
    get_hits = [h for h in hits if is_get(h)]
    if get_hits or x.get("family") == "b_kontroll_worklist":
        rows.append((f, x.get("family"), get_hits, hits[:3]))

print(len(rows))
for r in sorted(rows):
    print(r[0], "|", r[1], "| gets:", r[2][:4])
