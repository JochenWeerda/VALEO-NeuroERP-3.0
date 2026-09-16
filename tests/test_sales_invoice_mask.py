"""Die Bewertung hinter der Rechnungsmaske — datenbankfrei geprueft.

Die Maske wird nicht von Hand gebaut, sondern aus der ScreenDefinition
erzeugt. Was sie aussagt, entsteht deshalb hier: Ob eine berechnete Menge
durch ihre Zuordnungen belegt ist, ist eine fachliche Bewertung und kein
Anzeigekniff.

Geprueft wird genau diese Aussage, nicht das Aussehen.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pytest

from app.services.sales_invoice_mask import (
    belegart_label,
    bewerte_herkunft,
    herkunfts_zeilen,
    positions_zeilen,
    ungedeckte_positionen,
)

pytestmark = pytest.mark.unit


def herkunft(**overrides):
    eintrag = {
        "source_document_type": "delivery_note",
        "source_document_id": "LS-1",
        "source_line_id": "1",
        "quantity": Decimal("100"),
        "unit": "dt",
        "reason": "rechnung_aus_lieferschein",
    }
    eintrag.update(overrides)
    return eintrag


@dataclass
class Position:
    line_no: str = "1"
    article_number: str | None = "10001"
    description: str | None = "Weizen A"
    quantity: Decimal = Decimal("100")
    unit: str = "dt"
    unit_price: Decimal = Decimal("25")
    net_amount: Decimal = Decimal("2500")
    vat_rate: Decimal | None = Decimal("7")


def test_gedeckte_menge_heisst_belegt() -> None:
    deckung = bewerte_herkunft(Decimal("100"), "dt", [herkunft()])
    assert deckung.art == "belegt"
    assert deckung.quellen == 1


def test_mehrere_quellen_derselben_einheit_werden_addiert() -> None:
    deckung = bewerte_herkunft(
        Decimal("100"),
        "dt",
        [herkunft(quantity=Decimal("60")), herkunft(source_document_id="LS-2", quantity=Decimal("40"))],
    )
    assert deckung.art == "belegt"
    assert deckung.quellen == 2


def test_luecke_wird_als_zahl_benannt() -> None:
    """Der Fall, den sonst niemand bemerkt: Der Betrag stimmt fuer sich genommen."""
    deckung = bewerte_herkunft(Decimal("100"), "dt", [herkunft(quantity=Decimal("60"))])
    assert deckung.art == "teilweise"
    assert deckung.text == "40 dt ohne Zuordnung"


def test_rundungsrest_ist_keine_luecke() -> None:
    deckung = bewerte_herkunft(Decimal("100"), "dt", [herkunft(quantity=Decimal("99.9999"))])
    assert deckung.art == "belegt"


def test_einheiten_werden_nicht_umgerechnet() -> None:
    """100 kg und 1 dt sind dasselbe — das hier zu rechnen waere eine Erfindung."""
    deckung = bewerte_herkunft(Decimal("1"), "dt", [herkunft(quantity=Decimal("100"), unit="kg")])
    assert deckung.art == "unvergleichbar"


def test_ohne_zuordnung_ist_eine_eigene_aussage() -> None:
    deckung = bewerte_herkunft(Decimal("100"), "dt", [])
    assert deckung.art == "ohne"
    assert deckung.text == "Keine Herkunft"
    assert deckung.quellen == 0


def test_unlesbare_menge_wird_nicht_zu_null_gerechnet() -> None:
    deckung = bewerte_herkunft("k.A.", "dt", [herkunft()])
    assert deckung.art == "unvergleichbar"


def test_unbekannte_belegart_wird_nicht_verschwiegen() -> None:
    assert belegart_label("delivery_note") == "Lieferschein"
    assert belegart_label("frachtbrief") == "Beleg (frachtbrief)"


def test_positionszeile_traegt_ihren_deckungsstand() -> None:
    zeilen = positions_zeilen([Position()], {"1": [herkunft(quantity=Decimal("60"))]})
    assert zeilen[0]["quantity"] == 100.0
    assert zeilen[0]["herkunft"] == "40 dt ohne Zuordnung"
    assert zeilen[0]["herkunft_art"] == "teilweise"


def test_position_ohne_zuordnung_bleibt_als_befund_stehen() -> None:
    zeilen = positions_zeilen([Position(line_no="2")], {})
    assert zeilen[0]["herkunft_art"] == "ohne"
    assert ungedeckte_positionen(zeilen) == ["2"]


def test_belegte_positionen_erzeugen_keine_meldung() -> None:
    zeilen = positions_zeilen([Position()], {"1": [herkunft()]})
    assert ungedeckte_positionen(zeilen) == []


def test_herkunftstabelle_hat_eine_zeile_je_zuordnung() -> None:
    zeilen = herkunfts_zeilen(
        {
            "1": [herkunft(quantity=Decimal("60")), herkunft(source_document_id="LS-2", quantity=Decimal("40"))],
            "2": [herkunft(source_document_type="weighing_ticket", quantity=Decimal("10"))],
        }
    )
    assert [z["line_no"] for z in zeilen] == ["1", "1", "2"]
    assert zeilen[1]["source_document_id"] == "LS-2"
    assert zeilen[2]["source_type"] == "Wiegeschein"
