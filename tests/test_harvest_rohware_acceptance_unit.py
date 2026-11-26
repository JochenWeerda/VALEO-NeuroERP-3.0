"""Executable Unit-Tests: Rohware-Annahme-Endpoint (Sonar New-Code-Coverage)."""
from __future__ import annotations

import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.harvest_acceptance import (
    RohwareAcceptanceCreate,
    create_rohware_acceptance,
)


def _payload(**overrides):
    base = dict(
        lieferant="Hof Müller",
        artikel="Weizen",
        brutto_kg=1000.0,
        tara_kg=50.0,
        netto_kg=950.0,
        kennzeichen="B-TEST 1",
        lager_ziel="SILO-A",
        is_rohware=True,
    )
    base.update(overrides)
    return RohwareAcceptanceCreate(**base)


def test_rohware_ohne_customer_und_ohne_treffer_422():
    db = MagicMock()
    request = MagicMock()
    with patch(
        "app.services.business_partner_service.BusinessPartnerService"
    ) as bp_cls, patch(
        "app.api.v1.endpoints.harvest_acceptance._get_user_id_from_request",
        return_value="user-1",
    ):
        bp_cls.return_value.find_customer_id_by_name.return_value = None
        with pytest.raises(HTTPException) as exc:
            asyncio.run(
                create_rohware_acceptance(
                    _payload(customer_id=None),
                    request=request,
                    tenant_id="t1",
                    db=db,
                )
            )
    assert exc.value.status_code == 422
    assert "Debitor" in str(exc.value.detail)


def test_rohware_mappt_datum_iso_und_qualitaet_in_remarks():
    db = MagicMock()
    request = MagicMock()
    article = SimpleNamespace(id="art-9")
    db.query.return_value.filter.return_value.first.return_value = article
    created = SimpleNamespace(id="ha-1")

    with patch(
        "app.api.v1.endpoints.harvest_acceptance._get_user_id_from_request",
        return_value="user-1",
    ), patch(
        "app.api.v1.endpoints.harvest_acceptance._svc"
    ) as svc_factory, patch(
        "app.api.v1.endpoints.harvest_acceptance.business_today",
        return_value=date(2026, 11, 1),
    ):
        svc_factory.return_value.create_acceptance.return_value = created
        result = asyncio.run(
            create_rohware_acceptance(
                _payload(
                    customer_id="cust-1",
                    datum="2026-11-15T14:30:00Z",
                    lieferschein_nr="LS-9",
                    feuchte_pct=14.5,
                    besatz_pct=1.2,
                    fallzahl=250,
                ),
                request=request,
                tenant_id="t1",
                db=db,
            )
        )
    assert result is created
    mapped = svc_factory.return_value.create_acceptance.call_args.args[0]
    assert mapped.customer_id == "cust-1"
    assert mapped.article_id == "art-9"
    assert mapped.delivery_date == date(2026, 11, 15)
    assert mapped.delivery_time == "14:30"
    assert mapped.vehicle_plate == "B-TEST 1"
    assert "Lieferschein=LS-9" in mapped.remarks
    assert "Feuchte=14.5%" in mapped.remarks
    assert "Besatz=1.2%" in mapped.remarks
    assert "Fallzahl=250" in mapped.remarks


def test_rohware_datum_nur_tag_bei_ungueltigem_iso():
    db = MagicMock()
    request = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    created = SimpleNamespace(id="ha-2")

    with patch(
        "app.api.v1.endpoints.harvest_acceptance._get_user_id_from_request",
        return_value="user-1",
    ), patch(
        "app.api.v1.endpoints.harvest_acceptance._svc"
    ) as svc_factory, patch(
        "app.api.v1.endpoints.harvest_acceptance.business_today",
        return_value=date(2026, 11, 1),
    ):
        svc_factory.return_value.create_acceptance.return_value = created
        asyncio.run(
            create_rohware_acceptance(
                _payload(customer_id="cust-1", datum="2026-11-18Txx"),
                request=request,
                tenant_id="t1",
                db=db,
            )
        )
    mapped = svc_factory.return_value.create_acceptance.call_args.args[0]
    assert mapped.delivery_date == date(2026, 11, 18)
    assert mapped.delivery_time is None
    assert mapped.article_id is None


def test_rohware_customer_per_name_lookup():
    db = MagicMock()
    request = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    created = SimpleNamespace(id="ha-3")

    with patch(
        "app.services.business_partner_service.BusinessPartnerService"
    ) as bp_cls, patch(
        "app.api.v1.endpoints.harvest_acceptance._get_user_id_from_request",
        return_value="user-1",
    ), patch(
        "app.api.v1.endpoints.harvest_acceptance._svc"
    ) as svc_factory, patch(
        "app.api.v1.endpoints.harvest_acceptance.business_today",
        return_value=date(2026, 11, 1),
    ):
        bp_cls.return_value.find_customer_id_by_name.return_value = "cust-from-name"
        svc_factory.return_value.create_acceptance.return_value = created
        asyncio.run(
            create_rohware_acceptance(
                _payload(customer_id="  "),
                request=request,
                tenant_id="t1",
                db=db,
            )
        )
    mapped = svc_factory.return_value.create_acceptance.call_args.args[0]
    assert mapped.customer_id == "cust-from-name"


def test_rohware_domain_fehler_werden_gemappt():
    from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError

    db = MagicMock()
    request = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    cases = [
        (EntityNotFoundError("Annahme", "x"), 404),
        (ConflictError("Konflikt"), 409),
        (ValidationFailedError("ungültig"), 422),
    ]
    for err, status in cases:
        with patch(
            "app.api.v1.endpoints.harvest_acceptance._get_user_id_from_request",
            return_value="user-1",
        ), patch(
            "app.api.v1.endpoints.harvest_acceptance._svc"
        ) as svc_factory, patch(
            "app.api.v1.endpoints.harvest_acceptance.business_today",
            return_value=date(2026, 11, 1),
        ):
            svc_factory.return_value.create_acceptance.side_effect = err
            with pytest.raises(HTTPException) as exc:
                asyncio.run(
                    create_rohware_acceptance(
                        _payload(customer_id="cust-1"),
                        request=request,
                        tenant_id="t1",
                        db=db,
                    )
                )
            assert exc.value.status_code == status
