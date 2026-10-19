#!/usr/bin/env python3
"""Inventar: Schreibwege (POST/PUT/PATCH/DELETE) der API ohne erkennbare Rollen- oder Rechtepruefung.

    python scripts/check_write_routes_roles.py              # Bericht
    python scripts/check_write_routes_roles.py --check      # Ratsche (CI): keine neuen Wege ohne Pruefung
    python scripts/check_write_routes_roles.py --write-baseline

Am 19.10.2026 fanden sich im Rollout MASK-COMMANDS mehrere Router, deren Schreibwege jede angemeldete Person
des Mandanten bedienen konnte (Produktionsleitstand, Fremdware, Inventur-Nebenlaeufe, Tankanlage, MDE,
Dokumentenruecklauf, Auftraege). Die Bearer-Pruefung sagt nur *wer*, nicht *was er darf*.

Ein Weg gilt als geprueft, wenn in seinem Abhaengigkeitsbaum eine Rollen-/Rechte-/Scope-Abhaengigkeit haengt
(``require_roles``, ``require_permission``, ``require_scopes``, Bereichsrollen aus ``app.auth``) oder sein
Funktionskoerper eine solche Pruefung aufruft (``require_roles(user, ...)``, ``verlange_rolle``, ``check_role`` …).
Das ist eine Heuristik ohne Gewaehr fuer die Richtigkeit der Rolle — sie findet Wege **ohne** Pruefung.

Bestandsluecken stehen in ``config/write_routes_without_roles.json`` und duerfen nur schrumpfen.
Exit 0 = OK, Exit 1 = neuer Weg ohne Pruefung.
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BASELINE = ROOT / "config" / "write_routes_without_roles.json"

#: Aufrufe im Funktionskoerper, die eine Rolle oder ein Recht pruefen.
KOERPER = re.compile(
    r"\b(require_roles|require_role|require_permission|require_scopes|require_all_scopes|require_roles_and_scopes|"
    r"verlange_rolle|check_role|check_permission|has_role|has_permission|_nur_leser|_require_role|_require_roles|"
    r"_pruefe_rolle|pruefe_rolle|darf_|rollen_von|_assert_role|assert_role|ensure_role|_check_roles?)\s*\("
)
#: Namen von Abhaengigkeiten, die eine Rolle/ein Recht pruefen (Fabriken liefern innere Funktionen).
ABHAENGIGKEIT = re.compile(r"(require_|_dep$|role|recht|permission|scope|write|admin|read|beleg_|_lesen|_schreiben)",
                           re.I)
#: Wege, die bewusst ohne Fachrolle offen sind (Anmeldung, eigene Sitzung, Geraeteeingang mit eigener Pruefung).
AUSGENOMMEN = re.compile(r"^/api/v1/(auth|session|sessions|me|users/me|portal)(/|$)|^/api/events|^/health|^/metrics")


def _abhaengigkeit_prueft(dependant) -> bool:  # noqa: ANN001
    stack = list(dependant.dependencies)
    while stack:
        dep = stack.pop()
        call = dep.call
        name = getattr(call, "__qualname__", "") or getattr(call, "__name__", "")
        module = getattr(call, "__module__", "") or ""
        if name.endswith("require_bearer_token") or name in {"get_db", "get_tenant_id", "get_current_user"}:
            stack.extend(dep.dependencies)
            continue
        if module.startswith(("app.auth", "app.core.rbac", "app.core.security", "app.core.permissions")) and \
                ABHAENGIGKEIT.search(name):
            return True
        if "require_roles" in name or "require_permission" in name or "require_scope" in name:
            return True
        stack.extend(dep.dependencies)
    return False


def _koerper_prueft(endpoint) -> bool:  # noqa: ANN001
    try:
        quelle = inspect.getsource(endpoint)
    except (OSError, TypeError):
        return False
    return bool(KOERPER.search(quelle))


def inventar() -> list[str]:
    os.environ.setdefault("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")
    from fastapi.routing import APIRoute

    from app.main import app

    offen = set()
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        methoden = sorted(set(route.methods or ()) & {"POST", "PUT", "PATCH", "DELETE"})
        if not methoden or AUSGENOMMEN.search(route.path):
            continue
        if _abhaengigkeit_prueft(route.dependant) or _koerper_prueft(route.endpoint):
            continue
        for methode in methoden:
            offen.add(f"{methode} {route.path}")
    return sorted(offen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)
    aktuell = inventar()
    if args.write_baseline:
        BASELINE.write_text(json.dumps({"_hinweis": "Nur schrumpfen. Erzeugt von scripts/check_write_routes_roles.py "
                                                    "--write-baseline.", "wege": aktuell},
                                       ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if not args.check:
        print(f"{len(aktuell)} Schreibwege ohne erkennbare Rollenpruefung")
        if not args.write_baseline:
            print("\n".join(aktuell))
        return 0
    erlaubt = set(json.loads(BASELINE.read_text(encoding="utf-8"))["wege"])
    neu = sorted(set(aktuell) - erlaubt)
    geschlossen = sorted(erlaubt - set(aktuell))
    if geschlossen:
        print(f"Hinweis: {len(geschlossen)} geschlossen — mit --write-baseline aus der Ratsche nehmen")
    if neu:
        print(f"FEHLER: {len(neu)} neue Schreibwege ohne Rollenpruefung:")
        print("\n".join(f"  + {w}" for w in neu))
        return 1
    print(f"Rollen-Ratsche OK: {len(aktuell)} Bestandswege ohne Pruefung (nur schrumpfen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
