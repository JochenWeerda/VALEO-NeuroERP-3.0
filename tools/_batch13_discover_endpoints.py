"""Discover openapi GET {id} endpoints for batch13 screen ids."""
from __future__ import annotations

import json
import re
from pathlib import Path

PAGES = """admin/agenten-integration.tsx
admin/ai-approvals.tsx
admin/api-keys.tsx
admin/backup-restore.tsx
admin/berechtigungen-matrix.tsx
admin/branches.tsx
admin/command-monitor.tsx
admin/system-einstellungen.tsx
admin/tankstelle-evb.tsx
admin/tenants.tsx
admin/users.tsx
admin/workflow-editor.tsx
admin/zeitachsen-editor.tsx
agrar/annahme-abrechnung.tsx
agrar/ernte-annahme-abrechnung.tsx
agrar/kontrakte/formular.tsx
agrar/LieferscheinErstellen.tsx
agrar/maschinen/formular.tsx
agrar/partie-historie.tsx
agrar/pflanzenschutz-rechner.tsx
agrar/probenehmer-stamm.tsx
agrar/rechnungen-erstellen.tsx
agrar/saatgut/abrechnung.tsx
agrar/saatgut/formular.tsx
agrar/saatgut/royalties.tsx
agrar/schlaege/bodenprobe.tsx
agrar/schlaege/duengung.tsx
agrar/schlaege/ernte.tsx
agrar/schlaege/formular.tsx
agrar/schlaege/pflanzenschutz.tsx
agrar/schlaege/saat.tsx
agrar/self-billing.tsx
agrar/sorten-vermehrung.tsx
agrar/vertraege/formular.tsx
agrar/wiegeschein-detail.tsx
aktien/dividenden.tsx
aktien/hauptversammlung.tsx
aktien/mitglieder.tsx
aktien/stimmrechte.tsx
aktien/zeichnungen.tsx
analysis/WhatIfSimulator.tsx
annahme/erfassung.tsx
annahme/labor.tsx
annahme/lkw-registrierung.tsx
annahme/muster.tsx
annahme/qualitaets-check.tsx
annahme/rohwaren-annahme.tsx
annahme/silo-zuweisung.tsx
annahme/trocknung.tsx
annahme/voranmeldung.tsx
annahme/waage-1.tsx
annahme/waage-2.tsx
annahme/wartezeit.tsx
annahme/wiegeschein.tsx
artikel/bestandsuebersicht.tsx
artikel/ersatzteile.tsx
artikel/gebinde.tsx
artikel/chargen-pflicht.tsx
artikel/gefahrgut.tsx
artikel/herkunft.tsx
artikel/kategorien.tsx
artikel/konditionen.tsx
artikel/lieferanten-artikel.tsx
artikel/preisstaffeln.tsx
artikel/qualitaetsmerkmale.tsx
artikel/rabattgruppen.tsx
artikel/stuecklisten.tsx
artikel/texte-medien.tsx
artikel/umrechnungen.tsx
artikel/verpackungen.tsx
artikel/zoll-intrastat.tsx
auswertungen/abfrage-generator.tsx
auswertungen/agrarmarkt-bericht.tsx
auswertungen/deckungsbeitraege.tsx
auswertungen/erntebilanz.tsx
auswertungen/kundenumsatz.tsx
auswertungen/lagerumschlag.tsx
auswertungen/lieferantenbewertung.tsx
auswertungen/rohertrag.tsx""".strip().splitlines()

# Manual overrides (highest priority)
OVERRIDES: dict[str, str] = {
    "admin/branches": "/api/v1/admin/branches/{entity_id}",
    "admin/tenants": "/api/v1/tenants/{entity_id}",
    "artikel/bestandsuebersicht": "/api/v1/articles/{entity_id}",
    "artikel/kategorien": "/api/v1/stammdaten/warengruppen/{entity_id}",
    "agrar/schlaege/formular": "/api/v1/agrar/schlaege/{entity_id}",
    "agrar/kontrakte/formular": "/api/v1/kontrakte/{entity_id}",
    "agrar/vertraege/formular": "/api/v1/kontrakte/{entity_id}",
    "agrar/wiegeschein-detail": "/api/v1/waage/wiegungen/{entity_id}/extended",
    "annahme/wiegeschein": "/api/v1/waage/wiegungen/{entity_id}/extended",
    "agrar/probenehmer-stamm": "/api/v1/agrar/probenehmer/{entity_id}",
    "agrar/partie-historie": "/api/v1/saatzucht/partien/{entity_id}",
    "agrar/saatgut/formular": "/api/v1/agrar/saatgut/{entity_id}",
}

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
oa = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
paths = oa.get("paths", {})

get_id_paths: list[str] = []
for p, spec in paths.items():
    if "get" not in spec:
        continue
    if "{" not in p:
        continue
    get_id_paths.append(p)


def to_entity_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{entity_id}", path)


def score(screen_id: str, path: str) -> int:
    low = path.lower()
    tokens = [t for t in re.split(r"[/\-_]", screen_id.lower()) if len(t) > 2]
    s = sum(3 for t in tokens if t in low)
    if screen_id.split("/")[0] in low:
        s += 2
    if "/actions/" in low or "/tabs/" in low:
        s -= 5
    if low.endswith("/{entity_id}") or "{entity_id}" in low:
        s += 1
    return s


from app.services.made_by_studio_gates import _endpoint_in_openapi, _openapi_route_keys

routes = _openapi_route_keys()

for page in PAGES:
    sid = page.replace(".tsx", "").replace("LieferscheinErstellen", "lieferschein-erstellen").replace(
        "WhatIfSimulator", "what-if-simulator"
    )
    if sid in OVERRIDES:
        ep = OVERRIDES[sid]
        ok = _endpoint_in_openapi(ep, routes)
        print(f"{sid}\t{ep}\toverride ok={ok}")
        continue
    best = None
    best_score = 0
    for raw in get_id_paths:
        ep = to_entity_path(raw)
        if "{entity_id}" not in ep:
            continue
        sc = score(sid, ep)
        if sc > best_score and _endpoint_in_openapi(ep, routes):
            best_score = sc
            best = ep
    if not best:
        best = "/api/v1/articles/{entity_id}"  # fallback article stub
    print(f"{sid}\t{best}\tscore={best_score}")
