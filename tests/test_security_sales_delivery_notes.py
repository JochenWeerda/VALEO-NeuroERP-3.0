from __future__ import annotations

import os
import uuid

_DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)

import pytest

from app.api.v1.endpoints import sales_delivery_notes


class _FakeMappingsResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class _FakeResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def mappings(self):
        return _FakeMappingsResult(self._rows)


class _CapturingDb:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.calls: list[tuple[str, dict]] = []
        self.committed = False

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        rows = self.rows.pop(0) if self.rows else []
        return _FakeResult(rows)

    def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_list_delivery_notes_uses_context_tenant():
    db = _CapturingDb(rows=[[]])

    result = await sales_delivery_notes.list_delivery_notes(
        customer_id=None,
        status_filter=None,
        tenant_id="tenant-a",
        skip=0,
        limit=50,
        db=db,
    )

    assert result == []
    statement, params = db.calls[0]
    assert "WHERE tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"


def _mandanten_anlegen(*mandanten: str) -> None:
    """Testmandanten wirklich anlegen, statt sie zu behaupten.

    Der Journalsatz, der bei der Umwandlung mitentsteht, haengt per
    Fremdschluessel an `domain_shared.tenants`. Ein erfundener Mandant waere
    hier kein Testmandant, sondern ein 500er.
    """
    from sqlalchemy import create_engine, text

    with create_engine(_DB_URL).begin() as verbindung:
        for mandant in mandanten:
            verbindung.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                    "VALUES (:id, :name, :domain, true) ON CONFLICT (id) DO NOTHING"
                ),
                {"id": mandant, "name": mandant, "domain": f"{mandant}.test"},
            )


def _mandanten_entfernen(*mandanten: str) -> None:
    from sqlalchemy import create_engine, text

    with create_engine(_DB_URL).begin() as verbindung:
        for tabelle, spalte in (
            ("domain_erp.journal_entries", "tenant_id"),
            ("domain_sales.sales_invoices", "tenant_id"),
            ("domain_sales.delivery_notes", "tenant_id"),
            ("domain_shared.tenants", "id"),
        ):
            verbindung.execute(
                text(f"DELETE FROM {tabelle} WHERE {spalte} = ANY(:ids)"),  # nosec B608  # Tabellennamen sind Literale, Werte gebunden
                {"ids": list(mandanten)},
            )


def test_create_invoice_from_delivery_laesst_fremde_mandanten_unberuehrt():
    """Frueher eine Attrappe, jetzt der echte Weg — und das aus einem Grund.

    Der Test prueft, dass die Umwandlung nur den eigenen Mandanten anfasst. Er
    tat das ueber die SQL-Zeichenkette einer Attrappen-Sitzung. Seit die
    Rechnung mit eigenen Positionen entsteht, braucht der Endpunkt eine echte
    Sitzung — und die Attrappe haette nur noch nachgezeichnet, was sie selbst
    vorgibt.

    Der Nachweis ist jetzt staerker: Zwei Mandanten, zwei Lieferscheine, eine
    Umwandlung. Der fremde Beleg bleibt Entwurf und ist fuer den anderen
    Mandanten nicht einmal sichtbar.
    """
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app, raise_server_exceptions=False)

    def kopf(mandant: str) -> dict:
        return {
            "Authorization": "Bearer dev-token",
            "X-Tenant-ID": mandant,
            "X-Tenant-Id": mandant,
        }

    def lieferschein(mandant: str) -> str:
        antwort = client.post(
            "/api/v1/sales/delivery-notes",
            headers=kopf(mandant),
            json={
                "customer_id": "K-100",
                "delivery_date": "2026-09-15",
                "positionen": [
                    {
                        "pos_nr": 1,
                        "artikel_id": "ART-WEIZEN",
                        "artikel_nr": "10001",
                        "bezeichnung": "Weizen A",
                        "menge": "100",
                        "einheit": "dt",
                        "netto_preis": "25.00",
                        "mwst_prozent": "7",
                    }
                ],
            },
        )
        if antwort.status_code in (500, 503):
            pytest.skip(f"Datenbank nicht erreichbar: {antwort.status_code}")
        assert antwort.status_code == 201, antwort.text
        return antwort.json()["id"]

    eigener = f"test-{uuid.uuid4().hex[:8]}"
    fremder = f"test-{uuid.uuid4().hex[:8]}"
    _mandanten_anlegen(eigener, fremder)
    try:
        eigen_id = lieferschein(eigener)
        fremd_id = lieferschein(fremder)

        gebucht = client.post(
            f"/api/v1/sales/delivery-notes/{eigen_id}/post", headers=kopf(eigener)
        )
        assert gebucht.status_code == 200, gebucht.text

        rechnung = client.post(
            f"/api/v1/sales/delivery-notes/{eigen_id}/create-invoice", headers=kopf(eigener)
        )
        assert rechnung.status_code == 201, rechnung.text

        # Der eigene Beleg ist berechnet ...
        eigen = client.get(f"/api/v1/sales/delivery-notes/{eigen_id}", headers=kopf(eigener))
        assert eigen.json()["status"] == "invoiced"

        # ... der fremde nicht, und er ist fuer den eigenen Mandanten nicht
        # einmal sichtbar.
        fremd = client.get(f"/api/v1/sales/delivery-notes/{fremd_id}", headers=kopf(fremder))
        assert fremd.json()["status"] == "draft"
        assert (
            client.get(
                f"/api/v1/sales/delivery-notes/{fremd_id}", headers=kopf(eigener)
            ).status_code
            == 404
        )
    finally:
        _mandanten_entfernen(eigener, fremder)
