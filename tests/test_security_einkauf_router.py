"""Tenant regressions exercise the leading purchasing handlers and real service."""
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.api.v1.endpoints import einkauf_bestellvorschlag as endpoint


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["lieferant", "bestellung"])
@pytest.mark.parametrize("operation", ["get", "update"])
async def test_missing_entity_lookup_keeps_id_and_context_tenant(kind, operation):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    entity_id = "00000000-0000-4000-8000-000000000071"
    kwargs = {f"{kind}_id": entity_id, "tenant_id": "tenant-a", "db": db}
    if operation == "update":
        kwargs["data"] = endpoint.LieferantUpdate(firmenname="Neu") if kind == "lieferant" else {"notiz": "Neu"}
    with pytest.raises(HTTPException) as exc:
        await getattr(endpoint, f"{operation}_{kind}")(**kwargs)
    assert exc.value.status_code == 404
    model = db.query.call_args.args[0]
    criteria = db.query.return_value.filter.call_args.args
    query = select(model).where(*criteria).compile()
    assert set(query.params.values()) == {entity_id, "tenant-a"}
    assert ".tenant_id =" in str(query) and ".id =" in str(query)
    db.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_lieferant_persists_context_tenant_despite_payload_override():
    db = MagicMock()
    payload = endpoint.LieferantCreate(
        lieferantennummer="L-100", firmenname="Lieferant GmbH",
        email="test@example.com", tenant_id="foreign-tenant",
    )
    result = await endpoint.create_lieferant(data=payload, tenant_id="tenant-a", db=db)
    stored = db.add.call_args.args[0]
    assert stored.tenant_id == "tenant-a"
    assert stored.lieferantennummer == "L-100"
    assert result["id"] == str(stored.id)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(stored)


@pytest.mark.asyncio
async def test_create_bestellung_persists_context_tenant_despite_payload_override():
    db = MagicMock()
    payload = endpoint.BestellungCreate(
        lieferant_id="00000000-0000-4000-8000-000000000017",
        bestelldatum=date(2026, 4, 1), tenant_id="foreign-tenant",
    )
    result = await endpoint.create_bestellung(data=payload, tenant_id="tenant-a", db=db)
    stored = db.add.call_args.args[0]
    assert stored.tenant_id == "tenant-a"
    assert stored.lieferant_id == payload.lieferant_id
    assert stored.bestelldatum == payload.bestelldatum
    assert result["id"] == str(stored.id)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(stored)
