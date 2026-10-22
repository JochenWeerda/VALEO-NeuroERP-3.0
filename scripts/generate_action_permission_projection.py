"""Rollen-Projektion der Maskenaktionen aus den Abhaengigkeiten ihrer Kommandowege (STAMMDATEN-BEARBEITEN-20261019).

Die Oberflaeche gab eine Aktion bisher nur frei, wenn ihr ``permission``-Name als Scope im Token stand (``erp_scopes``
je Nutzer) — ein Fachanwender mit der passenden Bereichsrolle sah den Knopf nicht, obwohl der Server ihn zuliess.
Hier entsteht dieselbe Entscheidung wie auf dem Server: Fuer jede Aktion mit Kommandoweg (und die Anlage) werden die Rollen der
``require_roles``-Abhaengigkeiten dieses Wegs gelesen. Jede Gruppe muss erfuellt sein (eine Rolle daraus).

    python scripts/generate_action_permission_projection.py          # schreiben
    python scripts/generate_action_permission_projection.py --check  # Drift pruefen

Wie ``generate_beleg_permission_projection.py``: eine Quelle (der Server), die Maske projiziert nur.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "packages/frontend-web/src/components/mask-builder/runtime/action-permissions.generated.json"


def _rollen_gruppen(dependant) -> list[list[str]]:  # noqa: ANN001
    gruppen: list[list[str]] = []
    stack = list(dependant.dependencies)
    while stack:
        dep = stack.pop()
        call = dep.call
        if getattr(call, "__qualname__", "").startswith("require_roles.<locals>"):
            frei = dict(zip(call.__code__.co_freevars, (c.cell_contents for c in call.__closure__ or ())))
            rollen = sorted(set(frei.get("needed") or ()) - {"manager"})
            if rollen and rollen not in gruppen:
                gruppen.append(rollen)
        stack.extend(dep.dependencies)
    return sorted(gruppen)


def _route(app, pfad: str, methode: str):  # noqa: ANN001
    from starlette.routing import Match

    konkret = re.sub(r"\{[^}]+\}", "X", pfad)
    scope = {"type": "http", "path": konkret, "method": methode, "root_path": "", "query_string": b"",
             "headers": []}
    for route in app.router.routes:
        treffer, _ = route.matches(scope)
        if treffer == Match.FULL:
            return route
    return None


def render() -> str:
    os.environ.setdefault("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")
    from app.core.screen_definitions import _SCREEN_DEFINITIONS, get_screen_definition
    from app.main import app
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry
    ensure_stamm_screen_registry()

    screens: dict[str, dict[str, list[list[str]]]] = {}
    for screen_id in sorted(_SCREEN_DEFINITIONS):
        definition = get_screen_definition(screen_id) or {}
        anlage = definition.get("creation") or {}
        anlage_als_aktion = [{"permission": anlage.get("permission"), "commandEndpoint": anlage.get("endpoint"),
                              "method": "POST"}] if anlage.get("endpoint") else []
        tabellen = [*(definition.get("tables") or []),
                    *(t for tab in definition.get("tabs") or [] for t in tab.get("tables") or [])]
        zeilen = [aktion for tabelle in tabellen for aktion in tabelle.get("rowActions") or []]
        for action in [*(definition.get("actions") or []), *zeilen, *anlage_als_aktion]:
            permission = action.get("permission")
            download = action.get("download") or {}
            endpoint = download.get("endpoint") or action.get("commandEndpoint")
            if not permission or not endpoint or permission.startswith(("belege.", "platform:")):
                continue
            route = _route(app, endpoint, "GET" if download else str(action.get("method") or "POST").upper())
            gruppen = _rollen_gruppen(route.dependant) if route is not None and hasattr(route, "dependant") else []
            if gruppen:
                screens.setdefault(screen_id, {})[permission] = gruppen
    from app.services.studio_entity_contracts import EntitySpec, POLICIES
    from app.services.studio_entity_router import build_router
    generated_entities = {}
    for domain in POLICIES:
        spec = EntitySpec(name='studio_permission_probe', domain=domain, label='Permission projection',
                          columns=[{'name':'label','type':'text','nullable':False}])
        commands = build_router(spec)
        route = next(route for route in commands.routes if route.path.endswith('/actions/create'))
        generated_entities[f'studio.entity.{domain}.write'] = _rollen_gruppen(route.dependant)
    return json.dumps({"schemaVersion": 1, "source": "require_roles der Kommandowege (scripts/"
                       "generate_action_permission_projection.py)", "screens": screens, "generatedEntities": generated_entities},
                      ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != expected:
            print("Projektion der Aktionsrechte veraltet; neu erzeugen.")
            return 1
        print("Projektion der Aktionsrechte aktuell.")
        return 0
    OUT.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Geschrieben: {OUT.relative_to(ROOT)} ({sum(len(v) for v in json.loads(expected)['screens'].values())} "
          "Aktionsrechte)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
