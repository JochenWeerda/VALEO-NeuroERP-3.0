"""Bruecken-Masken aus Abschnitt B haben einen Feldvertrag (P4)."""

from __future__ import annotations

import pytest

from scripts.check_field_contracts import pruefe

pytestmark = pytest.mark.unit

#: Native Bruecken-Masken, deren Entity-Kopf jetzt deklariert ist.
#: sales/invoice bleibt Claudes Rechnungsweg — nicht in dieser Liste.
BRUECKEN_KOEPFE = (
    "einkauf/anfrage",
    "einkauf/angebot",
    "einkauf/anlieferavis",
    "einkauf/auftragsbestaetigung",
    "einkauf/purchase-order",
    "einkauf/supplier",
    "finance/ap-invoice",
    "finance/bankkonto",
    "finance/debitor",
    "finance/kreditor",
    "futtermittel/mischfuttermittel",
    "qualitaet/reklamation",
)


@pytest.fixture(scope="module")
def ergebnis() -> dict:
    return pruefe()


def test_bruecken_koepfe_sind_pruefbar(ergebnis: dict) -> None:
    blind = {
        zeile.split(" -> ", 1)[0].rsplit("/", 1)[0]
        for zeile in ergebnis["nicht_pruefbar"]
    }
    fehlend = [screen for screen in BRUECKEN_KOEPFE if screen in blind]
    assert fehlend == [], (
        "Diese Bruecken-Masken haben noch keine deklarierte Antwort:\n  "
        + "\n  ".join(fehlend)
    )


#: Tabellen der drei Bruecken mit echten Rollout-Daten — nicht die leeren Stubs.
BRUECKEN_ZEILEN = (
    "einkauf/purchase-order/positionen/positionen",
    "einkauf/purchase-order/kommunikation/kommunikation",
    "einkauf/supplier/bestellungen/bestellungen",
    "einkauf/supplier/kontakte/kontakte",
    "finance/ap-invoice/positionen/positionen",
    "finance/ap-invoice/freigabe/freigabe",
)


def test_bruecken_zeilen_sind_pruefbar(ergebnis: dict) -> None:
    blind = {zeile.split(" -> ", 1)[0] for zeile in ergebnis["zeilen_nicht_pruefbar"]}
    fehlend = [quelle for quelle in BRUECKEN_ZEILEN if quelle in blind]
    assert fehlend == [], (
        "Diese Bruecken-Tabellen haben noch keine deklarierte Zeilenform:\n  "
        + "\n  ".join(fehlend)
    )
