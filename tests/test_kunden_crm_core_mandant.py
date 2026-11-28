"""Kunden aus crm-core nur fuer den eigenen Mandanten (20.10.2026).

crm-core fuehrt an Kunden keinen Mandanten. Vorher reichten Liste, Abruf, Aendern und Loeschen Kunden *aller*
Mandanten durch; die Anlage nahm den Mandanten aus dem Body (Standard: Dev-Mandant). Diese Vertraege halten fest:

* ein crm-core-Kunde gilt nur ueber seinen Eintrag in ``domain_crm.customers`` als eigener — fremde fehlen in der
  Liste, ergeben beim Abruf "nicht gefunden" und werden weder geaendert noch geloescht;
* die Anlage traegt den lokalen Eintrag immer im Mandanten des Kontexts ein;
* ein abweichender Mandant im Body wird mit 403 abgewiesen.

crm-core wird simuliert; Datenbank ist der Pruefstand (``TEST_DATABASE_URL``/``DATABASE_URL``).
"""
from __future__ import annotations

import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.integration

HAUS_A = f"kcc-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"kcc-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture()
def sitzung(require_db):
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt

    assert pruefstand_erlaubt(engine.url)
    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                      {"id": haus, "n": f"Pruefbetrieb {haus}"})
    yield sessionmaker(bind=engine)
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_crm.customers WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        # Seit der Partnerbruecke (01.11.2026) legt jede Kundenanlage auch einen Geschaeftspartner an.
        v.execute(text("DELETE FROM domain_crm.business_partners WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture()
def db(sitzung):
    s = sitzung()
    yield s
    s.close()


def _kunde(db, haus: str) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, is_active) "
                    "VALUES (:i, :h, :n, 'Hof', TRUE)"), {"i": kennung, "h": haus, "n": f"K-{kennung[:6]}"})
    db.commit()
    return kennung


def _core(kennung: str) -> SimpleNamespace:
    return SimpleNamespace(id=kennung, display_name=f"Hof {kennung[:4]}")


def _dienst(db, haus=HAUS_A):
    from app.services.customer_service import CustomerService

    return CustomerService(db, haus)


@pytest.fixture(autouse=True)
def flach():
    # Die Abbildung der crm-core-Felder ist hier nicht Gegenstand.
    with patch("app.services.customer_service._adapt_customer", lambda c, _tenant: {"id": str(c.id), "company_name": c.display_name}):
        yield


def test_liste_paginiert_eigene_kunden_aus_dem_operativen_stamm(db):
    eigene = {_kunde(db, HAUS_A), _kunde(db, HAUS_A)}
    _kunde(db, HAUS_B)
    dienst = _dienst(db)
    erste, total = asyncio.run(dienst.list_customers(limit=1))
    zweite, zweites_total = asyncio.run(dienst.list_customers(skip=1, limit=1))
    assert [len(erste), len(zweite)] == [1, 1]
    assert {erste[0]["id"], zweite[0]["id"]} == eigene
    assert total == zweites_total == 2


def test_fremder_kunde_ist_nicht_abrufbar_aenderbar_oder_loeschbar(db):
    from app.api.v1.schemas.crm import CustomerUpdate
    from app.core.exceptions import EntityNotFoundError

    fremd = _kunde(db, HAUS_B)
    aendern, loeschen = AsyncMock(), AsyncMock()
    with patch("app.services.customer_service._crm_get", AsyncMock(return_value=_core(fremd))), \
         patch("app.services.customer_service._crm_update", aendern), \
         patch("app.services.customer_service._crm_delete", loeschen):
        with pytest.raises(EntityNotFoundError):
            asyncio.run(_dienst(db).get_customer(fremd))
        with pytest.raises(EntityNotFoundError):
            asyncio.run(_dienst(db).update_customer(fremd, CustomerUpdate(company_name="Uebernahme")))
        with pytest.raises(EntityNotFoundError):
            asyncio.run(_dienst(db).delete_customer(fremd))
    aendern.assert_not_awaited()
    loeschen.assert_not_awaited()


def test_eigener_kunde_wird_geaendert(db):
    from app.api.v1.schemas.crm import CustomerUpdate

    eigen = _kunde(db, HAUS_A)
    with patch("app.services.customer_service._crm_update", AsyncMock(return_value=_core(eigen))) as aendern:
        asyncio.run(_dienst(db).update_customer(eigen, CustomerUpdate(company_name="Hof Neu")))
    aendern.assert_awaited_once()


def test_anlage_traegt_den_kunden_im_mandanten_des_kontexts_ein(db):
    from sqlalchemy import text

    from app.api.v1.schemas.crm import CustomerCreate

    neu = str(uuid.uuid4())
    daten = CustomerCreate(customer_number=f"K-{neu[:6]}", company_name="Hof Janssen", country="DE")
    assert daten.tenant_id is None
    with patch("app.services.customer_service._crm_create", AsyncMock(return_value=_core(neu))):
        asyncio.run(_dienst(db).create_customer(daten))
    zeile = db.execute(text("SELECT tenant_id, customer_number FROM domain_crm.customers WHERE id::text = :i"),
                       {"i": neu}).mappings().one()
    assert (zeile["tenant_id"], zeile["customer_number"]) == (HAUS_A, f"K-{neu[:6]}")


def test_anlage_mit_fremdem_mandanten_im_body_wird_abgewiesen(db):
    from fastapi import HTTPException

    from app.api.v1.endpoints.customers import create_customer
    from app.api.v1.schemas.crm import CustomerCreate

    daten = CustomerCreate(customer_number="K-FREMD", company_name="Hof", country="DE", tenant_id=str(uuid.uuid4()))
    with pytest.raises(HTTPException) as fehler:
        asyncio.run(create_customer(daten, db=db, tenant_id=HAUS_A))
    assert fehler.value.status_code == 403
