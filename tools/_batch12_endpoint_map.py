"""Temporary: map Batch-12 screen IDs to OpenAPI GET endpoints."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
openapi = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
GET_PATHS = [p for p, m in openapi.get("paths", {}).items() if "get" in m]

BATCH = """admin/compliance-dashboard
admin/control-center/ai-approvals
admin/control-center/incident-response
admin/control-center
admin/control-center/operations
admin/control-center/security
admin/core/audit-governance
admin/data-quality
admin/devices
admin/dms-integration
admin/erntepeak-stabilitaet
admin/forst/kalkulation
admin/integrationen-quarantaene
admin/monitoring/alerting
admin/monitoring/historie
admin/monitoring/regeln
admin/omnichannel-handelskonflikt
admin/audit-log
admin/belegfolgekonfig
agrar/daily-prices
agrar/duenger-rechner
agrar/ernte/kampagnenabschluss
agrar/ernte-kampagne-erfassung
agrar/ernte-qualitaetsfreigabe
agrar/futter/mischfutter-optimierung
agrar/kalkulation/deckungsbeitrag
agrar/maschinen/wartung
agrar/nawaro-erntemeldung
agrar/nawaro-kaskade
agrar/nawaro-vertraege
agrar/pflanzenschutz-liste
agrar/planung/duengeplanung
agrar/planung/fruchtfolge
agrar/psm/anwendungsprotokoll
agrar/psm/tankmischung
agrar/qualitaet/ausnahmen
agrar/qualitaet/laborwerte
agrar/qualitaet/mykotoxine
agrar/saatgut/prognose
agrar/saatgut/vermehrung
agrar/sektion-auswahl
agrar/silo-belegung
agrar/silo-qualitaet
agrar/silo-trocknung
agrar/soil-samples
agrar/sorten
agrar/trocknungsregeln
agrar/umwelt/nitrat
agrar/wetter
charge/chargen-verfolgung
charge/qualitaets-freigabe
charge/rueckruf
charge/stamm
compliance/audit-trail
compliance/cross-compliance
compliance/duenge-bilanz
compliance/eudr-meldungen
compliance/gefahrstoff-verzeichnis
compliance/lksg-lieferkette
compliance/meldewesen-konsole
compliance/pflanzenschutz-nachweis
compliance/qs-audits
compliance/schadstoff-monitoring
compliance/stichtagsmeldung-bestaende
compliance/tierwohl-dokumentation
compliance/usp-konformitaet
compliance/wasserschutz-auflagen
compliance/zertifikate
contracts/contract
controlling/abweichungsanalyse
controlling/agrarkalkulation
controlling/benchmark-cockpit
controlling/berichtswesen
controlling/bwa
controlling/cashflow-prognose
controlling/deckungsbeitragsrechnung
controlling/investitionsrechnung
controlling/kampagnen-controlling
controlling/kennzahlen
controlling/kostentraegerrechnung
controlling/liquiditaetsplanung
controlling/standort-vergleich
controlling/unternehmensplanung""".strip().splitlines()

OVERRIDE: dict[str, str] = {
    "admin/compliance-dashboard": "/api/v1/compliance/stats",
    "admin/control-center": "/api/v1/admin/control-center/planning",
    "admin/data-quality": "/api/v1/admin/data-quality/rules",
    "admin/integrationen-quarantaene": "/api/v1/admin/mobile/connector-events/quarantine",
    "admin/monitoring/regeln": "/api/v1/admin/monitoring/rules",
    "admin/monitoring/alerting": "/api/v1/admin/monitoring/alerts",
    "admin/audit-log": "/api/v1/admin/audit-log",
    "admin/devices": "/api/v1/admin/devices",
    "admin/dms-integration": "/api/v1/admin/dms/status",
    "compliance/cross-compliance": "/api/v1/compliance/cross-compliance",
    "controlling/benchmark-cockpit": "/api/v1/benchmark/read-model",
    "controlling/abweichungsanalyse": "/api/v1/controlling/abweichung",
    "controlling/kennzahlen": "/api/v1/controlling/kpis",
    "controlling/massnahmen": "/api/v1/controlling/actions",
    "agrar/daily-prices": "/api/v1/agrar/daily-prices",
    "agrar/trocknungsregeln": "/api/v1/agrar/drying-rules",
    "agrar/soil-samples": "/api/v1/agrar/bodenproben",
    "agrar/maschinen/wartung": "/api/v1/agrar/maschinen",
    "agrar/nawaro-vertraege": "/api/v1/agrar/nawaro/contract-sheets",
    "agrar/nawaro-erntemeldung": "/api/v1/agrar/nawaro/print-notifications",
    "agrar/sorten": "/api/v1/agrar/kulturen",
    "charge/stamm": "/api/v1/chargen",
    "charge/rueckruf": "/api/v1/chargen/recalls",
    "compliance/eudr-meldungen": "/api/v1/compliance/eudr",
    "compliance/lksg-lieferkette": "/api/v1/compliance/lksg/supplier-risk-assessments",
    "compliance/audit-trail": "/api/v1/audit/logs",
    "compliance/duenge-bilanz": "/api/v1/agrar/feldbuch/duengebilanz",
    "compliance/gefahrstoff-verzeichnis": "/api/v1/compliance/exports/gefahrstoffdoku",
    "compliance/meldewesen-konsole": "/api/v1/meldewesen/konsole",
    "contracts/contract": "/api/v1/agrar/contracts/",
    "controlling/bwa": "/api/v1/controlling/timeseries",
    "controlling/plan-ist": "/api/v1/controlling/ist-werte",
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def candidates(screen_id: str) -> list[str]:
    domain, _, rest = screen_id.partition("/")
    out: list[str] = []
    for p in GET_PATHS:
        if p.startswith(f"/api/v1/{screen_id}"):
            out.append(p)
    if rest:
        tail = _norm(rest.split("/")[-1])
        for p in GET_PATHS:
            if not p.startswith(f"/api/v1/{domain}"):
                continue
            if tail and tail in _norm(p):
                out.append(p)
    seen: set[str] = set()
    deduped: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    deduped.sort(key=lambda x: (x.count("{"), len(x)))
    return deduped


def main() -> None:
    missing: list[str] = []
    for sid in BATCH:
        ep = OVERRIDE.get(sid) or (candidates(sid)[0] if candidates(sid) else None)
        if not ep or ep not in GET_PATHS:
            missing.append(sid)
            print(f"NO\t{sid}")
        else:
            print(f"OK\t{sid}\t{ep}")
    print("missing", len(missing), "of", len(BATCH))


if __name__ == "__main__":
    main()
