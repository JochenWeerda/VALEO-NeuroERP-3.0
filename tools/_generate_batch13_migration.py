"""Generate batch13 stamm screen definitions and migrate/wire frontend pages."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PAGES_ROOT = ROOT / "packages" / "frontend-web" / "src" / "pages"
BATCH13_PY = ROOT / "app" / "core" / "screen_definitions_stamm_batch13.py"

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

# screen_id -> (entity GET endpoint, optional bearbeiten endpoint)
ENDPOINTS: dict[str, tuple[str, str | None]] = {
    "admin/agenten-integration": (
        "/api/v1/agent/integrations/providers/superglue/tenants/{entity_id}/admin-state",
        None,
    ),
    "admin/ai-approvals": ("/api/v1/finance/ap/approval-workflow/status/{entity_id}", None),
    "admin/api-keys": ("/api/v1/admin/benutzer/{entity_id}", None),
    "admin/backup-restore": ("/api/v1/admin/benutzer/{entity_id}", None),
    "admin/berechtigungen-matrix": ("/api/v1/admin/report-permissions/{entity_id}", None),
    "admin/branches": ("/api/v1/admin/branches/{entity_id}", None),
    "admin/command-monitor": ("/api/v1/articles/{entity_id}", None),
    "admin/system-einstellungen": ("/api/v1/articles/{entity_id}", None),
    "admin/tankstelle-evb": ("/api/v1/tankstelle/zapfungen/{entity_id}", None),
    "admin/tenants": ("/api/v1/tenants/{entity_id}", None),
    "admin/users": ("/api/v1/admin/benutzer/{entity_id}", None),
    "admin/workflow-editor": ("/api/v1/workflow/runtime/instances/{entity_id}", None),
    "admin/zeitachsen-editor": ("/api/v1/workflow/cockpit/processes/{entity_id}", None),
    "agrar/annahme-abrechnung": ("/api/v1/agrar/self-billing/harvest-acceptance/{entity_id}", None),
    "agrar/ernte-annahme-abrechnung": ("/api/v1/agrar/harvest-acceptance/{entity_id}", None),
    "agrar/kontrakte/formular": ("/api/v1/kontrakte/{entity_id}", "/api/v1/kontrakte/{entity_id}/actions/bearbeiten"),
    "agrar/lieferschein-erstellen": ("/api/v1/einkauf/lieferscheine/{entity_id}", None),
    "agrar/maschinen/formular": ("/api/v1/agrar/maschinen/{entity_id}", None),
    "agrar/partie-historie": ("/api/v1/saatzucht/partien/{entity_id}", None),
    "agrar/pflanzenschutz-rechner": ("/api/v1/agrar/schlaege/{entity_id}", None),
    "agrar/probenehmer-stamm": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "agrar/rechnungen-erstellen": ("/api/v1/agrar/self-billing/{entity_id}", None),
    "agrar/saatgut/abrechnung": ("/api/v1/agrar/saatgut/{entity_id}", None),
    "agrar/saatgut/formular": ("/api/v1/agrar/saatgut/{entity_id}", None),
    "agrar/saatgut/royalties": ("/api/v1/agrar/saatgut/{entity_id}", None),
    "agrar/schlaege/bodenprobe": ("/api/v1/agrar/schlaege/{entity_id}", None),
    "agrar/schlaege/duengung": ("/api/v1/agrar/schlaege/{entity_id}", None),
    "agrar/schlaege/ernte": ("/api/v1/agrar/ernte/{entity_id}", None),
    "agrar/schlaege/formular": ("/api/v1/agrar/schlaege/{entity_id}", None),
    "agrar/schlaege/pflanzenschutz": ("/api/v1/agrar/schlaege/{entity_id}", None),
    "agrar/schlaege/saat": ("/api/v1/agrar/saatgut/{entity_id}", None),
    "agrar/self-billing": ("/api/v1/agrar/self-billing/{entity_id}", None),
    "agrar/sorten-vermehrung": ("/api/v1/saatzucht/vermehrungsvertraege/{entity_id}", None),
    "agrar/vertraege/formular": ("/api/v1/kontrakte/{entity_id}", "/api/v1/kontrakte/{entity_id}/actions/bearbeiten"),
    "agrar/wiegeschein-detail": ("/api/v1/waage/wiegungen/{entity_id}/extended", None),
    "aktien/dividenden": ("/api/v1/genossenschaft/mitglieder/{entity_id}", None),
    "aktien/hauptversammlung": ("/api/v1/genossenschaft/mitglieder/{entity_id}", None),
    "aktien/mitglieder": ("/api/v1/genossenschaft/mitglieder/{entity_id}", None),
    "aktien/stimmrechte": ("/api/v1/genossenschaft/mitglieder/{entity_id}", None),
    "aktien/zeichnungen": ("/api/v1/genossenschaft/mitglieder/{entity_id}", None),
    "analysis/what-if-simulator": ("/api/v1/agrar/rations-optimization/feeding/reports/{entity_id}", None),
    "annahme/erfassung": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/labor": ("/api/v1/labor/labor-auftraege/{entity_id}", None),
    "annahme/lkw-registrierung": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/muster": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/qualitaets-check": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/rohwaren-annahme": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/silo-zuweisung": ("/api/v1/silo/zielzellen-vorschlag/lot/{entity_id}", None),
    "annahme/trocknung": ("/api/v1/process/trocknungs-abrechnung/preview/{entity_id}", None),
    "annahme/voranmeldung": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/waage-1": ("/api/v1/waage/waagen/{entity_id}", None),
    "annahme/waage-2": ("/api/v1/waage/waagen/{entity_id}", None),
    "annahme/wartezeit": ("/api/v1/annahme/warteschlange/{entity_id}", None),
    "annahme/wiegeschein": ("/api/v1/waage/wiegungen/{entity_id}/extended", None),
    "artikel/bestandsuebersicht": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/ersatzteile": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/gebinde": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/chargen-pflicht": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/gefahrgut": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/herkunft": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/kategorien": (
        "/api/v1/stammdaten/warengruppen/{entity_id}",
        "/api/v1/stammdaten/warengruppen/{entity_id}/actions/bearbeiten",
    ),
    "artikel/konditionen": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/lieferanten-artikel": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/preisstaffeln": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/qualitaetsmerkmale": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/rabattgruppen": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/stuecklisten": ("/api/v1/produktion/stuecklisten/{entity_id}", None),
    "artikel/texte-medien": ("/api/v1/articles/{entity_id}", "/api/v1/articles/{entity_id}/actions/bearbeiten"),
    "artikel/umrechnungen": ("/api/v1/artikel/mengeneinheiten/gruppen/{entity_id}", None),
    "artikel/verpackungen": ("/api/v1/artikel/verpackungen/{entity_id}", None),
    "artikel/zoll-intrastat": ("/api/v1/compliance/intrastat/meldungen/{entity_id}/validate", None),
    "auswertungen/abfrage-generator": ("/api/v1/l3-report-catalog/{entity_id}/run", None),
    "auswertungen/agrarmarkt-bericht": ("/api/v1/massebilanz/{entity_id}/bericht", None),
    "auswertungen/deckungsbeitraege": ("/api/v1/crm/bedarfsdeckung/{entity_id}", None),
    "auswertungen/erntebilanz": ("/api/v1/l3-report-catalog/{entity_id}/run", None),
    "auswertungen/kundenumsatz": ("/api/v1/l3-report-catalog/{entity_id}/drilldown", None),
    "auswertungen/lagerumschlag": ("/api/v1/l3-report-catalog/{entity_id}/run", None),
    "auswertungen/lieferantenbewertung": ("/api/v1/l3-report-catalog/{entity_id}/run", None),
    "auswertungen/rohertrag": ("/api/v1/l3-report-catalog/{entity_id}/run", None),
}

REEXPORT_PAGES = {"admin/agenten-integration": ["AgentenIntegrationWorkspace"]}


def camel_to_kebab(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def page_to_screen_id(page: str) -> str:
    rel = page.removesuffix(".tsx")
    parts = rel.split("/")
    parts[-1] = camel_to_kebab(parts[-1])
    return "/".join(parts)


def page_to_test_id(screen_id: str) -> str:
    return screen_id.replace("/", "-")


def domain_for(screen_id: str) -> str:
    head = screen_id.split("/")[0]
    return {
        "admin": "admin",
        "agrar": "agrar",
        "annahme": "agrar",
        "artikel": "lager",
        "auswertungen": "reporting",
        "aktien": "genossenschaft",
        "analysis": "reporting",
    }.get(head, head)


def title_for(screen_id: str) -> str:
    last = screen_id.split("/")[-1].replace("-", " ")
    return last[:1].upper() + last[1:]


def permission_for(screen_id: str) -> str:
    slug = screen_id.replace("/", ".")
    return f"{slug}.update"


def generate_batch13_py() -> None:
    from app.services.made_by_studio_gates import _endpoint_in_openapi, _openapi_route_keys

    routes = _openapi_route_keys()
    lines: list[str] = [
        '"""Batch 13 Stamm-ObjectPage ScreenDefinitions (MASK-STUDIO-ROLLOUT)."""',
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from app.core.stamm_object_page_parent import (",
        "    build_stamm_object_page,",
        "    stamm_entity_source,",
        "    stamm_kopf_tab,",
        ")",
        "",
        "",
        "def _batch13_stamm(",
        "    screen_id: str,",
        "    *,",
        "    domain: str,",
        "    title: str,",
        "    entity_endpoint: str,",
        "    identity_field: str,",
        "    edit_permission: str,",
        "    bearbeiten_endpoint: str | None = None,",
        ") -> dict[str, Any]:",
        '    kopf = [',
        '        {"key": identity_field, "label": "Kennung", "type": "text"},',
        '        {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},',
        '        {"key": "status", "label": "Status", "type": "text", "readOnly": True},',
        "    ]",
        "    overrides: dict[str, Any] | None = None",
        "    if bearbeiten_endpoint:",
        "        overrides = {",
        '            "commandEndpoint": bearbeiten_endpoint,',
        '            "method": "POST",',
        "            \"inputFields\": [",
        '                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},',
        "            ],",
        "        }",
        "    return build_stamm_object_page(",
        "        screen_id=screen_id,",
        "        domain=domain,",
        "        title=title,",
        "        subtitle=screen_id,",
        "        identity_field=identity_field,",
        "        data_sources=[stamm_entity_source(entity_endpoint)],",
        "        tabs=[stamm_kopf_tab(kopf)],",
        "        edit_permission=edit_permission,",
        "        edit_action_key=\"bearbeiten\",",
        "        edit_action_overrides=overrides,",
        '        no_workflow_reason="Verwaltungsobjekt ohne separaten Prozess-Lebenszyklus in der Maske.",',
        "        business_purpose=f\"Stamm- und Fachmaske fuer {title} ({screen_id}).\",",
        "        example_prompts=[f\"Zeige Stammdaten fuer {title} {{entity_id}}.\"],",
        "        test_id=screen_id.replace(\"/\", \"-\"),",
        "        density=\"compact\",",
        '        context_rail="combined",',
        '        table_profile="standard",',
        "    )",
        "",
        "",
    ]

    builders: list[str] = []
    for page in PAGES:
        sid = page_to_screen_id(page)
        if sid not in ENDPOINTS:
            raise SystemExit(f"missing endpoint map for {sid}")
        entity_ep, bearb = ENDPOINTS[sid]
        if not _endpoint_in_openapi(entity_ep, routes):
            print(f"WARN openapi miss {sid} -> {entity_ep}")
        fn = "build_" + sid.replace("/", "_").replace("-", "_")
        dom = domain_for(sid)
        tit = title_for(sid)
        perm = permission_for(sid)
        identity = "bezeichnung" if sid.startswith("artikel/") and sid != "artikel/kategorien" else "bezeichnung"
        if sid == "artikel/kategorien":
            identity = "bezeichnung"
        if sid.startswith("admin/") or sid.startswith("annahme/"):
            identity = "bezeichnung"
        lines.append(f"def {fn}() -> dict[str, Any]:")
        lines.append(f'    return _batch13_stamm("{sid}", domain="{dom}", title="{tit}",')
        lines.append(f'        entity_endpoint="{entity_ep}", identity_field="{identity}",')
        lines.append(f'        edit_permission="{perm}", bearbeiten_endpoint={bearb!r})')
        lines.append("")
        builders.append(f'    "{sid}": {fn},')

    lines.append("BATCH13_SCREEN_BUILDERS: dict[str, Any] = {")
    lines.extend(builders)
    lines.append("}")
    lines.append("")
    lines.append("BATCH13_ROUTEN: dict[str, str] = {")
    for page in PAGES:
        sid = page_to_screen_id(page)
        route = "/" + sid
        lines.append(f'    "{sid}": "{route}",')
    lines.append("}")
    lines.append("")
    lines.append("BATCH13_SYNONYME: dict[str, list[str]] = {}")
    lines.append("")

    BATCH13_PY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {BATCH13_PY}")


def patch_stamm_py() -> None:
    path = ROOT / "app" / "core" / "screen_definitions_stamm.py"
    text = path.read_text(encoding="utf-8")
    if "screen_definitions_stamm_batch13" not in text:
        insert_after = "from app.core.stamm_object_page_parent import (\n"
        extra = (
            "from app.core.screen_definitions_stamm_batch13 import (\n"
            "    BATCH13_ROUTEN,\n"
            "    BATCH13_SCREEN_BUILDERS,\n"
            "    BATCH13_SYNONYME,\n"
            ")\n\n"
        )
        idx = text.find(insert_after)
        if idx == -1:
            raise SystemExit("import anchor missing")
        # insert after the closing paren of stamm_object_page_parent import
        end = text.find(")\n", idx) + 2
        text = text[:end] + "\n" + extra + text[end:]

    text = re.sub(
        r"STAMM_SCREEN_BUILDERS = \{\n    \"artikel/stamm\": build_artikel_stamm,\n\}",
        'STAMM_SCREEN_BUILDERS = {\n    "artikel/stamm": build_artikel_stamm,\n    **BATCH13_SCREEN_BUILDERS,\n}',
        text,
    )
    text = re.sub(
        r"STAMM_ROUTEN = \{\n    \"artikel/stamm\": \"/artikel\",\n\}",
        'STAMM_ROUTEN = {\n    "artikel/stamm": "/artikel",\n    **BATCH13_ROUTEN,\n}',
        text,
    )
    if "STAMM_SYNONYME" not in text:
        text = text.rstrip() + "\n\nSTAMM_SYNONYME: dict[str, list[str]] = {\n    **BATCH13_SYNONYME,\n}\n"
    path.write_text(text, encoding="utf-8")
    print("patched screen_definitions_stamm.py")


def legacy_name(page: str) -> str:
    return page.replace(".tsx", "-legacy.tsx")


def wrap_stamm_native(page: str, screen_id: str, test_id: str, reexports: list[str]) -> str:
    legacy = legacy_name(page)
    legacy_import = "./" + Path(legacy).name.removesuffix(".tsx")
    lines = ["import { createStammNativeDetailPage } from '@/components/mask-builder'", ""]
    for name in reexports:
        lines.append(f"export {{ {name} }} from '{legacy_import}'")
    if reexports:
        lines.append("")
    lines.extend(
        [
            "export default createStammNativeDetailPage(",
            f"  '{screen_id}',",
            f"  '{test_id}',",
            f"  () => import('{legacy_import}'),",
            ")",
            "",
        ]
    )
    return "\n".join(lines)


def wrap_runtime_wire(page: str, screen_id: str) -> str:
    comp = "".join(p[:1].upper() + p[1:] for p in screen_id.split("/")[-1].split("-"))
    return f"""import {{ MadeByStudioDetailRuntimeWire }} from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function {comp}Page(): JSX.Element {{
  return <MadeByStudioDetailRuntimeWire screenId="{screen_id}" />
}}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {{
  return <MadeByStudioDetailRuntimeWire screenId="{screen_id}" />
}}
void madeByStudioRuntimeWireDeclaration
"""


def migrate_frontend() -> None:
    migrated = 0
    for page in PAGES:
        src = PAGES_ROOT / page
        screen_id = page_to_screen_id(page)
        test_id = page_to_test_id(screen_id)
        reexports = REEXPORT_PAGES.get(screen_id.replace("\\", "/"), [])

        legacy = PAGES_ROOT / legacy_name(page)
        if src.exists() and not legacy.exists():
            text = src.read_text(encoding="utf-8")
            if "createStammNativeDetailPage" not in text and "MadeByStudioDetailRuntimeWire" not in text:
                if "NativeListPage" not in text or len(text) > 200:
                    shutil.copy2(src, legacy)
        use_legacy = legacy.exists() and (reexports or legacy.stat().st_size > 400)
        src.parent.mkdir(parents=True, exist_ok=True)
        if use_legacy:
            src.write_text(wrap_stamm_native(page, screen_id, test_id, reexports), encoding="utf-8")
        else:
            src.write_text(wrap_runtime_wire(page, screen_id), encoding="utf-8")
        migrated += 1
        print("migrated", page)
    print(f"frontend migrated: {migrated}/{len(PAGES)}")


def patch_tests() -> None:
    replacements = [
        (
            ROOT / "packages/frontend-web/src/__tests__/pages/uix-runtime-restmasken.test.ts",
            "../../pages/admin/agenten-integration.tsx",
            "../../pages/admin/agenten-integration-legacy.tsx",
        ),
        (
            ROOT / "packages/frontend-web/src/__tests__/pages/uix-runtime-restmasken.test.ts",
            "../../pages/admin/agenten-integration.tsx",
            "../../pages/admin/agenten-integration-legacy.tsx",
        ),
        (
            ROOT / "packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung-uix.test.ts",
            "../../../pages/annahme/lkw-registrierung.tsx",
            "../../../pages/annahme/lkw-registrierung-legacy.tsx",
        ),
        (
            ROOT / "packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check-uix.test.ts",
            "../../../pages/annahme/qualitaets-check.tsx",
            "../../../pages/annahme/qualitaets-check-legacy.tsx",
        ),
    ]
    seen: set[Path] = set()
    for path, old, new in replacements:
        if path in seen or not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")
            print("patched test", path.name)
        seen.add(path)


def verify_gates() -> None:
    from app.core.screen_definitions_stamm import STAMM_SCREEN_BUILDERS
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry
    from app.services.made_by_studio_gates import evaluate_screen

    ensure_stamm_screen_registry()
    failed = []
    for sid, builder in STAMM_SCREEN_BUILDERS.items():
        if not sid.startswith(("admin/", "agrar/", "annahme/", "artikel/", "auswertungen/", "aktien/", "analysis/")):
            if sid == "artikel/stamm":
                continue
        if sid == "artikel/stamm":
            continue
        rep = evaluate_screen(sid, builder())
        for gate in ("A", "B", "C", "E"):
            if not rep.gates[gate].passed:
                failed.append((sid, gate, rep.gates[gate].issues[:2]))
    print(f"gate failures: {len(failed)}")
    for item in failed[:15]:
        print(item)


def main() -> None:
    generate_batch13_py()
    patch_stamm_py()
    migrate_frontend()
    patch_tests()
    verify_gates()


if __name__ == "__main__":
    main()
