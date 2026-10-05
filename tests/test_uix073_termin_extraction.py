"""UIX-073: Deterministische Termin-Extraktion aus E-Mails.

Reine Unit-Tests (kein DB) fuer den Stufe-1-Extraktor: deutsche Datums-/
Zeitmuster, Bezugsobjekt-Heuristik, Idempotenz, Safety (Kandidaten sind nur
Vorschlaege, nie Auto-Confirm).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from app.services.crm_capture.termin_extraction import (
    BERLIN,
    build_source_key,
    extract_object_reference,
    extract_termine,
)

pytestmark = pytest.mark.unit

# Anker: Mittwoch, 08.07.2026, 09:00 Europe/Berlin.
ANCHOR = datetime(2026, 7, 8, 9, 0, tzinfo=BERLIN)
FIXTURES = Path(__file__).parent / "fixtures" / "mails"


def _starts(text: str, **kw):
    return extract_termine(text, received_at=ANCHOR, **kw)


def test_klare_anlieferung_mit_datum_zeit_und_bestellung():
    cands = _starts("Wir liefern am 12.07. um 14 Uhr an. Bestellung 7712.")
    assert len(cands) == 1
    c = cands[0]
    assert c.start.startswith("2026-07-12T14:00")
    assert c.all_day is False
    assert c.matched_object is not None
    assert c.matched_object.type == "purchase_order"
    assert c.matched_object.id == "7712"
    assert c.confidence >= 0.85


def test_wochentag_mit_uhrzeit_relativ_zum_anker():
    cands = _starts("Lieferung Montag 14 Uhr an Rampe 2.")
    assert len(cands) == 1
    start = datetime.fromisoformat(cands[0].start)
    assert start.weekday() == 0  # Montag
    assert start.date() > ANCHOR.date()
    assert start.hour == 14


def test_kw_ist_ganztags_am_montag():
    cands = _starts("Anlieferung in KW 29 geplant.")
    assert len(cands) == 1
    c = cands[0]
    assert c.all_day is True
    start = datetime.fromisoformat(c.start)
    assert start.weekday() == 0


def test_morgen_frueh_setzt_tageszeit_default():
    cands = _starts("Bitte morgen frueh anliefern.")
    assert len(cands) == 1
    start = datetime.fromisoformat(cands[0].start)
    assert start.date() == (ANCHOR.date().replace(day=9))
    assert start.hour == 8
    # relativer Anker senkt Konfidenz
    assert cands[0].confidence < 0.9


def test_zeitfenster_zwischen_x_und_y():
    cands = _starts("Am 15.07. zwischen 8 und 10 Uhr.")
    assert len(cands) == 1
    c = cands[0]
    assert c.start.startswith("2026-07-15T08:00")
    assert c.end is not None and c.end.startswith("2026-07-15T10:00")


def test_kein_termin_liefert_leer():
    assert _starts("Koennen Sie mir ein Angebot fuer Weizen senden?") == []


def test_mehrere_termine_in_einer_mail():
    text = "Anlieferung am 12.07. um 8 Uhr.\nZweite Fuhre am 13.07. um 15 Uhr."
    cands = _starts(text)
    assert len(cands) == 2
    assert {c.start[:10] for c in cands} == {"2026-07-12", "2026-07-13"}


def test_englisch_gemischt_wird_noch_erkannt():
    cands = _starts("Delivery on 14.07. at 9:30.")
    assert len(cands) == 1
    assert cands[0].start.startswith("2026-07-14T09:30")


def test_nur_uhrzeit_ohne_datum_wird_verworfen():
    assert _starts("Wir melden uns um 14 Uhr telefonisch.") == []


def test_kontrakt_und_lieferschein_referenzen():
    assert extract_object_reference("Betrifft Kontrakt K-123").type == "contract"
    assert extract_object_reference("Lieferschein LS-99 anbei").type == "delivery_note"
    ref = extract_object_reference("kein objekt", sender_domain="spedition-meyer.de")
    assert ref is not None and ref.type == "supplier"
    assert extract_object_reference("gar nichts hier") is None


def test_datum_ohne_jahr_rollt_ins_folgejahr_bei_vergangenheit():
    # 01.01. liegt vor dem Anker (08.07.) → naechstes Jahr.
    cands = _starts("Termin am 01.01. um 10 Uhr.")
    assert cands[0].start.startswith("2027-01-01")


def test_idempotenz_source_key_und_dedup():
    assert build_source_key("mail-1", 0) == "mail-1:0"
    assert build_source_key("mail-1", 1) == "mail-1:1"
    # Dieselbe Mail zweimal extrahiert → identische Startzeiten (keine Dubletten innerhalb).
    text = "Anlieferung am 12.07. um 14 Uhr.\nAnlieferung am 12.07. um 14 Uhr."
    cands = _starts(text)
    assert len(cands) == 1  # doppelter Slot dedupliziert


def test_safety_kandidaten_sind_nur_vorschlaege_keine_konfidenz_ueber_1():
    cands = _starts("Anlieferung am 12.07. um 14 Uhr.")
    for c in cands:
        assert 0.0 < c.confidence <= 1.0
        # Kandidat traegt keinen 'confirmed'-Status — reine Datenstruktur.
        assert not hasattr(c, "status")


def test_fixture_dateien_klar_und_kein_termin():
    klar = (FIXTURES / "klar_anlieferung.txt").read_text(encoding="utf-8")
    kein = (FIXTURES / "kein_termin.txt").read_text(encoding="utf-8")
    klar_cands = extract_termine(klar, received_at=ANCHOR)
    assert len(klar_cands) == 1
    assert klar_cands[0].matched_object.id == "7712"
    assert extract_termine(kein, received_at=ANCHOR) == []


def test_naive_received_at_wird_akzeptiert():
    naive = datetime(2026, 7, 8, 9, 0)
    cands = extract_termine("Lieferung am 12.07. um 14 Uhr.", received_at=naive)
    assert cands and cands[0].start.startswith("2026-07-12T14:00")
