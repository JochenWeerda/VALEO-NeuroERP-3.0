#!/usr/bin/env python3
"""Welche Policy-Form eine RLS-Tabelle traegt (Ratsche gegen abweichende Strukturen).

Zulaessig sind genau zwei Formen; alles andere ist ``abweichend``:

``getrennt``  vier permissive Policies fuer PUBLIC, eine je Befehl, keine weitere:

    tenant_isolation_select  FOR SELECT USING (eigen)          bzw. (eigen OR system) -> ``getrennt_system``
    tenant_isolation_insert  FOR INSERT WITH CHECK (eigen)
    tenant_isolation_update  FOR UPDATE USING (eigen) WITH CHECK (eigen)
    tenant_isolation_delete  FOR DELETE USING (eigen)

    eigen  = tenant_id = rls_current_tenant()
    system = tenant_id = 'system' AND rls_current_tenant() IS NOT NULL

    ``system``-Zeilen sind so hoechstens lesbar: UPDATE und DELETE sehen nur eigene Zeilen,
    und kein Schreiben kann eine Zeile auf ``system`` oder einen fremden Mandanten setzen.
    ``getrennt_system`` nur fuer Tabellen, deren Freigabe in docs/admin/rls-exceptions.json
    begruendet ist.

``alt``  eine ALL-Policy ``tenant_isolation`` (P3/P5/P6 vor der Korrektur). Sie laesst
    ``system``-Zeilen loeschen und per UPDATE uebernehmen. Codex hat P3/P5/P6 in
    RLS-ORDERED-INTEGRATION-20261027 auf die getrennte Form mit denselben Namen umgestellt
    (943ba2bb0); dort lesen die 501 Bestandstabellen ``system`` noch pauschal mit.

Altbestand = ``alt`` plus ``getrennt_system`` ohne Begruendung; seine Zahl darf nur sinken
(``altbestand_hoechstens``), je Tabellenfamilie wird die Lesefreigabe begruendet oder entfernt.

FORCE ROW LEVEL SECURITY bleibt aus (Plan 2.4: der Eigentuemer migriert).

    python scripts/rls_policy_shape.py      # Formen auf TEST_DATABASE_URL (zurueckgerollt) zaehlen
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter

OWN = "tenant_id=rls_current_tenant"
SHARED = "tenant_id=rls_current_tenantORtenant_id='system'ANDrls_current_tenantISNOTNULL"

# Name -> (polcmd, USING, WITH CHECK); USING von tenant_isolation_select ist eigen oder eigen+system.
SPLIT = {
    "tenant_isolation_select": ("r", (OWN, SHARED), None),
    "tenant_isolation_insert": ("a", None, OWN),
    "tenant_isolation_update": ("w", OWN, OWN),
    "tenant_isolation_delete": ("d", OWN, None),
}
LEGACY = ("tenant_isolation", "*", SHARED, OWN)

POLICIES_SQL = """
SELECT c.oid::regclass::text AS tbl, c.relforcerowsecurity AS force,
       p.polname, p.polcmd::text, p.polpermissive, p.polroles::oid[]::text,
       pg_get_expr(p.polqual, p.polrelid), pg_get_expr(p.polwithcheck, p.polrelid)
  FROM pg_class c
  LEFT JOIN pg_policy p ON p.polrelid = c.oid
 WHERE c.relrowsecurity
 ORDER BY 1, 3
"""


def normalize(expr: str | None) -> str | None:
    """PostgreSQL renders casts and parentheses depending on the column type; drop both."""
    if expr is None:
        return None
    expr = re.sub(r"::(?:text|character varying)", "", expr)
    expr = expr.replace("public.", "")
    return re.sub(r"[\s()]", "", expr)


def classify(force: bool, policies: list[tuple]) -> tuple[str, str]:
    """policies: (name, cmd, permissive, roles, qual, check) of one table."""
    if force:
        return "abweichend", "FORCE ROW LEVEL SECURITY gesetzt"
    named = {p[0]: p for p in policies if p[0] is not None}
    if not named:
        return "abweichend", "RLS ohne Policy"
    for name, cmd, permissive, roles, _q, _c in named.values():
        if not permissive:
            return "abweichend", f"{name}: restriktive Policy"
        if roles not in ("{0}", "[0]", [0]):
            return "abweichend", f"{name}: Rollen {roles} statt PUBLIC"
    if set(named) == {LEGACY[0]}:
        _n, cmd, _p, _r, qual, check = named[LEGACY[0]]
        if cmd == LEGACY[1] and normalize(qual) == LEGACY[2] and normalize(check) == LEGACY[3]:
            return "alt", ""
        return "abweichend", f"{LEGACY[0]}: Ausdruck oder Befehl weicht ab"
    if set(named) != set(SPLIT):
        return "abweichend", f"Policies {sorted(named)} statt {sorted(SPLIT)}"
    shared = False
    for name, (want_cmd, want_qual, want_check) in SPLIT.items():
        _n, cmd, _p, _r, qual, check = named[name]
        if cmd != want_cmd:
            return "abweichend", f"{name}: Befehl {cmd} statt {want_cmd}"
        qual, check = normalize(qual), normalize(check)
        if isinstance(want_qual, tuple):
            if qual not in want_qual:
                return "abweichend", f"{name}: USING {qual}"
            shared = qual == SHARED
        elif qual != want_qual:
            return "abweichend", f"{name}: USING {qual}"
        if check != want_check:
            return "abweichend", f"{name}: WITH CHECK {check}"
    return ("getrennt_system" if shared else "getrennt"), ""


def shapes(conn) -> dict[str, tuple[str, str]]:
    import sqlalchemy as sa

    tables: dict[str, list] = {}
    forced: dict[str, bool] = {}
    for tbl, force, name, cmd, permissive, roles, qual, check in conn.execute(sa.text(POLICIES_SQL)):
        forced[tbl] = force
        tables.setdefault(tbl, []).append((name, cmd, permissive, roles, qual, check))
    return {t: classify(forced[t], p) for t, p in tables.items()}


def main() -> int:
    import sqlalchemy as sa

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rls_inventory

    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        print("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt.")
        return 2
    engine = sa.create_engine(url)
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            rls_inventory._pending_upgrade(conn)
            result = shapes(conn)
        finally:
            tx.rollback()
    engine.dispose()
    print(dict(Counter(shape for shape, _ in result.values())))
    for table, (shape, detail) in sorted(result.items()):
        if shape == "abweichend":
            print(f"  {table}: {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
