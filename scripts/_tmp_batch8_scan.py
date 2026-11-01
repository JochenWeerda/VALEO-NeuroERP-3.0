import json
import re
from pathlib import Path

data = json.loads(Path(".cursor/hand_built_analysis.json").read_text(encoding="utf-8"))
KW = re.compile(
    r"(worklist|queue|freigab|approval|pruef|prüf|inbox|ausnahm|kontroll|monitor|warteschl|arbeitsliste|"
    r"freigabe|genehmig|pending|exception|cockpit|leitstand|lagebild|stapel|ruecklauf|korb|meldewesen|"
    r"whistle|sanction|sanktion|docflow|capture|duplikat|audit|evidence|nachweis|reklamation|wiedervor|"
    r"qualitaets|qualitäts|gesperrt|klaerung|klärung|freigabe|zur-freigabe|ai-approval)",
    re.I,
)
SKIP = re.compile(r"(tour|training|bestellvorschlag|FrmCoverageMonitor)", re.I)

candidates = []
for x in data:
    f = x["file"]
    if SKIP.search(f):
        continue
    hay = f + " " + " ".join(x.get("oa_hits") or [])
    if x.get("family") == "b_kontroll_worklist" or KW.search(hay):
        if x.get("has_api") or x.get("oa_hits"):
            candidates.append(x)

print(f"candidates with openapi hits: {len(candidates)}")
for x in sorted(candidates, key=lambda z: z["file"]):
    hits = x.get("oa_hits") or []
    print(x["file"], "|", x.get("family"), "|", hits[0] if hits else "no hits")
