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
#
# Bis zum 05.10.2026 forderte ein Test hier den Fehler ein:
# ``test_disposition_list_returns_empty_on_missing_table`` — "GET Dispositionen
# muss [] zurückgeben wenn Tabelle fehlt". Die Tabelle fehlte in **jeder**
# Datenbank, weil keine Migration sie anlegt; der Endpunkt fing den Lesefehler,
# und ein Kontrakt ohne sichtbare Abrufe sieht aus wie ein ganz offener Kontrakt
# — genau danach würde disponiert.
#
# Die vier anderen Tests prüften Antwortformen gegen `fetchone()`-Doubles, also
# die Form und nicht die Regel: Keiner von ihnen hätte bemerkt, dass niemand die
# Kontraktmenge prüft, dass `freigabe` und `status` dasselbe zweimal sagen oder
# dass eine stornierte Disposition als geliefert gemeldet werden kann.
#
# Der fachliche Nachweis gegen eine echte Datenbank steht in
# ``tests/test_kontrakt_disposition_vertrag.py``.


@pytest.mark.unit
def test_zustandswoerterbuch_hat_eine_quelle():
    from app.services import kontrakt_disposition_service as dispo

    assert set(dispo.UEBERGAENGE) == set(dispo.ZUSTAENDE)
    assert set(dispo.BINDEND) <= set(dispo.ZUSTAENDE)
    assert "STORNIERT" not in dispo.BINDEND, "Ein stornierter Abruf bindet keine Menge"


@pytest.mark.unit
def test_geliefert_nur_aus_der_freigabe():
    """Sonst wäre die Freigabe kein Tor, sondern eine Notiz."""
    from fastapi import HTTPException

    from app.services import kontrakt_disposition_service as dispo

    dispo.uebergang_pruefen("FREIGEGEBEN", "GELIEFERT", 1)
    with pytest.raises(HTTPException) as fehler:
        dispo.uebergang_pruefen("OFFEN", "GELIEFERT", 1)
    assert fehler.value.status_code == 409
    assert "Freigabe" in str(fehler.value.detail)


@pytest.mark.unit
@pytest.mark.parametrize("von,nach", [
    ("GELIEFERT", "STORNIERT"),
    ("GELIEFERT", "FREIGEGEBEN"),
    ("STORNIERT", "GELIEFERT"),
    ("STORNIERT", "FREIGEGEBEN"),
])
def test_endgueltige_zustaende_bleiben(von, nach):
    from fastapi import HTTPException

    from app.services import kontrakt_disposition_service as dispo

    with pytest.raises(HTTPException) as fehler:
        dispo.uebergang_pruefen(von, nach, 7)
    assert "endgueltig" in str(fehler.value.detail)


@pytest.mark.unit
def test_abruf_ueber_der_kontraktmenge_wird_abgewiesen():
    """Die Regel stand mit ``allow_overdelivery`` im Modell und wurde nie gelesen."""
    from decimal import Decimal

    from fastapi import HTTPException

    from app.services import kontrakt_disposition_service as dispo

    position = {
        "contract_no": "K-2026-001", "position_no": 1,
        "qty_contract": Decimal("100"), "ueberlieferung_erlaubt": False,
    }
    dispo.menge_pruefen(position, Decimal("40"), 60)
    with pytest.raises(HTTPException) as fehler:
        dispo.menge_pruefen(position, Decimal("40"), 61)
    assert fehler.value.status_code == 409
    assert "allow_overdelivery" in str(fehler.value.detail)


@pytest.mark.unit
def test_ueberlieferung_wenn_der_kontrakt_sie_erlaubt():
    from decimal import Decimal

    from app.services import kontrakt_disposition_service as dispo

    position = {
        "contract_no": "K-2026-002", "position_no": 1,
        "qty_contract": Decimal("100"), "ueberlieferung_erlaubt": True,
    }
    dispo.menge_pruefen(position, Decimal("100"), 50)


@pytest.mark.unit
def test_position_ohne_kontraktmenge_ist_nicht_pruefbar():
    """Keine kontrahierte Menge heisst nicht "beliebig viel"."""
    from decimal import Decimal

    from fastapi import HTTPException

    from app.services import kontrakt_disposition_service as dispo

    with pytest.raises(HTTPException) as fehler:
        dispo.menge_pruefen(
            {"contract_no": "K", "position_no": 1, "qty_contract": None,
             "ueberlieferung_erlaubt": False},
            Decimal("0"), 1,
        )
    assert fehler.value.status_code == 409


@pytest.mark.unit
def test_freigabe_ist_abgeleitet_und_keine_spalte():
    from app.services import kontrakt_disposition_service as dispo

    assert "freigabe" not in dispo.FELDER
    for zustand, erwartet in (
        ("OFFEN", False), ("FREIGEGEBEN", True), ("GELIEFERT", True), ("STORNIERT", False),
    ):
        assert dispo.als_dict({"status": zustand})["freigabe"] is erwartet


@pytest.mark.unit
def test_lesefehler_wird_nicht_zur_leeren_liste():
    """Vorher: ``if "relation" in err: return []``."""
    from app.services import kontrakt_disposition_service as dispo

    db = MagicMock()
    db.execute.side_effect = Exception('relation "kontrakt_dispositionen" does not exist')
    umgewandelt = dispo.nicht_lesbar(db, Exception("weg"), "Kontraktabrufe", "t-1")
    assert umgewandelt.status_code == 503
    assert "migration_hint" in str(umgewandelt.detail)
    db.rollback.assert_called_once()
