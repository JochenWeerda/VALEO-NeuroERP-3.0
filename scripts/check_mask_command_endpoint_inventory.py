#!/usr/bin/env python3
"""SPEC-P1-04 — Inventur: keine Aktion einer nativen Maske ohne Weg.

Prüft alle ScreenDefinitions mit adapter.temporary=False. Eine Aktion hat einen Weg,
wenn sie einen ``commandEndpoint``, einen gueltigen ``inputFlow``, eine
``navigationRoute`` oder ein ``command`` hat (Capture-Masken: die Seite verdrahtet den
Befehl; ihr ``stubReason`` ist dort Beschreibung, kein Stub).

**Bekannte Luecken** (``stubReason`` ohne jeden Weg) sind nur aus ``BEKANNTE_LUECKEN``
erlaubt — die Liste darf nur schrumpfen. Bis 07.10.2026 verbot dieses Gate jeden
``stubReason``; das hat Endpunkte erzwungen, die ``success: true`` meldeten, ohne etwas
zu tun (docs/quality-assurance/mask-aktionen-wirkung-20261007.md).

Exit 0 = OK, Exit 1 = Verstöße.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition  # noqa: E402


#: Ehrliche Luecken: kein Fachweg oder keine Eingabe in der Maske. Nur schrumpfen.
BEKANNTE_LUECKEN: set[str] = set()


def valid_input_flow(action: dict) -> bool:
    flow = action.get("inputFlow")
    return bool(
        isinstance(flow, dict)
        and flow.get("kind") == "humanForm"
        and isinstance(flow.get("submitEndpoint"), str)
        and flow["submitEndpoint"].startswith("/api/v1/")
        and flow.get("method") in {"POST", "PUT", "PATCH", "DELETE"}
        and action.get("forbiddenForAgents") is True
        and not action.get("commandEndpoint")
    )


def main() -> int:
    violations: list[str] = []

    for screen_id in sorted(SCREEN_DEFINITION_BUILDERS.keys()):
        sd = get_screen_definition(screen_id)
        if not sd:
            continue
        if sd.get("adapter", {}).get("temporary", True):
            continue

        for action in sd.get("actions", []):
            key = action.get("key", "?")
            hat_weg = bool(
                action.get("commandEndpoint") or action.get("command")
                or action.get("navigationRoute") or valid_input_flow(action)
            )
            erlaubt = BEKANNTE_LUECKEN
            if action.get("stubReason") and not hat_weg and f"{screen_id}/{key}" not in erlaubt:
                violations.append(f"{screen_id}/{key}: neue Luecke ohne Weg, stubReason={action['stubReason']!r}")
            if f"{screen_id}/{key}" in erlaubt and hat_weg:
                violations.append(f"{screen_id}/{key}: hat jetzt einen Weg — aus der Ausnahmeliste streichen")

            endpoint = action.get("commandEndpoint")
            if action.get("inputFlow") and not valid_input_flow(action):
                violations.append(f"{screen_id}/{key}: ungueltiger humanForm-Eingabevertrag")
            if endpoint and action.get("stubReason"):
                violations.append(f"{screen_id}/{key}: commandEndpoint + stubReason gleichzeitig")

            # Mutations-Actions ohne Endpoint (edit-only ausgenommen)
            if (
                not endpoint
                and not valid_input_flow(action)
                and not action.get("stubReason")
                and action.get("key") not in ("edit",)
                and action.get("dangerLevel") in ("moderate", "high", "critical")
            ):
                violations.append(f"{screen_id}/{key}: high-risk action ohne commandEndpoint")

    if violations:
        print("Mask commandEndpoint inventory FAILED:\n")
        for v in violations:
            print(f"  - {v}")
        return 1

    native_count = sum(
        1 for sid in SCREEN_DEFINITION_BUILDERS
        if not (get_screen_definition(sid) or {}).get("adapter", {}).get("temporary", True)
    )
    print(f"Mask commandEndpoint inventory OK ({native_count} native ScreenDefinitions, "
          f"{len(BEKANNTE_LUECKEN)} bekannte Luecken).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
