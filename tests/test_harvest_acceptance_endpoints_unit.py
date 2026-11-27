"""Executable Unit-Tests: Harvest-Acceptance Endpoint-Exception-Mapping (Sonar New-Code)."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import harvest_acceptance as ha
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError


def _run(coro):
    return asyncio.run(coro)


def test_derive_nuts2_maps_not_found_and_validation():
    db = MagicMock()
    svc = MagicMock()
    with patch.object(ha, "_svc", return_value=svc):
        svc.derive_nuts2.side_effect = EntityNotFoundError("HarvestAcceptance", "acc-1")
        with pytest.raises(HTTPException) as exc:
            _run(ha.derive_nuts2_from_postal_code_endpoint("acc-1", tenant_id="t1", db=db))
        assert exc.value.status_code == 404

        svc.derive_nuts2.side_effect = ValidationFailedError("bad plz")
        with pytest.raises(HTTPException) as exc2:
            _run(ha.derive_nuts2_from_postal_code_endpoint("acc-1", tenant_id="t1", db=db))
        assert exc2.value.status_code == 400


def test_derive_nuts2_success():
    db = MagicMock()
    svc = MagicMock()
    svc.derive_nuts2.return_value = SimpleNamespace(nuts2_code="DE60")
    with patch.object(ha, "_svc", return_value=svc):
        out = _run(ha.derive_nuts2_from_postal_code_endpoint("acc-1", tenant_id="t1", db=db))
    assert out.nuts2_code == "DE60"


def test_cancel_maps_conflict_and_not_found():
    db = MagicMock()
    svc = MagicMock()
    with patch.object(ha, "_svc", return_value=svc):
        svc.cancel.side_effect = ConflictError("already final")
        with pytest.raises(HTTPException) as exc:
            _run(ha.cancel_harvest_acceptance("acc-1", reason="Irrtum", tenant_id="t1", db=db))
        assert exc.value.status_code == 409

        svc.cancel.side_effect = EntityNotFoundError("HarvestAcceptance", "acc-1")
        with pytest.raises(HTTPException) as exc2:
            _run(ha.cancel_harvest_acceptance("acc-1", reason="Irrtum", tenant_id="t1", db=db))
        assert exc2.value.status_code == 404

        svc.cancel.side_effect = ValidationFailedError("empty")
        with pytest.raises(HTTPException) as exc3:
            _run(ha.cancel_harvest_acceptance("acc-1", reason="Irrtum", tenant_id="t1", db=db))
        assert exc3.value.status_code == 400


def test_cancel_success():
    db = MagicMock()
    svc = MagicMock()
    svc.cancel.return_value = SimpleNamespace(id="acc-1", status="cancelled")
    with patch.object(ha, "_svc", return_value=svc):
        out = _run(ha.cancel_harvest_acceptance("acc-1", reason="Doppelbuchung", tenant_id="t1", db=db))
    assert out.id == "acc-1"


def test_calculate_settlement_maps_errors():
    db = MagicMock()
    payload = MagicMock()
    request = MagicMock()
    user = {"sub": "u1"}
    with patch.object(ha, "verified_principal", return_value=SimpleNamespace(id="u1")):
        with patch.object(ha, "controlled_service", return_value=(MagicMock(), MagicMock())) as cs:
            service = cs.return_value[0]
            with patch.object(ha, "execute") as execute:
                execute.side_effect = EntityNotFoundError("HarvestAcceptance", "acc-1")
                with pytest.raises(HTTPException) as exc:
                    _run(
                        ha.calculate_harvest_settlement_endpoint(
                            "acc-1", payload, request, tenant_id="t1", db=db, user=user
                        )
                    )
                assert exc.value.status_code == 404

                execute.side_effect = ValidationFailedError("bad")
                with pytest.raises(HTTPException) as exc2:
                    _run(
                        ha.calculate_harvest_settlement_endpoint(
                            "acc-1", payload, request, tenant_id="t1", db=db, user=user
                        )
                    )
                assert exc2.value.status_code == 400
                assert service is not None


def test_release_without_credit_note_uses_svc():
    db = MagicMock()
    request = MagicMock()
    request.headers = {}
    svc = MagicMock()
    svc.release_acceptance.return_value = SimpleNamespace(id="acc-1", release_status="provisional")
    with patch.object(ha, "_get_user_id_from_request", return_value="u1"):
        with patch.object(ha, "_svc", return_value=svc):
            out = _run(
                ha.release_harvest_acceptance(
                    "acc-1",
                    release_status="provisional",
                    create_stock_movement=True,
                    create_credit_note=False,
                    request=request,
                    tenant_id="t1",
                    db=db,
                    payload=None,
                    user={"sub": "u1"},
                )
            )
    assert out.id == "acc-1"
    svc.release_acceptance.assert_called_once()


def test_release_final_credit_note_requires_payload():
    db = MagicMock()
    request = MagicMock()
    with patch.object(ha, "_get_user_id_from_request", return_value="u1"):
        with pytest.raises(HTTPException) as exc:
            _run(
                ha.release_harvest_acceptance(
                    "acc-1",
                    release_status="final",
                    create_stock_movement=True,
                    create_credit_note=True,
                    request=request,
                    tenant_id="t1",
                    db=db,
                    payload=None,
                    user={"sub": "u1"},
                )
            )
    assert exc.value.status_code == 422


def test_get_and_delete_map_not_found():
    db = MagicMock()
    svc = MagicMock()
    with patch.object(ha, "_svc", return_value=svc):
        svc.get_acceptance.side_effect = EntityNotFoundError("HarvestAcceptance", "acc-1")
        with pytest.raises(HTTPException) as exc:
            _run(ha.get_harvest_acceptance("acc-1", tenant_id="t1", db=db))
        assert exc.value.status_code == 404

        svc.delete_acceptance.side_effect = EntityNotFoundError("HarvestAcceptance", "acc-1")
        with pytest.raises(HTTPException) as exc2:
            _run(ha.delete_harvest_acceptance("acc-1", tenant_id="t1", db=db))
        assert exc2.value.status_code == 404

        svc.delete_acceptance.side_effect = ValidationFailedError("blocked")
        with pytest.raises(HTTPException) as exc3:
            _run(ha.delete_harvest_acceptance("acc-1", tenant_id="t1", db=db))
        assert exc3.value.status_code == 400
