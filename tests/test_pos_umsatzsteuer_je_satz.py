"""Kassen-Tagesabschluss bucht Erloes netto und Umsatzsteuer je Satz (M3, POS-Umsatzsteuer, 19.11.2026).

Bis dahin ging der ganze Kassenumsatz brutto auf 8400 - ohne Umsatzsteuer. Jetzt:
1. Jeder Kassiervorgang speichert sein Brutto je Umsatzsteuersatz (``vat_breakdown``, wie die TSE es meldet).
2. Die Tagessumme liefert Brutto je Satz; deckt sie den Tagesumsatz nicht (Altvorgaenge), wird nicht gebucht.
3. Je Satz genau ein Verkaufs-Steuerschluessel aus ``domain_erp.tax_keys``; Konten nur von dort, nie angenommen.
4. Netto = Brutto * 100 / (100 + Satz), Steuer = Rest - die Summe je Satz bleibt bitgleich das Brutto.
"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.core.exceptions import DomainError
from app.finance.steuerschluessel import Steuerklaerung
from app.services import pos_accounting_service as pas
from app.services.pos_accounting_service import (
    PosAccountingLine,
    PosClosingAmounts,
    PosVerkaufsschluessel,
    build_pos_closing_lines,
    mit_umsatzsteuer,
    pos_buchungszeilen_mit_ust,
)

D = Decimal
SCHLUESSEL = {
    D("19"): PosVerkaufsschluessel("3", D("19"), "8400", "1776"),
    D("7"): PosVerkaufsschluessel("2", D("7"), "8300", "1771"),
    D("0"): PosVerkaufsschluessel("1", D("0"), "8120", None),
}


def _zeilen(brutto: str) -> list[PosAccountingLine]:
    return build_pos_closing_lines(PosClosingAmounts(cash_sales=D(brutto), card_sales=D("0")))


def _summe(lines, feld):
    return sum((getattr(line, feld) for line in lines), D("0"))


# --- Rechenkern -------------------------------------------------------------------------------------------------

def test_brutto_wird_je_satz_in_erloes_netto_und_umsatzsteuer_geteilt():
    lines = mit_umsatzsteuer(_zeilen("226.00"), {D("19"): D("119.00"), D("7"): D("107.00")}, SCHLUESSEL)

    haben = {(l.account_number, l.credit) for l in lines if l.credit > 0}
    assert haben == {("8400", D("100.00")), ("1776", D("19.00")), ("8300", D("100.00")), ("1771", D("7.00"))}
    assert _summe(lines, "debit") == _summe(lines, "credit") == D("226.00")


def test_rundung_laesst_das_brutto_je_satz_bitgleich():
    lines = mit_umsatzsteuer(_zeilen("10.00"), {D("19"): D("10.00")}, SCHLUESSEL)

    netto = next(l.credit for l in lines if l.account_number == "8400")
    steuer = next(l.credit for l in lines if l.account_number == "1776")
    assert (netto, steuer) == (D("8.40"), D("1.60"))
    assert netto + steuer == D("10.00")


def test_steuerfreier_satz_bucht_keine_steuerzeile():
    lines = mit_umsatzsteuer(_zeilen("50.00"), {D("0"): D("50.00")}, SCHLUESSEL)

    assert {(l.account_number, l.credit) for l in lines if l.credit > 0} == {("8120", D("50.00"))}


def test_satz_ohne_umsatz_bleibt_ohne_zeile():
    lines = mit_umsatzsteuer(_zeilen("119.00"), {D("19"): D("119.00"), D("7"): D("0.00")}, SCHLUESSEL)

    assert not any(l.account_number in {"8300", "1771"} for l in lines)


def test_brutto_je_satz_muss_den_kassenumsatz_decken():
    with pytest.raises(ValueError, match="deckt den Kassenumsatz"):
        mit_umsatzsteuer(_zeilen("226.00"), {D("19"): D("119.00")}, SCHLUESSEL)


def test_steuerpflichtiger_satz_ohne_steuerkonto_bucht_nicht():
    ohne_konto = {D("19"): PosVerkaufsschluessel("3", D("19"), "8400", None)}
    with pytest.raises(ValueError, match="kein Umsatzsteuerkonto"):
        mit_umsatzsteuer(_zeilen("119.00"), {D("19"): D("119.00")}, ohne_konto)


def test_ohne_erloeszeile_bleibt_die_buchung_unveraendert():
    nur_entnahme = build_pos_closing_lines(PosClosingAmounts(cash_withdrawals=D("80.00")))

    assert mit_umsatzsteuer(nur_entnahme, {}, SCHLUESSEL) == nur_entnahme


# --- Vorpruefung vor der TSE-Signatur ---------------------------------------------------------------------------

class _Buchung:
    def __init__(self, periode_fehler: Exception | None = None):
        self.periode_fehler = periode_fehler
        self.perioden: list[str] = []

    def check_period_open(self, periode: str) -> None:
        self.perioden.append(periode)
        if self.periode_fehler:
            raise self.periode_fehler

    def account_id_for_number(self, nummer: str) -> str:
        return f"konto-{nummer}"


def _summary(brutto_je_satz: dict, gesamt: str) -> dict:
    return {"gross_total": D(gesamt), "gross_by_rate": brutto_je_satz,
            "gross_by_rate_total": sum(brutto_je_satz.values(), D("0"))}


def _schluessel_aus_tax_keys(monkeypatch, ergebnis=None, fehler=None):
    import app.finance.steuerschluessel as sk

    def wahl(_db, _tenant, saetze):
        if fehler:
            raise fehler
        return {satz: ergebnis[satz] for satz in saetze}

    monkeypatch.setattr(sk, "kassen_verkaufsschluessel", wahl)


def test_vorpruefung_liefert_zeilen_mit_steuer_und_alle_konten(monkeypatch):
    _schluessel_aus_tax_keys(monkeypatch, {D("19"): ("3", "8400", "1776")})
    buchung = _Buchung()

    lines, konten = pos_buchungszeilen_mit_ust(None, "t", buchung, _zeilen("119.00"),
                                               _summary({D("19"): D("119.00")}, "119.00"), date(2026, 11, 19))

    assert buchung.perioden == ["2026-11"]
    assert {(l.account_number, l.credit) for l in lines if l.credit > 0} == {("8400", D("100.00")),
                                                                             ("1776", D("19.00"))}
    assert konten == {"1000": "konto-1000", "8400": "konto-8400", "1776": "konto-1776"}


def test_altvorgaenge_ohne_saetze_sperren_den_abschluss(monkeypatch):
    _schluessel_aus_tax_keys(monkeypatch, {})
    with pytest.raises(ValueError, match="ohne Steuersaetze"):
        pos_buchungszeilen_mit_ust(None, "t", _Buchung(), _zeilen("119.00"), _summary({}, "119.00"),
                                   date(2026, 11, 19))


def test_fehlender_steuerschluessel_wird_zum_buchungshindernis(monkeypatch):
    _schluessel_aus_tax_keys(monkeypatch, fehler=Steuerklaerung("kein passender Verkaufs-Steuerschlüssel"))
    with pytest.raises(ValueError, match="kein passender"):
        pos_buchungszeilen_mit_ust(None, "t", _Buchung(), _zeilen("119.00"),
                                   _summary({D("19"): D("119.00")}, "119.00"), date(2026, 11, 19))


def test_gesperrte_periode_wird_zum_buchungshindernis(monkeypatch):
    _schluessel_aus_tax_keys(monkeypatch, {D("19"): ("3", "8400", "1776")})
    with pytest.raises(ValueError, match="gesperrt"):
        pos_buchungszeilen_mit_ust(None, "t", _Buchung(DomainError("Periode 2026-11 gesperrt")), _zeilen("119.00"),
                                   _summary({D("19"): D("119.00")}, "119.00"), date(2026, 11, 19))


def test_tag_ohne_umsatz_braucht_keinen_steuerschluessel(monkeypatch):
    _schluessel_aus_tax_keys(monkeypatch, fehler=AssertionError("darf nicht gefragt werden"))
    nur_entnahme = build_pos_closing_lines(PosClosingAmounts(cash_withdrawals=D("80.00")))

    lines, konten = pos_buchungszeilen_mit_ust(None, "t", _Buchung(), nur_entnahme, _summary({}, "0"),
                                               date(2026, 11, 19))

    assert lines == nur_entnahme
    assert set(konten) == {"1000", "1800"}


def test_vorpruefung_liegt_vor_der_tse_signatur():
    """Ist der TSE-Abschluss signiert, darf die Buchung nicht mehr scheitern: Steuerpruefung vor close_cash_point."""
    from pathlib import Path

    quelle = Path("app/api/v1/endpoints/compat.py").read_text(encoding="utf-8")
    abschluss = quelle[quelle.index("async def create_tagesabschluss"):]
    assert abschluss.index("pos_buchungszeilen_mit_ust(") < abschluss.index("fiscal.close_cash_point(")
    assert pas.pos_buchungszeilen_mit_ust is pos_buchungszeilen_mit_ust


# --- Gegen die Datenbank ----------------------------------------------------------------------------------------

@pytest.fixture
def mandant():
    from sqlalchemy import text

    from app.core.database import SessionLocal
    from app.finance.steuerschluessel import richte_skr03_ein

    kennung = f"ust-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        richte_skr03_ein(db, kennung)  # Schluessel 2 (7 %) und 3 (19 %) mit Erloes- und Steuerkonto
        db.commit()
    try:
        yield kennung
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_docflow.pos_fiscal_transactions WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": kennung})
            db.commit()


@pytest.mark.integration
def test_kassenschluessel_kommen_aus_den_steuerschluesseln_des_mandanten(mandant):
    from app.core.database import SessionLocal
    from app.finance.steuerschluessel import kassen_verkaufsschluessel

    with SessionLocal() as db:
        wahl = kassen_verkaufsschluessel(db, mandant, [D("19"), D("7"), D("19")])

    assert set(wahl) == {D("7"), D("19")}
    for code, erloes, steuer in wahl.values():
        assert code and erloes and steuer


@pytest.mark.integration
def test_satz_ohne_schluessel_wird_nicht_angenommen(mandant):
    from app.core.database import SessionLocal
    from app.finance.steuerschluessel import kassen_verkaufsschluessel

    with SessionLocal() as db, pytest.raises(Steuerklaerung, match="16 % gibt es kein"):
        kassen_verkaufsschluessel(db, mandant, [D("16")])


@pytest.mark.integration
def test_zwei_schluessel_fuer_einen_satz_sind_mehrdeutig(mandant):
    from sqlalchemy import text

    from app.core.database import SessionLocal
    from app.finance.steuerschluessel import kassen_verkaufsschluessel

    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, gueltig_von, "
            " credit_account, revenue_account) "
            "VALUES (:id, :t, '93', 'Zweiter 19er', 19, DATE '2021-01-01', '1776', '8400')"),
            {"id": f"{mandant}-sk93", "t": mandant})
        db.commit()
        with pytest.raises(Steuerklaerung, match=r"2 \("):
            kassen_verkaufsschluessel(db, mandant, [D("19")])


@pytest.mark.integration
def test_tagessumme_liefert_brutto_je_satz(mandant):
    from sqlalchemy import text

    from app.core.database import SessionLocal
    from app.services.fiscalization.service import FiscalizationService

    tag = date(2026, 11, 19)
    with SessionLocal() as db:
        for nr, brutto, saetze in ((1, "226.00", {"19": "119.00", "7": "107.00"}), (2, "11.90", {"19": "11.90"})):
            db.execute(text(
                "INSERT INTO domain_docflow.pos_fiscal_transactions (id, tenant_id, transaction_id, provider, "
                " terminal_id, cash_register_id, client_id, business_date, transaction_type, state, gross_total, "
                " payment_breakdown, vat_breakdown, started_at, provider_response) VALUES (:id, :t, :tx, 'test', "
                " 'K1', 'KASSE-1', 'C1', :tag, 'Beleg', 'FINISHED', :brutto, CAST(:zahl AS jsonb), "
                " CAST(:ust AS jsonb), :start, CAST('{}' AS jsonb))"),
                {"id": str(uuid.uuid4()), "t": mandant, "tx": f"tx-{nr}", "tag": tag, "brutto": brutto,
                 "zahl": json.dumps({"BAR": brutto}), "ust": json.dumps(saetze),
                 "start": datetime(2026, 11, 19, 9, nr, tzinfo=timezone.utc)})
        db.commit()
        summe = FiscalizationService(db, mandant).daily_summary(tag)

    assert summe["gross_by_rate"] == {D("19"): D("130.90"), D("7"): D("107.00")}
    assert summe["gross_by_rate_total"] == D(str(summe["gross_total"])) == D("237.90")
