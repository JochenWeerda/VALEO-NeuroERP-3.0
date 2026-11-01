#!/usr/bin/env python3
"""Wire last handgebaut routes: minimal ScreenDefinitions + thin Native/Cockpit pages."""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages"
OUT = ROOT / "app" / "core" / "screen_definitions_finisher.py"
SCREEN_DEF = ROOT / "app" / "core" / "screen_definitions.py"

# screen_id, title, domain, endpoint, layout: list|cockpit
FINISHER: list[tuple[str, str, str, str, str]] = [
    ("agrar/aussaat/liste", "Aussaat", "agrar", "/api/v1/agrar/aussaat", "list"),
    ("copilot", "Copilot", "workspace", "/api/v1/analytics/kpis", "cockpit"),
    ("analytics", "Analytics", "workspace", "/api/v1/analytics/kpis", "cockpit"),
    ("document", "Dokument", "workspace", "/api/mcp/documents/analytics/customer-analytics", "cockpit"),
    ("einstellungen/system", "Systemeinstellungen", "admin", "/api/v1/config/system", "cockpit"),
    ("energie/verbrauch", "Energieverbrauch", "energie", "/api/v1/energie/verbrauch", "cockpit"),
    ("errors/NotFound", "Seite nicht gefunden", "workspace", "/api/v1/health", "cockpit"),
    ("finance", "Finance", "finance", "/api/v1/finance/overview", "cockpit"),
    ("hilfe", "Hilfe", "workspace", "/api/v1/help/topics", "cockpit"),
    ("inventory/adjust", "Bestandskorrektur", "lager", "/api/v1/inventory/adjustments", "list"),
    ("lager/bestandsuebersicht", "Bestandsübersicht", "lager", "/api/v1/inventory/stock", "list"),
    ("nachhaltigkeit/biodiversitaet", "Biodiversität", "nachhaltigkeit", "/api/v1/sustainability/biodiversity", "cockpit"),
    ("nachhaltigkeit/co2-bilanz", "CO2-Bilanz", "nachhaltigkeit", "/api/v1/sustainability/co2", "cockpit"),
    ("nachhaltigkeit/esg-report", "ESG-Report", "nachhaltigkeit", "/api/v1/sustainability/esg", "cockpit"),
    ("nawaro/anbauflaechen", "Anbauflächen", "nawaro", "/api/v1/nawaro/anbauflaechen", "list"),
    ("nawaro/mitteilung-drucken", "Mitteilung drucken", "nawaro", "/api/v1/nawaro/mitteilungen", "cockpit"),
    ("nawaro/raps-profil", "Raps-Profil", "nawaro", "/api/v1/nawaro/raps-profil", "cockpit"),
    ("nawaro/vertraege", "NaWaRo-Verträge", "nawaro", "/api/v1/nawaro/vertraege", "list"),
    ("policies", "Richtlinien", "admin", "/api/v1/policies", "list"),
    ("portal/portal", "Portal", "portal", "/api/v1/portal/overview", "cockpit"),
    ("pricing", "Preise", "preise", "/api/v1/pricing/overview", "cockpit"),
    ("public/verify", "Verifikation", "workspace", "/api/v1/public/verify", "cockpit"),
    ("schichtplan/liste", "Schichtplan", "personal", "/api/v1/personal/schichtplan", "list"),
    ("statistik/bewegungen", "Bewegungsstatistik", "statistik", "/api/v1/statistics/movements", "list"),
    ("stock-management", "Bestandsführung", "lager", "/api/v1/inventory/stock", "list"),
    ("termine/kalender", "Kalender", "termine", "/api/v1/calendar/events", "cockpit"),
    ("versand/frachtdokumente", "Frachtdokumente", "versand", "/api/v1/logistics/freight-documents", "list"),
    ("versand/paket-etikett", "Paket-Etikett", "versand", "/api/v1/logistics/parcel-labels", "cockpit"),
    ("weighing", "Wiegung", "waage", "/api/v1/weighing/sessions", "list"),
    ("wissen/wissensbasis", "Wissensbasis", "wissen", "/api/v1/knowledge/articles", "list"),
    ("workflows/approval", "Freigaben", "workflow", "/api/v1/workflows/approvals", "list"),
    ("workflows/trigger", "Workflow-Trigger", "workflow", "/api/v1/workflows/triggers", "list"),
]

ROUTE_TO_MODULE: dict[str, str] = {
    "agrar/aussaat": "@/pages/agrar/aussaat/liste",
    "agrar/aussaat/liste": "@/pages/agrar/aussaat/liste",
    "copilot": "@/pages/analytics",
    "analytics": "@/pages/analytics",
    "document": "@/pages/document",
    "einstellungen/system": "@/pages/einstellungen/system",
    "energie": "@/pages/energie/verbrauch",
    "energie/verbrauch": "@/pages/energie/verbrauch",
    "errors/NotFound": "@/pages/errors/NotFound",
    "finance": "@/pages/finance/index",
    "hilfe": "@/pages/hilfe",
    "inventory/adjust": "@/pages/inventory",
    "lager/bestandsuebersicht": "@/pages/lager/bestandsuebersicht",
    "nachhaltigkeit/biodiversitaet": "@/pages/nachhaltigkeit/biodiversitaet",
    "nachhaltigkeit/co2-bilanz": "@/pages/nachhaltigkeit/co2-bilanz",
    "nachhaltigkeit/esg-report": "@/pages/nachhaltigkeit/esg-report",
    "nawaro/anbauflaechen": "@/pages/nawaro/anbauflaechen",
    "nawaro/mitteilung-drucken": "@/pages/nawaro/mitteilung-drucken",
    "nawaro/raps-profil": "@/pages/nawaro/raps-profil",
    "nawaro/vertraege": "@/pages/nawaro/vertraege",
    "policies": "@/pages/policy-manager",
    "policy-manager": "@/pages/policy-manager",
    "portal/portal": "@/pages/portal/index",
    "pricing": "@/pages/pricing",
    "public/verify": "@/pages/public/verify",
    "schichtplan": "@/pages/schichtplan/liste",
    "statistik/bewegungen": "@/pages/statistik/bewegungen",
    "stock-management": "@/pages/stock-management",
    "termine/kalender": "@/pages/termine/kalender",
    "versand": "@/pages/versand/frachtdokumente",
    "versand/frachtdokumente": "@/pages/versand/frachtdokumente",
    "versand/paket-etikett": "@/pages/versand/paket-etikett",
    "weighing": "@/pages/weighing",
    "wissen/wissensbasis": "@/pages/wissen/wissensbasis",
    "workflows/approval": "@/pages/workflows/approval",
    "workflows/trigger": "@/pages/workflows/trigger",
}


def fn_name(screen_id: str) -> str:
    return "build_" + re.sub(r"[^a-zA-Z0-9]+", "_", screen_id).strip("_").lower() + "_screen_definition"


def test_id(screen_id: str) -> str:
    return screen_id.replace("/", "-")


def py_builder(screen_id: str, title: str, domain: str, endpoint: str, layout: str) -> str:
    fn = fn_name(screen_id)
    perm = f"{domain}.read" if domain != "workspace" else "read"
    cols = '[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]'
    if layout == "list":
        return textwrap.dedent(
            f'''
            def {fn}() -> dict[str, Any]:
                return build_stamm_list_screen(
                    screen_id="{screen_id}",
                    domain="{domain}",
                    title="{title}",
                    subtitle="{domain}",
                    endpoint="{endpoint}",
                    row_route=None,
                    columns={cols},
                    actions=[stamm_list_export_action()],
                    row_actions=[],
                    purpose="{title} finden und auswerten.",
                    prompts=["Zeige {title}."],
                    bundle="{domain}",
                    no_workflow="Read-Model-Liste ohne Prozessband.",
                )
            '''
        )
    return textwrap.dedent(
        f'''
        def {fn}() -> dict[str, Any]:
            cols = {cols}
            return build_cockpit_overview_screen(
                screen_id="{screen_id}",
                domain="{domain}",
                title="{title}",
                subtitle="{domain}",
                business_purpose="{title} mandantensicher als Cockpit bereitstellen.",
                example_prompts=["Zeige {title}."],
                test_id="{test_id(screen_id)}",
                data_sources=[cockpit_entity_source("{endpoint}")],
                tables=[cockpit_summary_table(table_key="list", label="{title}", columns=cols)],
                actions=[cockpit_refresh_action(permission="{perm}")],
                context_rail="combined",
            )
        '''
    )


def write_tsx(module: str, screen_id: str, layout: str) -> None:
    rel = module.replace("@/pages/", "")
    path = PAGES / Path(*rel.split("/"))
    if not path.suffix:
        path = path.with_suffix(".tsx")
    tid = test_id(screen_id)
    if layout == "list":
        content = textwrap.dedent(
            f'''\
            import {{ NativeListPage }} from '@/components/mask-builder/NativeListPage'

            export default function Page(): JSX.Element {{
              return <NativeListPage screenId="{screen_id}" testId="screen-{tid}" />
            }}
            '''
        )
    else:
        content = textwrap.dedent(
            f'''\
            import {{ UniversalNativeCockpitPage }} from '@/components/mask-builder/UniversalNativeCockpitPage'

            export default function Page(): JSX.Element {{
              return (
                <UniversalNativeCockpitPage
                  screenId="{screen_id}"
                  testId="screen-{tid}"
                />
              )
            }}
            '''
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT))
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS

    builders: list[str] = []
    registry: list[tuple[str, str]] = []
    wrapped_modules: dict[str, tuple[str, str]] = {}

    for screen_id, title, domain, endpoint, layout in FINISHER:
        if screen_id in SCREEN_DEFINITION_BUILDERS:
            fn = fn_name(screen_id)
        else:
            builders.append(py_builder(screen_id, title, domain, endpoint, layout))
            fn = fn_name(screen_id)
            registry.append((screen_id, fn))
        mod = ROUTE_TO_MODULE.get(screen_id)
        if mod and mod not in wrapped_modules:
            wrapped_modules[mod] = (screen_id, layout)

    header = textwrap.dedent(
        '''\
        """Finisher ScreenDefinitions for last handgebaut routes."""
        from __future__ import annotations
        from typing import Any
        from app.core.cockpit_overview_parent import (
            build_cockpit_overview_screen,
            cockpit_entity_source,
            cockpit_refresh_action,
            cockpit_summary_table,
        )
        from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

        '''
    )
    body = header + "\n".join(builders)
    reg = "\nFINISHER_SCREEN_BUILDERS: dict[str, Any] = {\n"
    for sid, fn in registry:
        reg += f'    "{sid}": {fn},\n'
    reg += "}\n"
    OUT.write_text(body + reg, encoding="utf-8", newline="\n")

    if "screen_definitions_finisher" not in SCREEN_DEF.read_text(encoding="utf-8"):
        text = SCREEN_DEF.read_text(encoding="utf-8")
        text = text.replace(
            "from app.core.screen_definitions_domain_batch15 import BATCH15_SCREEN_BUILDERS\n",
            "from app.core.screen_definitions_domain_batch15 import BATCH15_SCREEN_BUILDERS\n"
            "from app.core.screen_definitions_finisher import FINISHER_SCREEN_BUILDERS\n",
        )
        text = text.replace(
            "    **BATCH15_SCREEN_BUILDERS,\n}",
            "    **BATCH15_SCREEN_BUILDERS,\n    **FINISHER_SCREEN_BUILDERS,\n}",
        )
        SCREEN_DEF.write_text(text, encoding="utf-8", newline="\n")

    for mod, (screen_id, layout) in wrapped_modules.items():
        write_tsx(mod, screen_id, layout)

    print(json.dumps({"builders": len(registry), "wrapped_modules": len(wrapped_modules)}, indent=2))


if __name__ == "__main__":
    main()
