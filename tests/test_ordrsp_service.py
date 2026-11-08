"""ORDRSP lesen und gegen die Bestellung abgleichen — reiner Dienst, ohne Datenbank."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.services.ordrsp_service import OrdrspFehler, abgleich, abweichungstext, parse_ordrsp

pytestmark = pytest.mark.unit

NACHRICHT = (
    "UNA:+.? '"
    "UNB+UNOC:3+4000000000001:14+4000000000002:14+261020:0800+77'"
    "UNH+1+ORDRSP:D:96A:UN:EAN005'"
    "BGM+231+AB-2026-0815+4'"
    "DTM+137:20261020:102'"
    "RFF+ON:B-1001'"
    "CUX+2:EUR:9'"
    "LIN+1+5+4012345000017:EN'"
    "PIA+1+WEIZ-A12:SA'"
    "QTY+21:100'"
    "PRI+AAA:24.50'"
    "LIN+2+3+4012345000024:EN'"
    "PIA+1+RAPS-00:SA'"
    "QTY+21:40'"
    "PRI+AAA:52.00'"
    "DTM+2:20261112:102'"
    "LIN+3+7+4012345000031:EN'"
    "QTY+21:0'"
    "UNS+S'"
    "MOA+79:4530.00'"
    "UNT+19+1'"
    "UNZ+1+77'"
)

BESTELLUNG = [
    {"pos_nr": 1, "artikel_nr": "4012345000017", "lieferanten_artnr": "WEIZ-A12", "menge": Decimal("100"),
     "einzelpreis": Decimal("24.50"), "lieferdatum": date(2026, 11, 5)},
    {"pos_nr": 2, "artikel_nr": "4012345000024", "lieferanten_artnr": "RAPS-00", "menge": Decimal("50"),
     "einzelpreis": Decimal("51.00"), "lieferdatum": date(2026, 11, 5)},
    {"pos_nr": 3, "artikel_nr": "4012345000031", "lieferanten_artnr": None, "menge": Decimal("10"),
     "einzelpreis": Decimal("9.00"), "lieferdatum": None},
    {"pos_nr": 4, "artikel_nr": "4012345000048", "lieferanten_artnr": None, "menge": Decimal("5"),
     "einzelpreis": Decimal("3.00"), "lieferdatum": None},
]


def test_kopf_und_positionen_werden_gelesen():
    antwort = parse_ordrsp(NACHRICHT)
    assert (antwort.ab_nummer, antwort.bestellnummer, antwort.funktion) == ("AB-2026-0815", "B-1001", "geaendert")
    assert antwort.datum == date(2026, 10, 20)
    assert antwort.waehrung == "EUR" and antwort.gesamtbetrag == Decimal("4530.00")
    assert [p.aktion for p in antwort.positionen] == ["angenommen", "geaendert", "abgelehnt"]
    zweite = antwort.positionen[1]
    assert (zweite.artikel, zweite.lieferanten_artnr, zweite.menge, zweite.preis, zweite.lieferdatum) == \
        ("4012345000024", "RAPS-00", Decimal("40"), Decimal("52.00"), date(2026, 11, 12))


def test_abgleich_nennt_jede_abweichung():
    arten = {(a["art"], a["position"]) for a in abgleich(BESTELLUNG, parse_ordrsp(NACHRICHT))}
    assert arten == {
        ("menge", "4012345000024"), ("preis", "4012345000024"), ("termin", "4012345000024"),
        ("abgelehnt", "4012345000031"), ("nicht_bestaetigt", "4012345000048"),
    }


def test_unveraenderte_bestaetigung_hat_keine_abweichung():
    antwort = parse_ordrsp(NACHRICHT.split("LIN+2")[0] + "UNT+9+1'")
    assert abgleich(BESTELLUNG[:1], antwort) == []
    assert abweichungstext([]) is None


def test_freigabezeichen_und_zusaetzliche_position():
    roh = ("UNH+1+ORDRSP:D:96A:UN'BGM+231+AB?+1+29'RFF+ON:B-9'LIN+1+5+X-1:EN'QTY+21:2'UNT+6+1'")
    antwort = parse_ordrsp(roh)
    assert antwort.ab_nummer == "AB+1" and antwort.funktion == "angenommen"
    assert abgleich([], antwort) == [{"art": "zusaetzlich", "position": "X-1", "bestaetigt": "2"}]
    assert "nicht bestellt" in abweichungstext(abgleich([], antwort))


@pytest.mark.parametrize("roh,grund", [
    ("", "leer"),
    ("UNH+1+ORDERS:D:96A:UN'BGM+220+1'", "ORDRSP"),
    ("UNH+1+ORDRSP:D:96A:UN'RFF+ON:B-1'", "BGM"),
    ("UNH+1+ORDRSP:D:96A:UN'BGM+231+AB-1'", "RFF"),
    ("UNH+1+ORDRSP:D:96A:UN'BGM+231+AB-1'RFF+ON:B-1'LIN+1++A:EN'QTY+21:viel'", "Zahl"),
])
def test_unlesbare_nachrichten_werden_abgewiesen(roh, grund):
    with pytest.raises(OrdrspFehler, match=grund):
        parse_ordrsp(roh)
