"""Belegbezug einer Bestandsbewegung — kanonisch und historisch.

``domain_inventory.inventory_stock_movements`` fuehrt zwei Feldpaare fuer den
Belegbezug:

* kanonisch: ``source_document_type`` / ``source_document_id`` — was neue
  Buchungen schreiben.
* historisch: ``reference_type`` / ``reference_id`` — aus aelteren Migrationen;
  Bestandsdatenbanken tragen dort Werte.

Die Altfelder bleiben erhalten. Ein Bestandshauptbuch nach GoB muss den
urspruenglichen Belegbezug waehrend der Aufbewahrungsfrist lesbar halten; ein
Spalten-Drop wuerde genau das aufgeben. Ein bestimmter Spaltenname ist dagegen
nirgends vorgeschrieben.

Dieses Modul loest den Bezug einer Zeile auf. Zwei Regeln sind dabei nicht
verhandelbar:

1. **Paarweise.** Typ und Id stammen immer aus demselben Paar. Ein kanonischer
   Typ mit einer historischen Id waere eine erfundene Verknuepfung.
2. **Keine stille Umdeutung.** Sind beide Paare gefuellt und widersprechen sich,
   wird der Konflikt ausgewiesen, nicht aufgeloest. Welche Buchung richtig ist,
   entscheidet die Fachseite mit Beleg — nicht der Lesepfad.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

Herkunft = Literal["kanonisch", "historisch", "keiner"]


@dataclass(frozen=True)
class Belegbezug:
    """Aufgeloester Belegbezug einer Bewegungszeile."""

    typ: str | None
    id: str | None
    herkunft: Herkunft
    konflikt: bool = False
    #: Bei Konflikt beide Paare, damit die Klaerung nichts nachschlagen muss.
    kanonisch: tuple[str | None, str | None] | None = None
    historisch: tuple[str | None, str | None] | None = None

    @property
    def vorhanden(self) -> bool:
        return self.typ is not None or self.id is not None


def _paar(zeile: Mapping[str, Any], typ_feld: str, id_feld: str) -> tuple[str | None, str | None]:
    typ = zeile.get(typ_feld)
    ref = zeile.get(id_feld)
    return (
        str(typ) if typ not in (None, "") else None,
        str(ref) if ref not in (None, "") else None,
    )


def belegbezug(zeile: Mapping[str, Any]) -> Belegbezug:
    """Loest den Belegbezug einer Bewegungszeile auf.

    Args:
        zeile: Bewegungszeile als Mapping, etwa ``.mappings().first()``.

    Returns:
        Den aufgeloesten Bezug. ``herkunft`` sagt, aus welchem Feldpaar er
        stammt; ``konflikt`` ist True, wenn beide Paare gefuellt sind und sich
        widersprechen. In diesem Fall bleiben ``typ``/``id`` auf dem kanonischen
        Paar, aber der Aufrufer muss den Konflikt sichtbar machen, statt ihn zu
        uebergehen.
    """
    kanonisch = _paar(zeile, "source_document_type", "source_document_id")
    historisch = _paar(zeile, "reference_type", "reference_id")

    hat_kanonisch = any(wert is not None for wert in kanonisch)
    hat_historisch = any(wert is not None for wert in historisch)

    if hat_kanonisch and hat_historisch and kanonisch != historisch:
        return Belegbezug(
            typ=kanonisch[0],
            id=kanonisch[1],
            herkunft="kanonisch",
            konflikt=True,
            kanonisch=kanonisch,
            historisch=historisch,
        )
    if hat_kanonisch:
        return Belegbezug(typ=kanonisch[0], id=kanonisch[1], herkunft="kanonisch")
    if hat_historisch:
        # Historische Buchung: der Bezug steht nur im Altfeldpaar und bleibt
        # lesbar, ohne dass die Zeile umgeschrieben wird.
        return Belegbezug(typ=historisch[0], id=historisch[1], herkunft="historisch")
    return Belegbezug(typ=None, id=None, herkunft="keiner")
