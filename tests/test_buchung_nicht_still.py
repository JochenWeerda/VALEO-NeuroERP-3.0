"""Gutschrift, Inventur, Bestandskorrektur: kein „gebucht“ ohne Buchung.

Bis zum 12.10.2026:
- Die Gutschrift schrieb den Buchungskopf fest und danach Zeilen mit Kontonummern statt Konto-IDs;
  sie scheiterten am Fremdschluessel, der Fehler wurde verschluckt. Waeren die Zeilen durchgegangen,
  haette die OP-Minderung jeden offenen Posten des Kunden um den vollen Betrag gekuerzt.
- Inventur und Bestandskorrektur protokollierten einen Fehler der Hauptbuchbuchung und meldeten
  Erfolg, obwohl die abgebrochene Transaktion auch die Bestandsaenderung verwarf.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import inventory_counts, inventory_operations, sales_credit_notes
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from testgrenze import ersetze_mandant, ersetze_nutzer

AUFRAEUMEN = (
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
    "DELETE FROM domain_sales.sales_credit_notes WHERE tenant_id = :t",
    "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
    "DELETE FROM domain_inventory.inventory_count_lines WHERE tenant_id = :t",
    "DELETE FROM domain_inventory.inventory_counts WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
    "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
    "DELETE FROM domain_shared.users WHERE id = :nutzer",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"bs-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        db.execute(text(
            "INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id) "
            "VALUES (:id, :nr, 'Testware', :t)"), {"id": f"bs-{lauf}-art", "nr": f"BS-{lauf}", "t": mandant})
        db.execute(text(
            "INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id) "
            "VALUES (:id, :nr, 'Testlager', :t)"), {"id": f"bs-{lauf}-lag", "nr": f"BS-{lauf}", "t": mandant})
        db.commit()

    # Die Kundensperre ist hier nicht Gegenstand.
    monkeypatch.setattr(sales_credit_notes, "assert_customer_allowed_for_invoice", lambda *a, **k: None)
    monkeypatch.setattr(sales_credit_notes, "log_fibu_audit", lambda *a, **k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(sales_credit_notes.router)
    app.include_router(inventory_operations.router, prefix="/lager")
    app.include_router(inventory_counts.router, prefix="/inventur")
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"lauf": lauf, "mandant": mandant, "client": client}
    finally:
        with SessionLocal() as db:
            for sql in AUFRAEUMEN:
                db.execute(text(sql), {"t": mandant, "nutzer": f"bs-{lauf}-nutzer"} if ":nutzer" in sql else {"t": mandant})
            db.commit()


def _zahl(sql: str, **werte) -> int:
    with SessionLocal() as db:
        return db.execute(text(sql), werte).scalar()


# Die Gutschrift prueft ``tests/test_gutschrift_umsatzsteuer.py``.


# --- Bestandskorrektur und Inventur ------------------------------------------------------------

def _kaputte_buchung(*_a, **_k):
    raise RuntimeError("Hauptbuch nicht erreichbar")


def test_bestandskorrektur_meldet_buchungsfehler_als_fehler(haus, monkeypatch):
    monkeypatch.setattr(inventory_operations, "_post_inventory_journal", _kaputte_buchung)
    weg = next(r.path for r in inventory_operations.router.routes
               if getattr(r, "name", "") == "create_bestandskorrektur")
    antwort = haus["client"].post("/lager" + weg, json={
        "article_id": f"bs-{haus['lauf']}-art", "warehouse_id": f"bs-{haus['lauf']}-lag",
        "menge": 1.0, "grund": "messdifferenz"})
    assert antwort.status_code == 500, antwort.text
    assert "nicht gebucht" in antwort.json()["detail"]
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                 t=haus["mandant"]) == 0


@pytest.fixture
def inventur(haus):
    lauf, mandant = haus["lauf"], haus["mandant"]
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.users (id, keycloak_id, username, email) "
            "VALUES (:id, :id, :id, :mail)"), {"id": f"bs-{lauf}-nutzer", "mail": f"bs-{lauf}@example.invalid"})
        db.execute(text(
            "INSERT INTO domain_inventory.inventory_counts (id, warehouse_id, counted_by, tenant_id, status) "
            "VALUES (:id, :lag, :nutzer, :t, 'draft')"),
            {"id": f"bs-{lauf}-inv", "lag": f"bs-{lauf}-lag", "nutzer": f"bs-{lauf}-nutzer", "t": mandant})
        db.execute(text(
            "INSERT INTO domain_inventory.inventory_count_lines "
            "(id, inventory_count_id, article_id, expected_qty, counted_qty, warehouse_id, tenant_id) "
            "VALUES (:id, :inv, :art, 10, 12, :lag, :t)"),
            {"id": f"bs-{lauf}-zeile", "inv": f"bs-{lauf}-inv", "art": f"bs-{lauf}-art",
             "lag": f"bs-{lauf}-lag", "t": mandant})
        db.commit()
    return {**haus, "id": f"bs-{lauf}-inv"}


def test_inventur_wird_mit_buchung_verbucht(inventur):
    antwort = inventur["client"].post(f"/inventur/{inventur['id']}/post")
    assert antwort.status_code == 200, antwort.text
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                 t=inventur["mandant"]) == 1
    assert _zahl("SELECT count(*) FROM domain_erp.journal_entry_lines l JOIN domain_erp.journal_entries e "
                 "ON e.id = l.journal_entry_id WHERE e.tenant_id = :t", t=inventur["mandant"]) == 2
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_counts WHERE id = :id AND status = 'posted'",
                 id=inventur["id"]) == 1


def test_inventur_meldet_buchungsfehler_als_fehler(inventur, monkeypatch):
    monkeypatch.setattr(inventory_operations, "_post_inventory_journal", _kaputte_buchung)
    antwort = inventur["client"].post(f"/inventur/{inventur['id']}/post")
    assert antwort.status_code == 500, antwort.text
    assert "nicht verbucht" in antwort.json()["detail"]
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                 t=inventur["mandant"]) == 0
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_counts WHERE id = :id AND status = 'draft'",
                 id=inventur["id"]) == 1


# --- Inventur: Mandant aus der Anmeldung -------------------------------------------------------

def test_fremde_inventur_gibt_es_nicht(inventur):
    """Vorher: Mandant aus ``?tenant_id=``; lesen, loeschen und verbuchen filterten gar nicht."""
    from app.core.tenant import get_tenant_id

    client = inventur["client"]
    client.app.dependency_overrides[get_tenant_id] = lambda: "bs-anderes-haus"
    weg = f"/inventur/{inventur['id']}"
    assert client.get(weg).status_code == 404
    assert client.get(weg + "/lines").status_code == 404
    assert client.post(weg + "/post").status_code == 404
    assert client.delete(weg).status_code == 404
    zeile = f"/inventur/lines/bs-{inventur['lauf']}-zeile"
    assert client.patch(zeile, json={"counted_qty": 99}).status_code == 404
    assert client.delete(zeile).status_code == 404
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_count_lines WHERE id = :id AND counted_qty = 12",
                 id=f"bs-{inventur['lauf']}-zeile") == 1
    assert client.get("/inventur/", params={"tenant_id": inventur["mandant"]}).json()["total"] == 0
    assert _zahl("SELECT count(*) FROM domain_inventory.inventory_counts WHERE id = :id AND status = 'draft'",
                 id=inventur["id"]) == 1
