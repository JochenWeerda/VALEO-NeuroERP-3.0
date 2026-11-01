import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "packages/frontend-web"
inv = json.loads((FE / "src/app/routing/route-inventory.gen.json").read_text(encoding="utf-8"))
md = (ROOT / "docs/architecture/uix/mask-route-migration-inventory.md").read_text(encoding="utf-8")
# parse hand built section - simpler: rerun classify
from scripts.mask_route_migration_inventory import resolve_module, classify_source

PAGES = FE / "src/pages"
KW = re.compile(
    r"(kontrolle|kontrol|inbox|freigab|approval|pruef|prüf|warteschl|queue|monitor|ausnahm|"
    r"audit|worklist|cockpit|meldewesen|sanction|sanktion|docflow|gobd|nachweis|reklamation|"
    r"gesperrt|klaerung|qualitaets|qualitäts|export-pruef|bestell-inbox|klaerfall|"
    r"rechnungseingang|whistle|enni|pcn|capture|evidence|artefakt|wiedervor|pending|"
    r"ai-approval|command-monitor|workflow-monitoring|alerts|rechnungstapel|pruefkorb|"
    r"legacy-adapter|mde-inbox|adapter-inbox|fremdware|leitstand|abfrage-center)",
    re.I,
)
SKIP = re.compile(r"(tour|training|bestellvorschlag|FrmCoverageMonitor|consent-confirm|gdpr-request-public)", re.I)

rows = []
for r in inv["routes"]:
    path = r.get("path", "")
    module = r.get("module", "")
    if SKIP.search(path + module):
        continue
    if not KW.search(path + module):
        continue
    src = resolve_module(module)
    if not src:
        continue
    text = src.read_text(encoding="utf-8", errors="replace")
    klass = classify_source(text)
    if klass == "hand_built":
        rows.append((path, str(src.relative_to(FE)).replace("\\", "/")))

print(len(rows))
for p, f in sorted(rows):
    print(p, "|", f)
