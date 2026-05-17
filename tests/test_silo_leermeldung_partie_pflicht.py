"""
Unit tests for SILO-LEER-001 (Silo-Leermeldung) and PARTIE-PFLICHT-001 (Partiepflicht).
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_db():
    """Return a simple MagicMock for a SQLAlchemy Session."""
    return MagicMock()


def _make_silo(silo_id="silo-1", tenant_id="t1", status="active"):
    silo = MagicMock()
    silo.id = silo_id
    silo.tenant_id = tenant_id
    silo.status = status
    silo.is_active = True
    return silo


def _make_lot(lot_id="lot-1", silo_id="silo-1", status="closed", quantity_tons=0):
    lot = MagicMock()
    lot.id = lot_id
    lot.silo_id = silo_id
    lot.status = status
    lot.quantity_tons = quantity_tons
    return lot


# ---------------------------------------------------------------------------
# SILO-LEER-001 Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_leermeldung_raises_if_silo_not_found():
    """404 wenn Silo nicht existiert oder falsche tenant_id."""
    from app.api.v1.endpoints.silo import create_leermeldung, LeermeldungCreate

    db = _make_mock_db()
    # query(...).filter(...).first() returns None
    db.query.return_value.filter.return_value.first.return_value = None

    payload = LeermeldungCreate(schwund_kg=0, grund="Test", bearbeiter="Max")

    with pytest.raises(HTTPException) as exc_info:
        await create_leermeldung(
            silo_id="nonexistent",
            payload=payload,
            tenant_id="t1",
            db=db,
        )
    assert exc_info.value.status_code == 404


@pytest.mark.unit
@pytest.mark.asyncio
async def test_leermeldung_raises_if_open_lots_exist():
    """422 wenn noch offene Lots mit Restbestand vorhanden sind."""
    from app.api.v1.endpoints.silo import create_leermeldung, LeermeldungCreate

    db = _make_mock_db()
    silo = _make_silo()

    # first() for silo query returns the mock silo
    # scalar() for open_lot_count returns 1 (open lot exists)
    filter_mock = MagicMock()
    filter_mock.first.return_value = silo
    filter_mock.scalar.return_value = 1

    db.query.return_value.filter.return_value = filter_mock

    payload = LeermeldungCreate(schwund_kg=5000, grund="Leerung", bearbeiter="Max")

    with pytest.raises(HTTPException) as exc_info:
        await create_leermeldung(
            silo_id="silo-1",
            payload=payload,
            tenant_id="t1",
            db=db,
        )
    assert exc_info.value.status_code == 422
    assert "Offene Lots" in exc_info.value.detail


@pytest.mark.unit
@pytest.mark.asyncio
async def test_leermeldung_success():
    """Erfolgreiche Leermeldung: Silo existiert, keine offenen Lots, schwund=0."""
    from app.api.v1.endpoints.silo import create_leermeldung, LeermeldungCreate
    from unittest.mock import call

    db = _make_mock_db()
    silo = _make_silo(status="active")
    lot = _make_lot(status="closed", quantity_tons=0)

    # db.query(...) is called multiple times; use side_effect to return different mocks
    # Call order in create_leermeldung:
    #   1. db.query(Silo) → silo lookup
    #   2. db.query(func.count(SiloLot.id)) → open lot count
    #   3. db.query(SiloLot) → update lots
    #   4. db.query(SiloLot) (any_lot) → first lot
    #   5. SiloQualitySnapshot in _create_snapshot → db.query(SiloLot)

    silo_q = MagicMock()
    silo_q.filter.return_value.first.return_value = silo

    count_q = MagicMock()
    count_q.filter.return_value.scalar.return_value = 0

    # any_lot query
    any_lot_q = MagicMock()
    any_lot_q.filter.return_value.first.return_value = lot

    # update query + snapshot lots query (return empty list for snapshot)
    update_q = MagicMock()
    update_q.filter.return_value.update.return_value = None
    update_q.filter.return_value.all.return_value = []

    db.query.side_effect = [silo_q, count_q, any_lot_q, update_q, update_q]

    # Raw SQL calls: _silo_columns (fetchall), restbestand (fetchone), status/meta updates
    fetchone_mock = MagicMock()
    fetchone_mock.__getitem__ = lambda self, i: 0  # restbestand = 0
    db.execute.return_value.fetchone.return_value = fetchone_mock
    db.execute.return_value.fetchall.return_value = []  # no silo columns → no optional updates

    payload = LeermeldungCreate(schwund_kg=0, grund="Reguläre Leerung", bearbeiter="Anna")

    result = await create_leermeldung(
        silo_id="silo-1",
        payload=payload,
        tenant_id="t1",
        db=db,
    )

    assert result["silo_id"] == "silo-1"
    assert result["status"] == "LEER"
    assert result["schwund_kg"] == 0
    assert "leermeldung_id" in result
    assert result["message"] == "Silo erfolgreich geleert"
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# PARTIE-PFLICHT-001 Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_partiepflicht_check_valid():
    """ROHWARE mit partie_id → valid=True."""
    from app.api.v1.endpoints.waage import check_partiepflicht, PartiepflichtCheckRequest

    db = _make_mock_db()
    db.execute.return_value.fetchone.return_value = None

    payload = PartiepflichtCheckRequest(
        artikel_id="art-1",
        wiegetyp="ROHWARE",
        partie_id="partie-abc",
    )
    result = await check_partiepflicht(payload=payload, db=db)
    assert result["valid"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_partiepflicht_check_invalid():
    """ROHWARE ohne partie_id → valid=False."""
    from app.api.v1.endpoints.waage import check_partiepflicht, PartiepflichtCheckRequest

    db = _make_mock_db()
    db.execute.return_value.fetchone.return_value = None

    payload = PartiepflichtCheckRequest(
        artikel_id="art-1",
        wiegetyp="ROHWARE",
        partie_id=None,
    )
    result = await check_partiepflicht(payload=payload, db=db)
    assert result["valid"] is False
    assert "Partie erforderlich" in result["reason"]
    assert "ROHWARE" in result["reason"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_partiepflicht_check_not_required():
    """Normaler Wiegetyp ohne Partiepflicht → immer valid."""
    from app.api.v1.endpoints.waage import check_partiepflicht, PartiepflichtCheckRequest

    db = _make_mock_db()
    db.execute.return_value.fetchone.return_value = None

    payload = PartiepflichtCheckRequest(
        artikel_id="art-99",
        wiegetyp="ABFALL",
        partie_id=None,
    )
    result = await check_partiepflicht(payload=payload, db=db)
    assert result["valid"] is True
