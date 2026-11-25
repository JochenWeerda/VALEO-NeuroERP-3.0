"""Aufbewahrungspflichten nach geltendem Recht (Nutzerauftrag 25.11.2026) - Ratsche gegen die Rechtstabelle.

Aendert sich eine Frist, muss sich dieser Test mit Rechtsgrundlage aendern - nicht umgekehrt.
"""
from __future__ import annotations

import asyncio
import importlib.util
import uuid
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.core.gobd_retention import (
    RICHTLINIE_ZU_DOKUMENTTYP,
    RetentionPruefung,
    build_default_retention_regeln,
    regel_fuer,
)

pytestmark = pytest.mark.unit

#: Dokumenttyp -> Mindestfrist in Jahren (0 = bis Erhalt/Versand der Rechnung)
RECHT = {
    "journal_entry": 10, "jahresabschluss": 10, "inventar": 10, "audit_evidence": 10,      # § 147 Abs. 1 Nr. 1 AO
    "ap_invoice": 8, "ar_invoice": 8, "payment_run": 8, "agrar_settlement": 8,             # BEG IV
    "lohnabrechnung": 8, "lieferschein_beleg": 8,
    "kontrakt": 6, "handelsbrief": 6, "reklamation": 6,                                    # Handels-/Geschaeftsbriefe
    "lieferschein": 0,                                                                     # § 147 Abs. 3 S. 3/4 AO
    "psm_protokoll": 3,                                                                    # § 11 PflSchG
    "duenge_bilanz": 7,                                                                    # § 10 Abs. 5 DueV
    "silo_reinigungsprotokoll": 6,                                                         # betrieblich
}


def test_katalog_entspricht_der_rechtstabelle():
    katalog = {r.dokumenttyp: r.aufbewahrungsjahre for r in build_default_retention_regeln()}
    assert katalog == RECHT
    assert all(r.rechtsgrundlage for r in build_default_retention_regeln())


@pytest.mark.parametrize(("typ", "ereignis", "ende"), [
    ("ap_invoice", date(2025, 3, 15), date(2033, 12, 31)),     # 8 Jahre ab Schluss 2025
    ("journal_entry", date(2025, 3, 15), date(2035, 12, 31)),
    ("kontrakt", date(2026, 7, 31), date(2032, 12, 31)),       # ab Schluss des Jahres des Vertragsendes
    ("duenge_bilanz", date(2026, 12, 31), date(2033, 12, 31)),
    ("lieferschein", date(2026, 4, 2), date(2026, 4, 2)),      # Rechnungsdatum
])
def test_fristende_ab_schluss_des_kalenderjahres(typ, ereignis, ende):
    assert regel_fuer(typ).fristende(ereignis) == ende


def test_alte_belege_unter_der_uebergangsregel_sind_frei():
    """Beleg aus 2016: 8 Jahre enden 31.12.2024 - seit 01.01.2025 loeschbar (Art. 97 § 19a EGAO)."""
    pruefung = RetentionPruefung(pruefung_id=str(uuid.uuid4()), dokumenttyp="ap_invoice",
                                 dokumentdatum=date(2016, 6, 1), ereignisdatum=date(2016, 6, 1), aufbewahrungsjahre=8)
    assert pruefung.darf_geloescht_werden(date(2025, 1, 1)) is True


def test_ablaufhemmung_und_loeschsperre_verhindern_die_loeschung():
    pruefung = RetentionPruefung(pruefung_id=str(uuid.uuid4()), dokumenttyp="ap_invoice",
                                 dokumentdatum=date(2016, 6, 1), ereignisdatum=date(2016, 6, 1), aufbewahrungsjahre=8)
    heute = date(2026, 11, 25)
    assert pruefung.darf_geloescht_werden(heute, festsetzungsfrist_offen_bis=date(2027, 12, 31)) is False
    assert pruefung.darf_geloescht_werden(heute, loeschsperre_aktiv=True) is False
    assert pruefung.darf_geloescht_werden(heute) is True


def test_migration_setzt_die_standardrichtlinien_aus_dem_katalog():
    pfad = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "aufbewahrung_geltendes_recht_20261125.py"
    spec = importlib.util.spec_from_file_location("aufbewahrung_migration", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    zeilen = list(modul.NEU) + [modul.LIEFERSCHEIN[:5]]

    for _pid, typ, jahre, trigger, _grundlage in zeilen:
        assert jahre == regel_fuer(RICHTLINIE_ZU_DOKUMENTTYP[typ]).aufbewahrungsjahre, typ
        assert trigger in {"CALENDAR_YEAR_END", "CONTRACT_END", "INVOICE_DATE"}, typ


def test_governance_und_personalakte_folgen_dem_katalog():
    from app.core.tenant_governance import build_default_governance
    from app.services.personal_service import PersonalService

    policy = build_default_governance("t")
    assert policy.get_rule("ap_invoice").retention_years == 8
    assert policy.get_rule("harvest_acceptance").retention_years == 8
    klassen = PersonalService._DOCUMENT_CLASSES
    assert klassen["payroll_document"]["retention_years"] == regel_fuer("lohnabrechnung").aufbewahrungsjahre
    assert klassen["employment_contract"]["retention_years"] == 6


@pytest.mark.parametrize(("typ", "datum", "jahre", "frist"), [
    ("EINGANGSRECHNUNG", date(2025, 3, 15), 8, "2033-12-31"),
    ("VERTRAG", date(2026, 7, 31), 6, "2032-12-31"),
    ("LIEFERSCHEIN", date(2026, 4, 2), 0, "2026-04-02"),
])
def test_router_rechnet_ohne_tabellenzeile_nach_katalog(typ, datum, jahre, frist):
    from app.finance.router import calculate_retention_date

    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.scalars.return_value.all.return_value = []

    ergebnis = asyncio.run(calculate_retention_date(typ, datum, tenant_id="t", current_user=None, db=db))

    assert (ergebnis["aufbewahrungs_jahre"], ergebnis["frist_datum"]) == (jahre, frist)
