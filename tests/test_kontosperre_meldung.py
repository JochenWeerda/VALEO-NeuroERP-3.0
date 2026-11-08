"""Kontosperre: An jedem Buchungsweg ein Satz statt eines Datenbankfehlers.

Die Sperre setzt die Datenbank durch (Trigger an ``journal_entry_lines``). Bis zum 12.10.2026 las sie
sich nur an der manuellen Buchung als Satz. Vorlagen, CSV-Einspielung und OP-Ausgleich antworteten mit
500 und dem rohen Fehlertext; Bestandskorrektur und Inventur verschluckten den Fehler und meldeten
Erfolg, obwohl die abgebrochene Transaktion auch die Bestandsaenderung verwarf.

Geprueft gegen die echte Datenbank und den echten Trigger.
"""

from __future__ import annotations

import ast
import uuid
from pathlib import Path

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.endpoints import inventory_operations
from app.core.database import SessionLocal, get_db
from app.core.exceptions import kontosperre_meldung, register_domain_exception_handlers
from testgrenze import ersetze_mandant, ersetze_nutzer

REPO = Path(__file__).resolve().parent.parent
ZEILE = (
    "INSERT INTO domain_erp.journal_entry_lines (id, journal_entry_id, account_id, line_number) "
    "VALUES (:id, :je, :konto, 1)"
)


@pytest.fixture
def lage():
    """Ein Mandant mit gesperrtem Warenbestandskonto 1500 und einem Buchungskopf."""
    lauf = uuid.uuid4().hex[:6]
    mandant = f"ks-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, account_number, account_name, account_type, category, tenant_id, is_active, posting_blocked) "
            "VALUES (:id, '1500', 'Warenbestand', 'asset', 'inventory', :t, true, true)"),
            {"id": f"ks-{lauf}-1500", "t": mandant})
        db.execute(text(
            "INSERT INTO domain_erp.journal_entries (id, tenant_id, entry_number, entry_date, posting_date) "
            "VALUES (:id, :t, :nr, DATE '2026-10-01', DATE '2026-10-01')"),
            {"id": f"ks-{lauf}-je", "t": mandant, "nr": f"KS-{lauf}"})
        db.execute(text(
            "INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id) "
            "VALUES (:id, :nr, 'Testware', :t)"), {"id": f"ks-{lauf}-art", "nr": f"KS-{lauf}", "t": mandant})
        db.execute(text(
            "INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id) "
            "VALUES (:id, :nr, 'Testlager', :t)"), {"id": f"ks-{lauf}-lag", "nr": f"KS-{lauf}", "t": mandant})
        db.commit()
    try:
        yield {"lauf": lauf, "mandant": mandant, "konto": f"ks-{lauf}-1500", "kopf": f"ks-{lauf}-je"}
    finally:
        with SessionLocal() as db:
            for sql in (
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _fehler(konto: str, kopf: str) -> IntegrityError:
    with SessionLocal() as db, pytest.raises(IntegrityError) as fehler:
        db.execute(text(ZEILE), {"id": f"ks-{uuid.uuid4().hex[:8]}", "je": kopf, "konto": konto})
    return fehler.value


def test_sperre_wird_an_der_kennung_erkannt(lage):
    assert kontosperre_meldung(_fehler(lage["konto"], lage["kopf"])) == "Konto 1500 ist fuer Buchungen gesperrt."


def test_anderer_integritaetsfehler_ist_keine_sperre(lage):
    """Ein Konto, das es nicht gibt, scheitert am Fremdschluessel — das ist keine Sperre."""
    assert kontosperre_meldung(_fehler("ks-gibt-es-nicht", lage["kopf"])) is None
    assert kontosperre_meldung(ValueError("Konto 1500 ist fuer Buchungen gesperrt")) is None


@pytest.fixture
def anwendung(lage):
    app = FastAPI()
    register_domain_exception_handlers(app)

    @app.post("/bucht/{konto}")
    def bucht(konto: str, db: Session = Depends(get_db)):  # noqa: B008
        db.execute(text(ZEILE), {"id": f"ks-{uuid.uuid4().hex[:8]}", "je": lage["kopf"], "konto": konto})
        db.commit()
        return {"ok": True}

    app.include_router(inventory_operations.router, prefix="/lager")
    ersetze_mandant(app, lage["mandant"])
    ersetze_nutzer(app, "admin")
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


def test_weg_ohne_eigene_fehlerbehandlung_antwortet_409(lage, anwendung):
    antwort = anwendung.post(f"/bucht/{lage['konto']}")
    assert antwort.status_code == 409, antwort.text
    assert antwort.json()["error"] == "KONTO_GESPERRT"
    assert antwort.json()["detail"] == "Konto 1500 ist fuer Buchungen gesperrt."


def test_anderer_integritaetsfehler_bleibt_ein_serverfehler(anwendung):
    assert anwendung.post("/bucht/ks-gibt-es-nicht").status_code == 500


def _korrektur_weg() -> str:
    return next(
        r.path for r in inventory_operations.router.routes
        if getattr(r, "name", "") == "create_bestandskorrektur")


def test_bestandskorrektur_meldet_die_sperre_statt_erfolg(lage, anwendung):
    """Vorher: 200/201 mit Korrekturnummer, aber weder Bewegung noch Buchung in der Datenbank."""
    antwort = anwendung.post("/lager" + _korrektur_weg(), json={
        "article_id": f"ks-{lage['lauf']}-art", "warehouse_id": f"ks-{lage['lauf']}-lag",
        "menge": 2.5, "grund": "messdifferenz"})
    assert antwort.status_code == 409, antwort.text
    assert "1500 ist fuer Buchungen gesperrt" in str(antwort.json()["detail"])
    with SessionLocal() as db:
        bewegungen = db.execute(text(
            "SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t"),
            {"t": lage["mandant"]}).scalar()
    assert bewegungen == 0


def test_bestandskorrektur_wird_gespeichert_wenn_das_konto_offen_ist(lage, anwendung):
    """Bis 12.10.2026 meldete der Weg „gebucht“ und speicherte nichts: Eine verschluckte Vorabfrage
    auf eine Spalte, die es nicht gibt, hatte die Transaktion schon abgebrochen."""
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_erp.chart_of_accounts SET posting_blocked = false WHERE id = :k"),
                   {"k": lage["konto"]})
        db.commit()
    antwort = anwendung.post("/lager" + _korrektur_weg(), json={
        "article_id": f"ks-{lage['lauf']}-art", "warehouse_id": f"ks-{lage['lauf']}-lag",
        "menge": 2.5, "grund": "messdifferenz"})
    assert antwort.status_code == 201, antwort.text
    assert antwort.json()["journal_entry_id"]
    with SessionLocal() as db:
        bewegungen = db.execute(text(
            "SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE id = :id"),
            {"id": antwort.json()["movement_id"]}).scalar()
        zeilen = db.execute(text(
            "SELECT count(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id = :je"),
            {"je": antwort.json()["journal_entry_id"]}).scalar()
    assert (bewegungen, zeilen) == (1, 2)


def test_kontenzuordnung_der_warengruppe_wird_gefunden(lage):
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_inventory.articles SET warengruppe = 'Getreide' WHERE id = :id"),
                   {"id": f"ks-{lage['lauf']}-art"})
        db.execute(text(
            "INSERT INTO domain_einkauf.lager_kontenzuordnung "
            "(id, tenant_id, artikelgruppe, bestandskonto, aktiv) "
            "VALUES (gen_random_uuid(), :t, 'Getreide', '1510', true)"), {"t": lage["mandant"]})
        try:
            konten = inventory_operations._get_account_mapping(db, lage["mandant"], f"ks-{lage['lauf']}-art")
        finally:
            db.rollback()
    assert konten["bestandskonto"] == "1510"


# --- Ratsche: Kein Buchungsweg faengt die Sperre breit ab, ohne sie zu erkennen --------------

AUSNAHMEN: set[str] = set()


def _breit(handler: ast.ExceptHandler) -> bool:
    return handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id in {"Exception", "BaseException"})


def _stumme_stellen() -> list[str]:
    stellen = []
    for datei in sorted((REPO / "app").rglob("*.py")):
        rel = datei.relative_to(REPO).as_posix()
        quelle = datei.read_text(encoding="utf-8")
        if "journal_entry_lines" not in quelle or rel in AUSNAHMEN:
            continue
        baum = ast.parse(quelle)
        einfuegungen = [
            k.lineno for k in ast.walk(baum)
            if isinstance(k, ast.Constant) and isinstance(k.value, str)
            and "INSERT INTO" in k.value and "journal_entry_lines" in k.value
        ]
        for versuch in (k for k in ast.walk(baum) if isinstance(k, ast.Try)):
            von, bis = versuch.body[0].lineno, versuch.body[-1].end_lineno
            if not any(von <= z <= bis for z in einfuegungen):
                continue
            for handler in versuch.handlers:
                wirft_weiter = isinstance(handler.body[-1], ast.Raise) and handler.body[-1].exc is None
                if _breit(handler) and not wirft_weiter and "kontosperre_meldung" not in ast.unparse(handler):
                    stellen.append(f"{rel}:{handler.lineno}")
    return stellen


def test_kein_buchungsweg_faengt_die_sperre_stumm_ab():
    assert _stumme_stellen() == []
