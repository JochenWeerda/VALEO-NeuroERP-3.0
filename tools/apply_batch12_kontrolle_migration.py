"""Batch-12: KontrollWorklist ScreenDefinitions + NativeListPage / UniversalNativeCockpitPage."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
KONTROLLE = ROOT / "app/core/screen_definitions_kontrolle.py"
BATCH12_MOD = ROOT / "app/core/screen_definitions_kontrolle_batch12.py"
OPENAPI = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
GET_PATHS = {p for p, spec in OPENAPI.get("paths", {}).items() if "get" in spec}

COCKPIT_SCREENS = frozenset({"admin/compliance-dashboard", "controlling/benchmark-cockpit"})
# Definition existiert bereits (Batch 8 / Cockpit-Modul) — nur TSX migrieren.
BUILDER_EXCLUDE = frozenset(
    {
        "compliance/meldewesen-konsole",
        "admin/compliance-dashboard",
        "controlling/benchmark-cockpit",
    }
)

PAGES_LIST = [
    "admin/compliance-dashboard.tsx",
    "admin/control-center/ai-approvals.tsx",
    "admin/control-center/incident-response.tsx",
    "admin/control-center/index.tsx",
    "admin/control-center/operations.tsx",
    "admin/control-center/security.tsx",
    "admin/core/audit-governance.tsx",
    "admin/data-quality.tsx",
    "admin/devices/index.tsx",
    "admin/dms-integration.tsx",
    "admin/erntepeak-stabilitaet.tsx",
    "admin/forst/kalkulation.tsx",
    "admin/integrationen-quarantaene.tsx",
    "admin/monitoring/alerting.tsx",
    "admin/monitoring/historie.tsx",
    "admin/monitoring/regeln.tsx",
    "admin/omnichannel-handelskonflikt.tsx",
    "admin/AuditLogPage.tsx",
    "admin/BelegfolgekonfigPage.tsx",
    "agrar/daily-prices.tsx",
    "agrar/duenger-rechner.tsx",
    "agrar/ernte/kampagnenabschluss.tsx",
    "agrar/ernte-kampagne-erfassung.tsx",
    "agrar/ernte-qualitaetsfreigabe.tsx",
    "agrar/futter/mischfutter-optimierung.tsx",
    "agrar/kalkulation/deckungsbeitrag.tsx",
    "agrar/maschinen/wartung.tsx",
    "agrar/nawaro-erntemeldung.tsx",
    "agrar/nawaro-kaskade.tsx",
    "agrar/nawaro-vertraege.tsx",
    "agrar/pflanzenschutz-liste.tsx",
    "agrar/planung/duengeplanung.tsx",
    "agrar/planung/fruchtfolge.tsx",
    "agrar/psm/anwendungsprotokoll.tsx",
    "agrar/psm/tankmischung.tsx",
    "agrar/qualitaet/ausnahmen.tsx",
    "agrar/qualitaet/laborwerte.tsx",
    "agrar/qualitaet/mykotoxine.tsx",
    "agrar/saatgut/prognose.tsx",
    "agrar/saatgut/vermehrung.tsx",
    "agrar/sektion-auswahl.tsx",
    "agrar/silo-belegung.tsx",
    "agrar/silo-qualitaet.tsx",
    "agrar/silo-trocknung.tsx",
    "agrar/soil-samples.tsx",
    "agrar/sorten.tsx",
    "agrar/trocknungsregeln.tsx",
    "agrar/umwelt/nitrat.tsx",
    "agrar/wetter.tsx",
    "charge/chargen-verfolgung.tsx",
    "charge/qualitaets-freigabe.tsx",
    "charge/rueckruf.tsx",
    "charge/stamm.tsx",
    "compliance/audit-trail.tsx",
    "compliance/cross-compliance.tsx",
    "compliance/duenge-bilanz.tsx",
    "compliance/eudr-meldungen.tsx",
    "compliance/gefahrstoff-verzeichnis.tsx",
    "compliance/lksg-lieferkette.tsx",
    "compliance/meldewesen-konsole.tsx",
    "compliance/pflanzenschutz-nachweis.tsx",
    "compliance/qs-audits.tsx",
    "compliance/schadstoff-monitoring.tsx",
    "compliance/stichtagsmeldung-bestaende.tsx",
    "compliance/tierwohl-dokumentation.tsx",
    "compliance/usp-konformitaet.tsx",
    "compliance/wasserschutz-auflagen.tsx",
    "compliance/zertifikate.tsx",
    "contracts/ContractPage.tsx",
    "controlling/abweichungsanalyse.tsx",
    "controlling/agrarkalkulation.tsx",
    "controlling/benchmark-cockpit.tsx",
    "controlling/berichtswesen.tsx",
    "controlling/bwa.tsx",
    "controlling/cashflow-prognose.tsx",
    "controlling/deckungsbeitragsrechnung.tsx",
    "controlling/investitionsrechnung.tsx",
    "controlling/kampagnen-controlling.tsx",
    "controlling/kennzahlen.tsx",
    "controlling/kostentraegerrechnung.tsx",
    "controlling/liquiditaetsplanung.tsx",
    "controlling/standort-vergleich.tsx",
    "controlling/unternehmensplanung.tsx",
]

SCREEN_ID_ALIASES = {
    "admin/AuditLogPage": "admin/audit-log",
    "admin/BelegfolgekonfigPage": "admin/belegfolgekonfig",
    "contracts/ContractPage": "contracts/contract",
}

ENDPOINTS: dict[str, str] = {
    "admin/compliance-dashboard": "/api/v1/compliance/stats",
    "admin/control-center/ai-approvals": "/api/v1/finance/ap/invoices/",
    "admin/control-center/incident-response": "/api/v1/agents/neuroassist/ops/incidents",
    "admin/control-center": "/api/v1/agents/neuroassist/ops/control-center",
    "admin/control-center/operations": "/api/v1/admin-suite/operations",
    "admin/control-center/security": "/api/v1/admin-suite/security",
    "admin/core/audit-governance": "/api/v1/governance/audit-trail",
    "admin/data-quality": "/api/v1/admin/data-quality/rules",
    "admin/devices": "/api/v1/admin/devices",
    "admin/dms-integration": "/api/v1/admin/dms/status",
    "admin/erntepeak-stabilitaet": "/api/v1/admin/erntefenster-campaigns",
    "admin/forst/kalkulation": "/api/v1/agrar/contracts/",
    "admin/integrationen-quarantaene": "/api/v1/admin/mobile/connector-events/quarantine",
    "admin/monitoring/alerting": "/api/v1/admin/monitoring/alerts",
    "admin/monitoring/historie": "/api/v1/admin/monitoring/scheduler-jobs",
    "admin/monitoring/regeln": "/api/v1/admin/monitoring/rules",
    "admin/omnichannel-handelskonflikt": "/api/v1/channels/livechat/sessions",
    "admin/audit-log": "/api/v1/admin/audit-log",
    "admin/belegfolgekonfig": "/api/v1/admin/number-ranges/",
    "agrar/daily-prices": "/api/v1/agrar/daily-prices",
    "agrar/duenger-rechner": "/api/v1/agrar/duenger/stats/overview",
    "agrar/ernte/kampagnenabschluss": "/api/v1/ernte-kampagnen/tenant/{tenant_id}",
    "agrar/ernte-kampagne-erfassung": "/api/v1/ernte-kampagnen/tenant/{tenant_id}",
    "agrar/ernte-qualitaetsfreigabe": "/api/v1/agrar/harvest-acceptance/",
    "agrar/futter/mischfutter-optimierung": "/api/v1/agrar/rations-optimization/controlling/series",
    "agrar/kalkulation/deckungsbeitrag": "/api/v1/agrar/rations-optimization/controlling/series",
    "agrar/maschinen/wartung": "/api/v1/agrar/maschinen",
    "agrar/nawaro-erntemeldung": "/api/v1/agrar/nawaro/print-notifications",
    "agrar/nawaro-kaskade": "/api/v1/agrar/nawaro/area-sheets",
    "agrar/nawaro-vertraege": "/api/v1/agrar/nawaro/contract-sheets",
    "agrar/pflanzenschutz-liste": "/api/v1/agrar/psm/",
    "agrar/planung/duengeplanung": "/api/v1/agrar/feldbuch/duengemittelmengen",
    "agrar/planung/fruchtfolge": "/api/v1/agrar/kulturen",
    "agrar/psm/anwendungsprotokoll": "/api/v1/agrar/psm/",
    "agrar/psm/tankmischung": "/api/v1/agrar/psm/monitoring",
    "agrar/qualitaet/ausnahmen": "/api/v1/agrar/quality-lots",
    "agrar/qualitaet/laborwerte": "/api/v1/agrar/quality-lots",
    "agrar/qualitaet/mykotoxine": "/api/v1/labor/proben",
    "agrar/saatgut/prognose": "/api/v1/agrar/saatgut/stats/overview",
    "agrar/saatgut/vermehrung": "/api/v1/saatzucht/vermehrungsvertraege",
    "agrar/sektion-auswahl": "/api/v1/agrar/kunden",
    "agrar/silo-belegung": "/api/v1/silo/silos",
    "agrar/silo-qualitaet": "/api/v1/agrar/quality-lots",
    "agrar/silo-trocknung": "/api/v1/agrar/settlements/drying-rules",
    "agrar/soil-samples": "/api/v1/labor/proben",
    "agrar/sorten": "/api/v1/agrar/kulturen",
    "agrar/trocknungsregeln": "/api/v1/agrar/settlements/drying-rules",
    "agrar/umwelt/nitrat": "/api/v1/agrar/feldbuch/duengebilanz",
    "agrar/wetter": "/api/v1/agrar/wetter/boden",
    "charge/chargen-verfolgung": "/api/v1/chargen/stats/summary",
    "charge/qualitaets-freigabe": "/api/v1/chargen",
    "charge/rueckruf": "/api/v1/chargen",
    "charge/stamm": "/api/v1/chargen",
    "compliance/audit-trail": "/api/v1/audit/logs",
    "compliance/cross-compliance": "/api/v1/compliance/cross-compliance",
    "compliance/duenge-bilanz": "/api/v1/agrar/feldbuch/duengebilanz",
    "compliance/eudr-meldungen": "/api/v1/compliance/eudr",
    "compliance/gefahrstoff-verzeichnis": "/api/v1/compliance/exports/gefahrstoffdoku",
    "compliance/lksg-lieferkette": "/api/v1/compliance/lksg/supplier-risk-assessments",
    "compliance/meldewesen-konsole": "/api/v1/jobs",
    "compliance/pflanzenschutz-nachweis": "/api/v1/compliance/bvl-umsaetze",
    "compliance/qs-audits": "/api/v1/admin/quality-evidence/",
    "compliance/schadstoff-monitoring": "/api/v1/agrar/psm/monitoring",
    "compliance/stichtagsmeldung-bestaende": "/api/v1/intrastat/meldungen",
    "compliance/tierwohl-dokumentation": "/api/v1/compliance/vvvo-register",
    "compliance/usp-konformitaet": "/api/v1/compliance/zulassungen-register",
    "compliance/wasserschutz-auflagen": "/api/v1/agrar/psm/wasserschutz-zonen",
    "compliance/zertifikate": "/api/v1/zertifikate",
    "contracts/contract": "/api/v1/agrar/contracts/",
    "controlling/abweichungsanalyse": "/api/v1/controlling/abweichung",
    "controlling/agrarkalkulation": "/api/v1/controlling/kpis",
    "controlling/benchmark-cockpit": "/api/v1/benchmark/read-model",
    "controlling/berichtswesen": "/api/v1/controlling/dashboards",
    "controlling/bwa": "/api/v1/finance/financial-reports/bwa",
    "controlling/cashflow-prognose": "/api/v1/finance/liquidity/forecast",
    "controlling/deckungsbeitragsrechnung": "/api/v1/controlling/abweichung/drill-down",
    "controlling/investitionsrechnung": "/api/v1/controlling/dashboards",
    "controlling/kampagnen-controlling": "/api/v1/ernte-kampagnen/tenant/{tenant_id}",
    "controlling/kennzahlen": "/api/v1/controlling/kpis",
    "controlling/kostentraegerrechnung": "/api/v1/controlling/timeseries",
    "controlling/liquiditaetsplanung": "/api/v1/finance/liquidity/overview",
    "controlling/standort-vergleich": "/api/v1/benchmark/read-model",
    "controlling/unternehmensplanung": "/api/v1/controlling/kpis",
}

ROW_ACTIONS: dict[str, list[dict]] = {
    "admin/integrationen-quarantaene": [
        {
            "key": "retry",
            "label": "Erneut versuchen",
            "permission": "admin.mobile.connector.retry",
            "commandEndpoint": "/api/v1/admin/mobile/connector-events/{entity_id}/retry",
            "method": "POST",
            "dangerLevel": "moderate",
        },
        {
            "key": "resolve",
            "label": "Erledigen",
            "permission": "admin.mobile.connector.resolve",
            "commandEndpoint": "/api/v1/admin/mobile/connector-events/{entity_id}/resolve",
            "method": "POST",
            "dangerLevel": "moderate",
        },
    ],
}

TABLE_PROFILE: dict[str, str] = {
    "compliance": "audit",
    "admin": "audit",
    "controlling": "financial",
    "finance": "financial",
    "charge": "inventory",
    "agrar": "standard",
}


def page_to_screen_id(page: str) -> str:
    stem = page.replace(".tsx", "")
    if stem.endswith("/index"):
        stem = stem[: -len("/index")]
    return SCREEN_ID_ALIASES.get(stem, stem)


def _title(screen_id: str) -> str:
    leaf = screen_id.split("/")[-1].replace("-", " ")
    return leaf[:1].upper() + leaf[1:]


def _validate_endpoint(endpoint: str) -> None:
    base = endpoint.split("?", 1)[0]
    if base in GET_PATHS:
        return
    alt = base.rstrip("/") + "/" if not base.endswith("/") else base.rstrip("/")
    if alt in GET_PATHS:
        return
    raise SystemExit(f"GET missing in openapi: {endpoint}")


def _tsx(page: str, screen_id: str) -> str:
    comp = "".join(w.capitalize() for w in re.sub(r"[^a-zA-Z0-9]+", " ", page.replace(".tsx", "")).split())
    if screen_id in COCKPIT_SCREENS:
        return (
            "import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'\n\n"
            f"/** Native Cockpit `{screen_id}` (Batch 12). */\n"
            f"export default function {comp}(): JSX.Element {{\n"
            f'  return <UniversalNativeCockpitPage screenId="{screen_id}" testId="screen-{screen_id}" />\n'
            "}\n"
        )
    return (
        "import { NativeListPage } from '@/components/mask-builder/NativeListPage'\n\n"
        f"/** Kontroll-Worklist `{screen_id}` (Batch 12). */\n"
        f"export default function {comp}(): JSX.Element {{\n"
        f'  return <NativeListPage screenId="{screen_id}" testId="screen-{screen_id}" />\n'
        "}\n"
    )


def _write_batch12_module() -> None:
    BATCH12_MOD.write_text(_render_batch12_module(), encoding="utf-8")


def _render_batch12_module() -> str:
    spec_lines = []
    for page in PAGES_LIST:
        sid = page_to_screen_id(page)
        if sid in BUILDER_EXCLUDE:
            continue
        ep = ENDPOINTS[sid]
        _validate_endpoint(ep)
        domain = sid.split("/")[0]
        profile = TABLE_PROFILE.get(domain, "standard")
        spec_lines.append(
            f'    "{sid}": {{"endpoint": "{ep}", "domain": "{domain}", "title": "{_title(sid)}", "table_profile": "{profile}"}},'
        )
    row_lines = [f'    "{k}": {v!r},' for k, v in ROW_ACTIONS.items()]
    builder_lines = [
        f'    "{page_to_screen_id(p)}": lambda _s="{page_to_screen_id(p)}": build_batch12_kontroll_screen(_s),'
        for p in PAGES_LIST
        if page_to_screen_id(p) not in BUILDER_EXCLUDE
    ]
    return "\n".join([
        '"""Kontroll-Worklists Batch 12 (Mask-Route-Migration)."""',
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from app.core.kontroll_worklist_parent import (",
        "    build_kontroll_worklist_screen,",
        "    kontroll_entity_and_queue_sources,",
        "    kontroll_queue_table,",
        ")",
        "",
        "_COLS = [",
        '    {"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 120},',
        '    {"key": "name", "label": "Bezeichnung", "sortable": True, "filterable": True, "width": 220},',
        '    {"key": "status", "label": "Status", "renderKind": "status", "sortable": True, "filterable": True, "width": 120},',
        '    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 130},',
        "]",
        "",
        "_ROW_ACTIONS: dict[str, list[dict[str, Any]]] = {",
        *row_lines,
        "}",
        "",
        "BATCH12_SPECS: dict[str, dict[str, Any]] = {",
        *spec_lines,
        "}",
        "",
        "def build_batch12_kontroll_screen(screen_id: str) -> dict[str, Any]:",
        "    spec = BATCH12_SPECS[screen_id]",
        "    endpoint = spec['endpoint']",
        "    domain = spec['domain']",
        "    title = spec['title']",
        "    queue_key = 'items'",
        "    row_actions = list(_ROW_ACTIONS.get(screen_id, []))",
        "    if not row_actions:",
        "        row_actions = [{'key': 'open', 'label': 'Oeffnen'}]",
        "    return build_kontroll_worklist_screen(",
        "        screen_id=screen_id,",
        "        domain=domain,",
        "        title=title,",
        "        subtitle=f'Kontroll-Worklist {title}',",
        "        data_sources=kontroll_entity_and_queue_sources(",
        "            summary_endpoint=endpoint,",
        "            queue_endpoint=endpoint,",
        "            queue_key=queue_key,",
        "        ),",
        "        summary=[",
        "            {'key': 'total', 'label': 'Eintraege', 'tone': 'neutral'},",
        "            {'key': 'offen', 'label': 'Offen', 'tone': 'warning'},",
        "        ],",
        "        tables=[",
        "            kontroll_queue_table(",
        "                table_key=queue_key,",
        "                label=title,",
        "                columns=list(_COLS),",
        "                row_actions=row_actions,",
        "            ),",
        "        ],",
        "        no_workflow_reason='Status und Freigaben stehen am Datensatz; die Liste priorisiert nur.',",
        "        table_profile=spec.get('table_profile', 'standard'),",
        "        bundle_group=domain,",
        "        business_purpose=f'{title} mandantensicher als Kontroll-Worklist abarbeiten.',",
        "        example_prompts=[f'Zeige offene {title}.', f'Was ist in {title} faellig?'],",
        "        test_id=screen_id.replace('/', '-'),",
        "    )",
        "",
        "",
        "BATCH12_BUILDERS: dict[str, Any] = {",
        *builder_lines,
        "}",
        "",
        "BATCH12_KONTROLL_TEST_IDS: tuple[str, ...] = tuple(",
        "    sid",
        "    for sid in BATCH12_SPECS",
        "    if sid",
        "    not in {",
        "        'admin/compliance-dashboard',",
        "        'controlling/benchmark-cockpit',",
        "        'compliance/meldewesen-konsole',",
        "    }",
        ")",
        "",
    ])


def _patch_kontrolle() -> None:
    text = KONTROLLE.read_text(encoding="utf-8")
    if "screen_definitions_kontrolle_batch12" not in text:
        text = text.replace(
            "from app.core.kontroll_worklist_legacy_payloads import KONTROLL_WORKLIST_LEGACY_PAYLOADS\n",
            "from app.core.kontroll_worklist_legacy_payloads import KONTROLL_WORKLIST_LEGACY_PAYLOADS\n"
            "from app.core.screen_definitions_kontrolle_batch12 import (\n"
            "    BATCH12_BUILDERS,\n"
            "    BATCH12_KONTROLL_TEST_IDS,\n"
            ")\n",
        )
    if "**BATCH12_BUILDERS" not in text:
        text = text.replace(
            "    **{sid: _lift_legacy_kontroll_worklist(sid) for sid in KONTROLL_WORKLIST_LEGACY_PAYLOADS},\n}",
            "    **{sid: _lift_legacy_kontroll_worklist(sid) for sid in KONTROLL_WORKLIST_LEGACY_PAYLOADS},\n"
            "    **BATCH12_BUILDERS,\n}",
        )
    if "BATCH12_KONTROLL_TEST_IDS" not in text.split("KONTROLL_WORKLIST_SCREEN_IDS", 1)[0]:
        pass
    old_tuple = "    *tuple(sorted(KONTROLL_WORKLIST_LEGACY_PAYLOADS)),\n)"
    new_tuple = (
        "    *tuple(sorted(KONTROLL_WORKLIST_LEGACY_PAYLOADS)),\n"
        "    *BATCH12_KONTROLL_TEST_IDS,\n)"
    )
    if "BATCH12_KONTROLL_TEST_IDS" not in text:
        text = text.replace(old_tuple, new_tuple)
    KONTROLLE.write_text(text, encoding="utf-8")


def main() -> None:
    for page in PAGES_LIST:
        sid = page_to_screen_id(page)
        _validate_endpoint(ENDPOINTS[sid])
    _write_batch12_module()
    _patch_kontrolle()
    for page in PAGES_LIST:
        sid = page_to_screen_id(page)
        dest = PAGES / page
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(_tsx(page, sid), encoding="utf-8")
    # also wire existing audit-log.tsx alias page
    audit = PAGES / "admin/audit-log.tsx"
    if audit.exists():
        audit.write_text(_tsx("admin/audit-log.tsx", "admin/audit-log"), encoding="utf-8")
    print(f"Batch 12: {len(PAGES_LIST)} pages, module {BATCH12_MOD.name}")


if __name__ == "__main__":
    main()
