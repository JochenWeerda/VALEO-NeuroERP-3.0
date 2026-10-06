from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints import personal


class _Result:
    def __init__(self, rows=None, row=None):
        self._rows = rows or []
        self._row = row

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._row


def test_org_subtree_uses_actual_root_parent():
    """Der Teilbaum beginnt an der angefragten Einheit, nicht an der Wurzel.

    Der Helfer heisst seit 06.10.2026 `baum_bauen` und liegt im Dienst
    `personal_organisation_service` — `personal.py` stand mit 3345 Zeilen in der
    Godfile-Ratsche.
    """
    from app.services import personal_organisation_service as orga

    rows = [
        {"id": "TEAM-1", "parent_id": "DEPT-1", "name": "Innendienst"},
        {"id": "TEAM-1-A", "parent_id": "TEAM-1", "name": "Auftrag"},
    ]

    tree = orga.baum_bauen(rows, rows[0]["parent_id"])

    assert tree[0]["id"] == "TEAM-1"
    assert tree[0]["children"][0]["id"] == "TEAM-1-A"


def test_zeitkonto_liest_die_kanonische_schichttabelle():
    """Vorher mockte dieser Test `domain_hr.schichten` in die Welt.

    Die Tabelle existiert nicht und hat nie existiert; die vorhandene heisst
    `domain_hr.shifts` und fuehrt keine der gelesenen Spalten (`planned_hours`,
    `employee_ref`). Ein Test, der eine fehlende Tabelle mockt, prueft die
    Abfrage gegen eine Welt, die es nicht gibt — und bestaetigte hier eine
    Saldoformel, die ausserdem die Korrektur zweimal zaehlte.

    Der fachliche Nachweis gegen eine echte Datenbank steht in
    ``tests/test_personal_organisation_zeitkonto_vertrag.py``.
    """
    from app.services import personal_organisation_service as orga

    assert orga.SCHICHTEN == "domain_hr.shifts"
    assert orga.SCHICHT_ABGESAGT in orga.SCHICHTSTAENDE


def test_saldo_zaehlt_jede_stunde_genau_einmal():
    """Der Saldo ist die Summe der ausgewiesenen Zahlen — nicht mehr und nicht weniger."""
    from unittest.mock import patch

    from app.services import personal_organisation_service as orga

    ist = [{"monat": "2025-12", "actual_hours": 10.0, "eintraege": 1},
           {"monat": "2026-05", "actual_hours": 16.0, "eintraege": 2}]
    plan = [{"monat": "2026-05", "planned_hours": 15.0}]
    korr = [{"monat": "2026-05", "adjustment_hours": 1.5}]

    with patch.object(orga, "ist_stunden", return_value=ist),          patch.object(orga, "plan_stunden", return_value=plan),          patch.object(orga, "korrekturen", return_value=korr):
        stand = orga.zeitkonto(db=None, tenant_id="t-1", employee_ref="EMP-1", jahr=2026)

    assert stand["uebertrag_vorperioden"] == pytest.approx(10.0)
    assert stand["saldo_laufende_periode"] == pytest.approx(2.5)
    assert stand["saldo_hours"] == pytest.approx(12.5)
    # Die Korrektur steckt in genau einer der beiden Zahlen.
    assert stand["saldo_hours"] == pytest.approx(
        stand["uebertrag_vorperioden"]
        + stand["saldo_laufende_periode"]
        + stand["saldo_folgeperioden"]
    )


def test_zyklus_im_organigramm_wird_nicht_verschwiegen():
    from fastapi import HTTPException

    from app.services import personal_organisation_service as orga

    with pytest.raises(HTTPException) as fehler:
        orga.zyklus_pruefen([{"id": "a", "parent_id": None, "depth": orga.MAX_TIEFE}])
    assert fehler.value.status_code == 409
