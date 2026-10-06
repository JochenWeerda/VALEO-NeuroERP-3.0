"""Die Zerlegung von personal.py — gleiche Wege, kleinere Datei.

`app/api/v1/endpoints/personal.py` stand mit 3315 Zeilen in der Godfile-Ratsche
und wuchs auf 3342. Statt die Schwelle anzuheben sind zwei Fächer
herausgenommen, die mit der Personalverwaltung nur den Prefix `/personal` teilen:
das Bewerbermanagement und die Lohnabrechnung.

**Eine Zerlegung ist keine Gelegenheit, Verhalten zu ändern.** Diese Verträge
prüfen deshalb vor allem, dass sich *nichts* geändert hat: dieselben Pfade,
dieselben Methoden, jeder genau einmal montiert — und dass der Code wortgleich
umgezogen ist.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PERSONAL = Path("app/api/v1/endpoints/personal.py")
BEWERBUNGEN = Path("app/api/v1/endpoints/personal_bewerbungen.py")
LOHN = Path("app/api/v1/endpoints/personal_lohnabrechnung.py")

#: Die Wege, die umgezogen sind — Pfad und Methode wie vorher.
UMGEZOGEN = {
    ("GET", "/api/v1/personal/applications"),
    ("POST", "/api/v1/personal/applications"),
    ("PATCH", "/api/v1/personal/applications/{application_id}/stage"),
    ("DELETE", "/api/v1/personal/applications/{application_id}"),
    ("POST", "/api/v1/personal/lohn/berechnung"),
    ("POST", "/api/v1/personal/lohn/closeout-preview"),
}


def _wege() -> list[tuple[str, str]]:
    from app.main import app

    gefunden = []
    for route in app.routes:
        pfad = getattr(route, "path", "")
        for methode in getattr(route, "methods", set()) or set():
            gefunden.append((methode, pfad))
    return gefunden


class TestWegeUnveraendert:
    def test_alle_umgezogenen_wege_sind_erreichbar(self):
        vorhanden = set(_wege())
        fehlend = UMGEZOGEN - vorhanden
        assert not fehlend, fehlend

    def test_kein_weg_ist_doppelt_montiert(self):
        """Zwei Router unter einem Prefix sind die Stelle, an der das passiert."""
        from collections import Counter

        zaehler = Counter(w for w in _wege() if w[1].startswith("/api/v1/personal"))
        doppelt = {w: n for w, n in zaehler.items() if n > 1}
        assert not doppelt, doppelt

    def test_die_festen_pfade_stehen_vor_dem_sammelrouter(self):
        """Heute gibt es keinen Platzhalter auf oberster Ebene — das soll so bleiben.

        Faende sich einer in `personal.py`, wuerde er `/applications` und `/lohn/…`
        verschlucken, wenn er vorher montiert ist. Die Reihenfolge ist deshalb
        festgelegt und wird hier festgehalten.
        """
        quelle = Path("app/api/v1/api.py").read_text(encoding="utf-8")
        i_bewerbung = quelle.index("personal_bewerbungen.router")
        i_lohn = quelle.index("personal_lohnabrechnung.router")
        i_personal = quelle.index("    personal.router,")
        assert i_bewerbung < i_personal
        assert i_lohn < i_personal

    def test_personal_hat_keinen_platzhalter_auf_oberster_ebene(self):
        baum = ast.parse(PERSONAL.read_text(encoding="utf-8"))
        platzhalter = []
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            funk = knoten.func
            if not (isinstance(funk, ast.Attribute) and isinstance(funk.value, ast.Name)):
                continue
            if funk.value.id != "router":
                continue
            if not knoten.args or not isinstance(knoten.args[0], ast.Constant):
                continue
            pfad = knoten.args[0].value
            if isinstance(pfad, str) and pfad.startswith("/{"):
                platzhalter.append(pfad)
        assert not platzhalter, platzhalter


class TestDateigroesse:
    def test_personal_liegt_unter_der_alten_schwelle(self):
        zeilen = sum(1 for _ in PERSONAL.open(encoding="utf-8"))
        assert zeilen < 3315, zeilen

    def test_baseline_nennt_die_neue_groesse(self):
        """Die Ratsche ist nur dann eine, wenn die Baseline mitgeht."""
        baseline = json.loads(Path("config/godfile_baseline.json").read_text(encoding="utf-8"))
        eintrag = baseline["files"]["app/api/v1/endpoints/personal.py"]
        zeilen = sum(1 for _ in PERSONAL.open(encoding="utf-8"))
        assert eintrag == zeilen, (eintrag, zeilen)

    def test_die_neuen_module_sind_keine_godfiles(self):
        for pfad in (BEWERBUNGEN, LOHN):
            zeilen = sum(1 for _ in pfad.open(encoding="utf-8"))
            assert zeilen < 1000, (pfad, zeilen)


class TestUmzugOhneAenderung:
    def test_der_code_ist_wortgleich_umgezogen(self):
        """Stichproben, die bei einer stillen Aenderung auffallen wuerden."""
        bewerbung = BEWERBUNGEN.read_text(encoding="utf-8")
        lohn = LOHN.read_text(encoding="utf-8")

        # Das Stufenwoerterbuch samt seiner Form (ein `set`) ist unveraendert.
        assert (
            'APPLICATION_STAGES = {"EINGANG", "VORAUSWAHL", "ERSTGESPRAECH", '
            '"ENDGESPRAECH", "ANGEBOT", "EINGESTELLT", "ABGELEHNT"}'
        ) in bewerbung
        # Der Vorbehalt der Lohnrechnung ist woertlich derselbe.
        assert "Produktiv massgeblich sind amtlicher BMF-PAP" in lohn
        # Die Beitragsgrundlagen stehen unveraendert im Weg.
        assert '"bbg_kv_monat": 5812.50' in lohn

    def test_der_fremde_loeschweg_ist_mitgewandert(self):
        """`delete_application` stammt von einem anderen Agenten (f7fcbdd7c)."""
        bewerbung = BEWERBUNGEN.read_text(encoding="utf-8")
        assert "async def delete_application(" in bewerbung
        assert "DELETE FROM domain_hr.applications WHERE id = :id AND tenant_id" in bewerbung

    def test_personal_kennt_die_beiden_faecher_nicht_mehr(self):
        quelle = PERSONAL.read_text(encoding="utf-8")
        for name in (
            "def list_applications",
            "def create_application",
            "def update_application_stage",
            "def delete_application",
            "def berechne_lohn",
            "def preview_payroll_closeout",
        ):
            assert name not in quelle, name

    def test_personal_out_steht_nur_noch_an_einer_stelle(self):
        """Lag in `endpoints/personal.py` und war von den neuen Modulen unerreichbar."""
        definitionen = []
        for pfad in (PERSONAL, BEWERBUNGEN, LOHN):
            if "class PersonalOut(" in pfad.read_text(encoding="utf-8"):
                definitionen.append(pfad)
        assert definitionen == [], definitionen
        schemata = Path("app/api/v1/schemas/personal_schemas.py").read_text(encoding="utf-8")
        assert schemata.count("class PersonalOut(") == 1


class TestBenannteMaengel:
    """Was der Umzug **nicht** behoben hat — damit es nicht als behoben gilt.

    Ein Vertrag, der einen Mangel festhält, ist besser als eine Notiz: Er fällt
    auf, wenn jemand ihn behebt, und verlangt dann, dass die Zusage hier mitgeht.
    """

    def test_der_fehlerweg_verwischt_noch_jeden_fehler(self):
        bewerbung = BEWERBUNGEN.read_text(encoding="utf-8")
        assert 'detail="applications table not available"' in bewerbung, (
            "Behoben? Dann gehoert der Mangel aus der QA-Doku gestrichen."
        )

    def test_die_bewerbungsliste_ist_noch_unbegrenzt(self):
        baum = ast.parse(BEWERBUNGEN.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.AsyncFunctionDef) and knoten.name == "list_applications":
                namen = {
                    a.arg for a in knoten.args.args + knoten.args.kwonlyargs
                }
                assert "limit" not in namen, (
                    "Begrenzt? Dann gehoert der Mangel aus der QA-Doku gestrichen."
                )
                return
        pytest.fail("list_applications nicht gefunden")
