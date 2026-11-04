"""Wertelisten der Masken gegen die des Servers.

Eine Auswahl in der Maske (``select``/``multiselect`` mit ``options``) darf nur Werte anbieten, die der Kommandoweg
annimmt. Der Server legt sie im Request-Modell fest: ``Literal[...]`` oder ein Muster ``^(a|b|c)$``. Weicht die
Maske ab, scheitert die Eingabe erst beim Speichern (422) - oder ein Wert des Servers ist in der Maske nicht waehlbar.
Gesucht wird in den Eingabefeldern der Aktionen (``inputFields``) und den Feldern einer Maske, deren
Speicher-Aktion den Kommandoweg traegt.
"""
from __future__ import annotations

import re
import typing
from typing import Any

_MUSTER = re.compile(r"^\^\(([A-Za-z0-9_|.\-]+)\)\$$")


def _erlaubt(annotation: Any, metadaten: list[Any]) -> set[str] | None:
    for kandidat in (annotation, *typing.get_args(annotation)):
        if typing.get_origin(kandidat) is typing.Literal:
            return {str(w) for w in typing.get_args(kandidat)}
        if typing.get_origin(kandidat) in (list, set, tuple):
            innen = _erlaubt(typing.get_args(kandidat)[0], []) if typing.get_args(kandidat) else None
            if innen:
                return innen
    for meta in metadaten:
        muster = getattr(meta, "pattern", None)
        if isinstance(muster, str) and (treffer := _MUSTER.match(muster)):
            return set(treffer[1].split("|"))
    return None


def _modell(route: Any) -> Any:
    body = getattr(getattr(route, "dependant", None), "body_params", None) or []
    for param in body:
        typ = getattr(param, "type_", None) or getattr(getattr(param, "field_info", None), "annotation", None)
        if hasattr(typ, "model_fields"):
            return typ
    return None


def _route(app: Any, pfad: str, methode: str) -> Any:
    from starlette.routing import Match

    scope = {"type": "http", "path": re.sub(r"\{[^}]+\}", "x", pfad), "method": methode}
    for route in app.routes:
        if hasattr(route, "matches") and route.matches(scope)[0] == Match.FULL:
            return route
    return None


def abweichungen(app: Any, definitionen: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Je Maske, Aktion und Feld: Optionen der Maske, die der Server ablehnt, und Serverwerte ohne Option."""
    funde: list[dict[str, Any]] = []
    for screen_id, definition in sorted(definitionen.items()):
        felder = {f.get("key"): f for f in definition.get("fields") or []}
        for tab in definition.get("tabs") or []:
            felder.update({f.get("key"): f for f in tab.get("fields") or []})
        for aktion in definition.get("actions") or []:
            pfad = aktion.get("commandEndpoint")
            if not pfad:
                continue
            route = _route(app, pfad, str(aktion.get("method") or "POST").upper())
            modell = _modell(route) if route is not None else None
            if modell is None:
                continue
            eingaben = {f.get("key"): f for f in aktion.get("inputFields") or []} or felder
            for name, info in modell.model_fields.items():
                feld = eingaben.get(name) or eingaben.get(info.alias or "")
                if not feld or feld.get("type") not in ("select", "multiselect") or not feld.get("options"):
                    continue
                erlaubt = _erlaubt(info.annotation, list(info.metadata))
                if erlaubt is None:
                    continue
                angeboten = {str(o.get("value")) for o in feld["options"]}
                fremd, fehlend = sorted(angeboten - erlaubt), sorted(erlaubt - angeboten)
                if fremd or fehlend:
                    funde.append({"screen": screen_id, "aktion": aktion.get("key"), "feld": feld.get("key"),
                                  "nicht_erlaubt": fremd, "nicht_waehlbar": fehlend})
    return funde
