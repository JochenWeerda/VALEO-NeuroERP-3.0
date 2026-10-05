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
#
# Bis zum 05.10.2026 forderte ein Test hier genau den Fehler ein:
# "Reihenfolge der Wiegungen darf kein negatives Netto erzeugen" — mit
# ``netto = abs(wiegung1 - wiegung2)`` als Beweis. Der Absolutbetrag verdeckt
# aber den Vorzeichenfehler: Eine Tara schwerer als das Brutto ist ein Messfehler
# oder eine Verwechslung der beiden Eingaben, und daraus wurde ein plausibles
# positives Nettogewicht, auf dem die Rechnung aufbaute.
#
# Drei weitere Tests riefen ``create_dual_wiegung(payload, db)`` positionell auf
# und trafen damit den Parameter ``tenant_id``. Sie waren rot, seit der Weg eine
# Mandantenabhaengigkeit hat — der Weg war kaputt und nur scheinbar geprueft.
#
# Der fachliche Nachweis gegen eine echte Datenbank steht in
# ``tests/test_wiegung_kanonisch_vertrag.py``.


@pytest.mark.unit
def test_netto_ist_brutto_minus_tara():
    from app.services.wiegung_service import netto_aus_doppelwiegung

    brutto, tara, netto = netto_aus_doppelwiegung(32500.0, 5000.0, None)
    assert brutto == pytest.approx(32500.0)
    assert tara == pytest.approx(5000.0)
    assert netto == pytest.approx(27500.0)


@pytest.mark.unit
def test_vertauschte_waegungen_sind_ein_fehler():
    """Vorher: ``abs(5000 - 32500) == 27500`` — ein Netto aus einem Messfehler."""
    from fastapi import HTTPException

    from app.services.wiegung_service import netto_aus_doppelwiegung

    with pytest.raises(HTTPException) as fehler:
        netto_aus_doppelwiegung(5000.0, 32500.0, None)
    assert fehler.value.status_code == 422
    assert "vertauscht" in str(fehler.value.detail)


@pytest.mark.unit
def test_gleiche_waegungen_ergeben_kein_netto():
    from fastapi import HTTPException

    from app.services.wiegung_service import netto_aus_doppelwiegung

    with pytest.raises(HTTPException):
        netto_aus_doppelwiegung(20000.0, 20000.0, None)


@pytest.mark.unit
def test_ausgewiesenes_netto_wird_uebernommen():
    """Handwiegung oder Fremdwaage: Es gibt keine zwei Messungen zum Nachrechnen."""
    from app.services.wiegung_service import netto_aus_doppelwiegung

    assert netto_aus_doppelwiegung(None, None, 18000.0)[2] == pytest.approx(18000.0)


@pytest.mark.unit
def test_ohne_jedes_gewicht_ist_der_schein_kein_beleg():
    from fastapi import HTTPException

    from app.services.wiegung_service import netto_aus_doppelwiegung

    with pytest.raises(HTTPException) as fehler:
        netto_aus_doppelwiegung(None, None, None)
    assert "kein Beleg" in str(fehler.value.detail)


@pytest.mark.unit
def test_zielscheintyp_wird_auf_die_richtung_abgebildet():
    """EL = Eingangslieferschein (Zugang), VL = Verkaufslieferschein (Abgang)."""
    from app.services.wiegung_service import richtung

    assert richtung("EL") == "in"
    assert richtung("VL") == "out"
    # Ohne Angabe gilt der Zugang — das ist der Regelfall an der Annahme.
    assert richtung(None) == "in"


@pytest.mark.unit
def test_unbekannter_zielscheintyp_ist_kein_stiller_zugang():
    """Ein stilles ``in`` haette eine Verkaufslieferung als Zugang gefuehrt."""
    from fastapi import HTTPException

    from app.services.wiegung_service import richtung

    with pytest.raises(HTTPException) as fehler:
        richtung("UMLAGERUNG")
    assert fehler.value.status_code == 422


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
