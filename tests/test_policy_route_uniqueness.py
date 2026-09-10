"""
Vertragstests fuer die Routen unter /api/mcp/policy
(Slice POLICY-ROUTE-DEDUP-20260910).

Hintergrund: ``app/api/v1/endpoints/policies.py`` wird in ``main.py`` frueher
registriert als ``app/policy/router.py`` und hat dessen gleichnamige Routen
ueberlagert. Betroffen waren /create, /update, /delete, /export und /restore —
alle fuenf im ueberlagerten Router mit ``require_roles`` deklariert, in der
wirksamen Implementierung ohne jede Rollenpruefung. Die Guards waren damit
wirkungslos: jeder authentifizierte Token konnte Policies aendern und ueber
/restore saemtliche Regeln ersetzen.

Diese Tests halten fest, dass es je Pfad genau eine Implementierung gibt und
dass die schreibenden Routen eine Rollenpruefung tragen.
"""

import pytest

PRAEFIX = "/api/mcp/policy"


@pytest.fixture(scope="module")
def policy_routes():
    from main import app

    routen = {}
    for r in app.routes:
        pfad = getattr(r, "path", "")
        if not pfad.startswith(PRAEFIX):
            continue
        methoden = tuple(sorted(getattr(r, "methods", []) or ["WEBSOCKET"]))
        routen.setdefault((pfad, methoden), []).append(r)
    return routen


def _hat_rollenpruefung(route) -> bool:
    dependant = getattr(route, "dependant", None)
    if dependant is None:
        return False

    def walk(d) -> bool:
        for sub in d.dependencies:
            name = getattr(sub.call, "__qualname__", str(sub.call))
            if "require_roles" in name:
                return True
            if walk(sub):
                return True
        return False

    return walk(dependant)


class TestRoutenEindeutigkeit:
    def test_kein_pfad_wird_doppelt_bedient(self, policy_routes):
        doppelt = {
            f"{m[0]} {p}": [r.endpoint.__module__ for r in rs]
            for (p, m), rs in policy_routes.items()
            if len(rs) > 1
        }
        assert doppelt == {}, doppelt

    def test_erwartete_pfade_sind_vorhanden(self, policy_routes):
        vorhanden = {p for (p, _) in policy_routes}
        for pfad in (
            "/list", "/upsert", "/create", "/update", "/delete", "/test",
            "/export", "/restore", "/backup", "/backups", "/backups/restore",
        ):
            assert PRAEFIX + pfad in vorhanden, pfad

    def test_datei_restore_liegt_kollisionsfrei(self, policy_routes):
        """Die JSON-Variante bedient /restore, die Datei-Variante
        /backups/restore — frueher lagen beide auf /restore."""
        json_restore = policy_routes[(PRAEFIX + "/restore", ("POST",))][0]
        datei_restore = policy_routes[(PRAEFIX + "/backups/restore", ("POST",))][0]
        assert json_restore.endpoint.__module__ == "app.api.v1.endpoints.policies"
        assert datei_restore.endpoint.__module__ == "app.policy.router"


class TestRollenpruefung:
    @pytest.mark.parametrize(
        "pfad,methode",
        [
            ("/upsert", "POST"),
            ("/create", "POST"),
            ("/update", "POST"),
            ("/delete", "POST"),
            ("/export", "GET"),
            ("/restore", "POST"),
            ("/backup", "POST"),
            ("/backups", "GET"),
            ("/backups/restore", "POST"),
        ],
    )
    def test_schreibende_und_exportierende_routen_sind_geschuetzt(
        self, policy_routes, pfad, methode
    ):
        route = policy_routes[(PRAEFIX + pfad, (methode,))][0]
        assert _hat_rollenpruefung(route), f"{methode} {pfad} ohne Rollenpruefung"

    def test_backup_ist_kein_get(self, policy_routes):
        """Der Aufruf legt eine Datei an. Als GET traf ihn der naechtliche
        Runtime-Sweep und erzeugte bei jedem Lauf eine Sicherung."""
        vorhanden = {(p, m) for (p, ms) in policy_routes for m in ms}
        assert (PRAEFIX + "/backup", "POST") in vorhanden
        assert (PRAEFIX + "/backup", "GET") not in vorhanden

    @pytest.mark.parametrize("pfad,methode", [("/list", "GET"), ("/test", "POST")])
    def test_lesende_routen_bleiben_ohne_rollenpruefung(
        self, policy_routes, pfad, methode
    ):
        """Bewusst offen, wie im urspruenglichen Router deklariert — hier
        festgehalten, damit eine Aenderung eine Entscheidung bleibt."""
        route = policy_routes[(PRAEFIX + pfad, (methode,))][0]
        assert not _hat_rollenpruefung(route)
