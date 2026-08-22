from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit


def test_deep_l3_masks_are_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    screen_ids = (
        "auswertungen/sanktionspruefung-personal",
        "auswertungen/sanktionspruefung-kunden",
        "auswertungen/duengemittelmengen",
        "produktion/chargen-bearbeiten",
    )
    for screen_id in screen_ids:
        definition = get_screen_definition(screen_id)
        assert definition["adapter"] == {
            "type": "native",
            "sourceId": screen_id,
            "temporary": False,
        }
        assert _check_readiness(definition)["generatorReady"] is True


def test_sanctions_protocol_is_tenant_and_scope_filtered() -> None:
    from app.api.v1.endpoints.sanctions_compliance import pruefprotokoll

    db = MagicMock()
    db.execute.return_value.fetchall.return_value = []
    assert pruefprotokoll(scope="personal", db=db, tenant_id="tenant-1") == []
    sql = str(db.execute.call_args.args[0])
    params = db.execute.call_args.args[1]
    assert "tenant_id = :tenant_id" in sql and "scope = :scope" in sql
    assert params == {"tenant_id": "tenant-1", "scope": "personal"}


def test_charge_repository_starts_with_tenant_scope() -> None:
    from app.domains.operations.repository import ChargeRepository

    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.count.return_value = 0
    assert ChargeRepository(db, "tenant-1").count() == 0
    assert query.filter.called
