"""Liest ein Endpunkt eine Tabelle, die es nicht gibt?

Die dritte und leiseste Ebene
-----------------------------

- `tests/test_mask_endpoint_inventory.py`: Gibt es die **Route**?
- `tests/test_mask_field_contracts.py`: Stimmen die **Schluessel**?
- hier: Gibt es die **Tabelle**?

Ein `SELECT` auf eine fehlende Tabelle wirft, das `except` faengt, und die
Maske zeigt **0,00** oder eine leere Liste. Eine Null sieht aus wie ein
Ergebnis. So meldete die Liquiditaetssicht „nichts offen", waehrend 18.000 EUR
offen waren, und das Management-Dashboard stimmte ihr zu — beide lasen leere
Parallel-Tabellen.

Zwei Zahlen statt einer: **lebend** heisst, eine Maske oder das Frontend ruft
eine Route dieser Datei auf — jemand sieht das Ergebnis. **Ruhend** heisst,
es gibt keinen Weg dorthin; ob dieser Code gebaut oder geloescht gehoert, ist
eine Produktentscheidung.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import pytest

from scripts.check_table_references import BASELINE_LEBEND, BASELINE_RUHEND, pruefe

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def ergebnis() -> dict:
    try:
        return pruefe()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")


def test_fehlende_tabellen_an_lebenden_wegen_nehmen_nicht_zu(ergebnis: dict) -> None:
    lebend = ergebnis["lebend"]
    beschreibung = ", ".join(f"{t} ({d[0]})" for t, d in lebend[:10])
    assert len(lebend) <= BASELINE_LEBEND, (
        f"Neue fehlende Tabelle an einem lebenden Weg: {beschreibung}"
    )


def test_fehlende_tabellen_in_ruhendem_code_nehmen_nicht_zu(ergebnis: dict) -> None:
    ruhend = ergebnis["ruhend"]
    beschreibung = ", ".join(f"{t} ({d[0]})" for t, d in ruhend[:10])
    assert len(ruhend) <= BASELINE_RUHEND, (
        f"Neue fehlende Tabelle in ruhendem Code: {beschreibung}"
    )


def test_die_belegkette_liest_vorhandene_tabellen(ergebnis: dict) -> None:
    """Die Dateien des Belegflusses duerfen **keinen** toten Verweis haben.

    Lieferschein, Rechnung, Sammelrechnung, Auftrag, Liquiditaet: Hier haengt
    Geld dran, und eine Null ist hier keine Auskunft, sondern ein Irrtum.
    """
    belegkette = {
        "sales_invoices.py",
        "sales_orders.py",
        "sales_offers.py",
        "collective_documents.py",
        "credit_management.py",
        "liquidity.py",
        "liquidity_planning.py",
        "xrechnung.py",
    }
    verstoesse = [
        f"{tabelle} in {', '.join(sorted(set(dateien) & belegkette))}"
        for tabelle, dateien in ergebnis["lebend"] + ergebnis["ruhend"]
        if set(dateien) & belegkette
    ]
    assert verstoesse == [], "Toter Tabellenverweis in der Belegkette: " + "; ".join(verstoesse)
