"""Wave 86 — Unit-Tests fuer business_partner_service, crm_kunden_map_service,
compensation_engine, controlling_service (pure domain functions)."""

from __future__ import annotations

import pytest
import asyncio


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# business_partner_service — resolve_customer_ref  (pure identity resolution)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_resolve_customer_ref_business_partner_id_preferred() -> None:
    from app.services.business_partner_service import resolve_customer_ref
    entry = {"business_partner_id": "BP-001", "partner_number": "P-999", "kunden_nr": "K-999"}
    result = resolve_customer_ref(entry)
    assert result == "BP-001"


@pytest.mark.unit
def test_resolve_customer_ref_falls_back_to_partner_number() -> None:
    from app.services.business_partner_service import resolve_customer_ref
    entry = {"partner_number": "P-001", "kunden_nr": "K-999"}
    result = resolve_customer_ref(entry)
    assert result == "P-001"


@pytest.mark.unit
def test_resolve_customer_ref_falls_back_to_kunden_nr() -> None:
    from app.services.business_partner_service import resolve_customer_ref
    entry = {"kunden_nr": "K-001"}
    result = resolve_customer_ref(entry)
    assert result == "K-001"


@pytest.mark.unit
def test_resolve_customer_ref_empty_dict_returns_none() -> None:
    from app.services.business_partner_service import resolve_customer_ref
    result = resolve_customer_ref({})
    assert result is None


@pytest.mark.unit
def test_resolve_customer_ref_none_returns_none() -> None:
    from app.services.business_partner_service import resolve_customer_ref
    result = resolve_customer_ref(None)
    assert result is None


# ---------------------------------------------------------------------------
# crm_kunden_map_service — deoverlap  (pure in-place geometry jitter)
# ---------------------------------------------------------------------------

def _make_feature(lon, lat, precision="city", kunden_nr="K-001"):
    return {
        "geometry": {"coordinates": [lon, lat]},
        "properties": {"kunden_nr": kunden_nr, "precision": precision},
    }


@pytest.mark.unit
def test_deoverlap_single_point_unchanged() -> None:
    from app.services.crm_kunden_map_service import deoverlap
    f = _make_feature(13.405, 52.52)
    deoverlap([f])
    # Single point with no overlaps — no change expected
    assert f["geometry"]["coordinates"] == [13.405, 52.52]


@pytest.mark.unit
def test_deoverlap_two_overlapping_points_separated() -> None:
    from app.services.crm_kunden_map_service import deoverlap
    f1 = _make_feature(13.405, 52.52, "city", "K-001")
    f2 = _make_feature(13.405, 52.52, "city", "K-002")
    deoverlap([f1, f2])
    lon1, lat1 = f1["geometry"]["coordinates"]
    lon2, lat2 = f2["geometry"]["coordinates"]
    # At least one point must have moved
    assert (lon1, lat1) != (lon2, lat2)


@pytest.mark.unit
def test_deoverlap_address_precision_not_moved() -> None:
    from app.services.crm_kunden_map_service import deoverlap
    f_addr = _make_feature(13.405, 52.52, "address", "K-001")
    f_city = _make_feature(13.405, 52.52, "city", "K-002")
    deoverlap([f_addr, f_city])
    # address-precision point must not be moved
    assert f_addr["geometry"]["coordinates"] == [13.405, 52.52]


@pytest.mark.unit
def test_deoverlap_returns_none_modifies_in_place() -> None:
    from app.services.crm_kunden_map_service import deoverlap
    features = [_make_feature(10.0, 50.0, "city", "K-001")]
    result = deoverlap(features)
    assert result is None


# ---------------------------------------------------------------------------
# compensation_engine — compensate, get_compensation_run  (async, in-memory)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compensate_rollback_strategy() -> None:
    from app.services.compensation_engine import compensate, CompensationStatus
    async def run():
        return await compensate(
            {"error": "db_write_failed"},
            strategy="rollback",
            rollback_steps=[{"action": "undo_create", "entity": "INV-001"}],
        )
    result = _run(run())
    assert result.status == CompensationStatus.ROLLED_BACK


@pytest.mark.unit
def test_compensate_returns_compensation_run_with_id() -> None:
    from app.services.compensation_engine import compensate
    async def run():
        return await compensate({"error": "test"}, strategy="rollback")
    result = _run(run())
    assert result.run_id is not None
    assert len(result.run_id) > 0


@pytest.mark.unit
def test_compensate_stores_run_for_retrieval() -> None:
    from app.services.compensation_engine import compensate, get_compensation_run
    async def run():
        return await compensate({"error": "store_test"}, strategy="rollback")
    result = _run(run())
    retrieved = get_compensation_run(result.run_id)
    assert retrieved is not None
    assert retrieved.run_id == result.run_id


@pytest.mark.unit
def test_get_compensation_run_unknown_id_returns_none() -> None:
    from app.services.compensation_engine import get_compensation_run
    result = get_compensation_run("00000000-0000-0000-0000-nonexistent")
    assert result is None


@pytest.mark.unit
def test_compensate_escalate_strategy() -> None:
    from app.services.compensation_engine import compensate, CompensationStatus
    async def run():
        return await compensate({"error": "critical_failure"}, strategy="escalate")
    result = _run(run())
    assert result.status == CompensationStatus.ESCALATED


# ---------------------------------------------------------------------------
# controlling_service — invalidate_tenant_prefix  (redis-optional, no-crash)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_invalidate_tenant_prefix_no_crash_without_redis() -> None:
    from app.services.controlling_service import invalidate_tenant_prefix
    # Should silently succeed even if Redis is not available
    result = invalidate_tenant_prefix("orders", "T001")
    assert result is None


@pytest.mark.unit
def test_invalidate_tenant_prefix_empty_prefix() -> None:
    from app.services.controlling_service import invalidate_tenant_prefix
    result = invalidate_tenant_prefix("", "T001")
    assert result is None
