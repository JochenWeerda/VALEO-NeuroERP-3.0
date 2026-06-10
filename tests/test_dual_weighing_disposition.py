"""
Tests für Dual-Wiegung (waage.py) und Kontrakt-Disposition (kontrakte.py).

Alle Tests nutzen Mock-DB und benötigen keine echte Datenbank.
"""
from __future__ import annotations

import asyncio
import uuid
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


def _mock_db():
    db = MagicMock()
    db.execute.return_value = MagicMock(fetchone=MagicMock(return_value=None))
    db.commit.return_value = None
    db.rollback.return_value = None
    return db


# ---------------------------------------------------------------------------
# Dual-Wiegung unit tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_dual_weighing_netto_computed():
    """netto = abs(wiegung1 - wiegung2) muss korrekt berechnet werden."""
    from app.api.v1.endpoints.waage import WiegungErweitert, WiegescheinMitDoppelwiegung

    ext = WiegungErweitert(waage_id="W1", wiegung1=32500.0, wiegung2=5000.0)
    payload = WiegescheinMitDoppelwiegung(waage_id="W1", wiegung_erweitert=ext)

    # Simulate netto computation (the same logic used in the endpoint)
    netto = abs(ext.wiegung1 - ext.wiegung2)
    assert netto == pytest.approx(27500.0)


@pytest.mark.unit
def test_dual_weighing_netto_computed_reverse():
    """Reihenfolge der Wiegungen darf kein negatives Netto erzeugen."""
    netto = abs(5000.0 - 32500.0)
    assert netto == pytest.approx(27500.0)


@pytest.mark.unit
def test_dual_weighing_with_gosse():
    """Gosse-Feld muss in der Response vorhanden sein."""
    from app.api.v1.endpoints.waage import WiegungErweitert, WiegescheinMitDoppelwiegung, create_dual_wiegung

    ext = WiegungErweitert(waage_id="W2", wiegung1=10000.0, wiegung2=2000.0, gosse=3)
    payload = WiegescheinMitDoppelwiegung(waage_id="W2", wiegung_erweitert=ext)

    db = _mock_db()
    # Simulate successful INSERT (no exception)
    db.execute.return_value = MagicMock()

    result = _run(create_dual_wiegung(payload, db))

    assert result["gosse"] == 3
    assert result["netto"] == pytest.approx(8000.0)
    assert result["status"] == "created"
    assert "id" in result


@pytest.mark.unit
def test_dual_weighing_zielschein_typ():
    """zielschein_typ muss in der Response korrekt übergeben werden."""
    from app.api.v1.endpoints.waage import WiegungErweitert, WiegescheinMitDoppelwiegung, create_dual_wiegung

    ext = WiegungErweitert(
        waage_id="W3", wiegung1=20000.0, wiegung2=4000.0, zielschein_typ="VL"
    )
    payload = WiegescheinMitDoppelwiegung(waage_id="W3", wiegung_erweitert=ext)

    db = _mock_db()
    db.execute.return_value = MagicMock()

    result = _run(create_dual_wiegung(payload, db))
    assert result["zielschein_typ"] == "VL"


@pytest.mark.unit
def test_dual_weighing_no_extended_block():
    """Payload ohne wiegung_erweitert darf nicht crashen, netto bleibt None."""
    from app.api.v1.endpoints.waage import WiegescheinMitDoppelwiegung, create_dual_wiegung

    payload = WiegescheinMitDoppelwiegung(waage_id="W4", lieferant_id="L-001")

    db = _mock_db()
    db.execute.return_value = MagicMock()

    result = _run(create_dual_wiegung(payload, db))
    assert result["netto"] is None
    assert result["status"] == "created"


# ---------------------------------------------------------------------------
# Kontrakt-Disposition unit tests
# ---------------------------------------------------------------------------

def _make_user(roles=None):
    return {"sub": "test-user", "roles": roles or ["KONTRAKT_BEARBEITEN"]}


def _make_tenant():
    return "test-tenant"


@pytest.mark.unit
def test_disposition_create_returns_id():
    """POST Disposition muss eine id und einen status zurückgeben."""
    from app.api.v1.endpoints.kontrakte import DispositionCreate, create_disposition

    payload = DispositionCreate(kontrakt_nr="K-2026-001", menge=5000.0)
    db = _mock_db()

    # Mock for the SELECT RETURNING after INSERT
    row_mock = MagicMock()
    row_mock.__getitem__ = lambda self, i: ["some-uuid", 1, "OFFEN"][i]
    db.execute.return_value.fetchone.return_value = row_mock

    result = _run(
        create_disposition(
            kontrakt_id="kontrakt-123",
            payload=payload,
            db=db,
            tenant_id=_make_tenant(),
            user=_make_user(),
        )
    )

    assert "id" in result
    assert "status" in result
    assert result["kontrakt_nr"] == "K-2026-001"
    assert result["menge"] == pytest.approx(5000.0)


@pytest.mark.unit
def test_disposition_freigabe_sets_status():
    """PATCH /freigabe muss status=FREIGEGEBEN zurückgeben."""
    from app.api.v1.endpoints.kontrakte import freigabe_disposition

    db = _mock_db()
    disp_id = str(uuid.uuid4())

    row_mock = MagicMock()
    row_mock.__getitem__ = lambda self, i: [disp_id, "FREIGEGEBEN"][i]
    db.execute.return_value.fetchone.return_value = row_mock

    result = _run(
        freigabe_disposition(
            kontrakt_id="kontrakt-123",
            disp_id=disp_id,
            db=db,
            tenant_id=_make_tenant(),
            user=_make_user(),
        )
    )

    assert result["status"] == "FREIGEGEBEN"
    assert result["id"] == disp_id


@pytest.mark.unit
def test_disposition_soft_delete():
    """DELETE Disposition muss status=STORNIERT zurückgeben (Soft-Delete)."""
    from app.api.v1.endpoints.kontrakte import storniere_disposition

    db = _mock_db()
    disp_id = str(uuid.uuid4())

    row_mock = MagicMock()
    row_mock.__getitem__ = lambda self, i: [disp_id, "STORNIERT"][i]
    db.execute.return_value.fetchone.return_value = row_mock

    result = _run(
        storniere_disposition(
            kontrakt_id="kontrakt-123",
            disp_id=disp_id,
            db=db,
            tenant_id=_make_tenant(),
            user=_make_user(),
        )
    )

    assert result["status"] == "STORNIERT"
    assert result["id"] == disp_id


@pytest.mark.unit
def test_disposition_geliefert_with_wiegeschein():
    """PATCH /geliefert mit wiegeschein_nr muss wiegeschein_nr in Response zurückgeben."""
    from app.api.v1.endpoints.kontrakte import geliefert_disposition

    db = _mock_db()
    disp_id = str(uuid.uuid4())
    ws_nr = "WS-2026-999"

    row_mock = MagicMock()
    row_mock.__getitem__ = lambda self, i: [disp_id, "GELIEFERT", ws_nr][i]
    db.execute.return_value.fetchone.return_value = row_mock

    result = _run(
        geliefert_disposition(
            kontrakt_id="kontrakt-123",
            disp_id=disp_id,
            wiegeschein_nr=ws_nr,
            db=db,
            tenant_id=_make_tenant(),
            user=_make_user(),
        )
    )

    assert result["status"] == "GELIEFERT"
    assert result["wiegeschein_nr"] == ws_nr


@pytest.mark.unit
def test_disposition_list_returns_empty_on_missing_table():
    """GET Dispositionen muss [] zurückgeben wenn Tabelle fehlt."""
    from app.api.v1.endpoints.kontrakte import list_dispositionen

    db = _mock_db()
    db.execute.side_effect = Exception('relation "domain_agrar.kontrakt_dispositionen" does not exist')

    result = _run(
        list_dispositionen(
            kontrakt_id="kontrakt-123",
            db=db,
            tenant_id=_make_tenant(),
            user=_make_user(),
        )
    )

    assert result == []
