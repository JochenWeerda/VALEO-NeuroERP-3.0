"""Ein Mahnweg statt drei (M3, 23.11.2026) - gegen die echte Datenbank.

Vorher: ``/dunning/process|run`` rechnete mit eigener Stufenlogik, ``/finance/mahnlauf/run`` mit einer zweiten, und
"Mahnstufe eskalieren" (auch die Maskenaktion am offenen Posten) schrieb einen dritten, eigenen Verlauf ohne Mahnung.
Der Mahnlauf eskalierte bei jedem Lauf: zweimal am selben Tag = Stufe 2. Ohne Mahnregeln setzte er erfundene
Gebuehren an. ``PUT /dunning/{id}/paid`` zifferte den Posten ohne Zahlungsbuchung aus.
Jetzt: ``FinanceDunningService.run_dunning`` fuer alle Zugaenge.
"""
from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.exceptions import ConflictError
from app.services.finance_dunning_service import FinanceDunningService

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    mandant = f"mw-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": mandant})
        for stufe, gebuehr, frist, sperre in ((1, 5, 14, False), (2, 10, 10, False), (3, 20, 7, True)):
            db.execute(text(
                "INSERT INTO domain_erp.dunning_rules (id, tenant_id, level, days_overdue_min, fee_amount, "
                "fee_percentage, interest_rate, payment_deadline_days, block_customer, active) "
                "VALUES (:id, :t, :l, 1, :g, 0, 0, :f, :s, true)"),
                {"id": str(uuid.uuid4()), "t": mandant, "l": stufe, "g": gebuehr, "f": frist, "s": sperre})
        db.commit()
    try:
        yield mandant
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_erp.dunning_notices WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.dunning_rules WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _posten(mandant: str, ueberfaellig_tage: int, nummer: str | None = None) -> tuple[str, str]:
    kennung, nummer = str(uuid.uuid4()), nummer or f"RE-{uuid.uuid4().hex[:6]}"
    faellig = date.today() - timedelta(days=ueberfaellig_tage)
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr, datum, faelligkeit, betrag, offen, "
            "konto_typ, op_status, kunde_id) VALUES (:id, :t, :nr, :d, :d, 100, 100, 'debitoren', 'offen', 'K-1')"),
            {"id": kennung, "t": mandant, "nr": nummer, "d": faellig})
        db.commit()
    return kennung, nummer


def _stufe(posten: str) -> int:
    with SessionLocal() as db:
        return int(db.execute(text("SELECT COALESCE(dunning_level, 0) FROM domain_erp.offene_posten WHERE id = :p"),
                              {"p": posten}).scalar())


def _mahnungen(posten: str) -> int:
    with SessionLocal() as db:
        return int(db.execute(text("SELECT COUNT(*) FROM domain_erp.dunning_notices WHERE op_id = :p"),
                              {"p": posten}).scalar())


def test_zweiter_lauf_in_der_frist_mahnt_nicht_erneut(haus):
    posten, _ = _posten(haus, 20)
    with SessionLocal() as db:
        erster = FinanceDunningService(db, haus).run_dunning(bediener="test")
        zweiter = FinanceDunningService(db, haus).run_dunning(bediener="test")

    assert erster["erzeugt"] == 1 and erster["mahnungen"][0]["gebuehr"] == 5.0
    assert zweiter["erzeugt"] == 0
    assert (_stufe(posten), _mahnungen(posten)) == (1, 1)


def test_nach_ablauf_der_frist_folgt_die_naechste_stufe(haus):
    posten, _ = _posten(haus, 40)
    with SessionLocal() as db:
        FinanceDunningService(db, haus).run_dunning(bediener="test")
        spaeter = FinanceDunningService(db, haus).run_dunning(bediener="test",
                                                              stichtag=date.today() + timedelta(days=15))

    assert spaeter["erzeugt"] == 1 and spaeter["mahnungen"][0]["stufe"] == 3
    assert _mahnungen(posten) == 2


def test_hoechste_stufe_mahnt_nicht_endlos(haus):
    posten, _ = _posten(haus, 90)
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_erp.offene_posten SET dunning_level = 3 WHERE id = :p"), {"p": posten})
        db.commit()
        assert FinanceDunningService(db, haus).run_dunning(bediener="test")["erzeugt"] == 0
    assert _mahnungen(posten) == 0


def test_nicht_ueberfaellig_wird_nicht_gemahnt(haus):
    posten, _ = _posten(haus, 0)
    with SessionLocal() as db:
        assert FinanceDunningService(db, haus).run_dunning(bediener="test")["erzeugt"] == 0
    assert _mahnungen(posten) == 0


def test_ohne_mahnregeln_wird_nicht_gemahnt(haus):
    posten, _ = _posten(haus, 20)
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_erp.dunning_rules SET active = false WHERE tenant_id = :t"), {"t": haus})
        db.commit()
        with pytest.raises(ConflictError, match="Keine aktiven Mahnregeln"):
            FinanceDunningService(db, haus).run_dunning(bediener="test")
    assert _mahnungen(posten) == 0


def test_auswahl_nach_posten_mahnt_nur_diese(haus):
    gewaehlt, _ = _posten(haus, 20)
    andere, _ = _posten(haus, 20)
    with SessionLocal() as db:
        ergebnis = FinanceDunningService(db, haus).run_dunning(bediener="test", op_ids=[gewaehlt])

    assert ergebnis["erzeugt"] == 1
    assert (_mahnungen(gewaehlt), _mahnungen(andere)) == (1, 0)


def test_mahnstufe_eskalieren_erzeugt_eine_mahnung_und_der_verlauf_sind_die_mahnungen(haus):
    from app.services.finance_mahnstufe_service import MahnstufeError, eskaliere_mahnstufe, get_mahnstufen_trail

    posten, nummer = _posten(haus, 20)
    with SessionLocal() as db:
        stufe = eskaliere_mahnstufe(db, nummer, haus, "anna")
        with pytest.raises(MahnstufeError, match="Zahlungsfrist"):
            eskaliere_mahnstufe(db, nummer, haus, "anna")
        verlauf = get_mahnstufen_trail(db, nummer, haus)

    assert (stufe["stufe"], stufe["vorherige_stufe"], stufe["bearbeitungsgebuehr_eur"]) == ("1", None, 5.0)
    assert [eintrag["stufe"] for eintrag in verlauf] == ["1"]
    assert (_stufe(posten), _mahnungen(posten)) == (1, 1)
