"""Die Rechnungsmaske als Daten — Kopf, Positionen und Herkunft fuer den Builder.

Warum das hier liegt und nicht in der Oberflaeche
-------------------------------------------------

Masken entstehen in VALEO ueber die Kette

    ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer

Die Maske baut also niemand von Hand. Was eine Maske zeigt, muss sie deshalb
als **Daten** bekommen. Die Aussage „diese Rechnungsposition ist nur teilweise
durch Zuordnungen belegt" ist eine fachliche Bewertung, kein Anzeigekniff — sie
gehoert hierher und nicht in eine Tabellenzelle aus TSX.

Die drei Aussagen, die sich unterscheiden muessen
-------------------------------------------------

``belegt``          Die Summe der Herkunftsmengen deckt die berechnete Menge.
``teilweise``       Sie deckt sie nicht. Die Luecke steht als Zahl da — das ist
                    der Fall, den sonst niemand bemerkt: Der Betrag der Position
                    stimmt fuer sich genommen, und nur die Summe der Zuordnungen
                    verraet, dass ein Teil der Menge unbelegt ist.
``ohne``            Gar keine Zuordnung. Kein Ladezustand, sondern eine Auskunft.
``unvergleichbar``  Quellen in abweichenden Einheiten. Hier wird **nicht**
                    umgerechnet: 100 kg und 1 dt sind dasselbe, aber das an
                    dieser Stelle zu rechnen hiesse, eine Umrechnung in der
                    Anzeige zu erfinden.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

#: Belegarten, deren Bezeichnung wir kennen. Ein unbekannter Schluessel wird
#: nicht verschwiegen, sondern mitgenannt — lieber "Beleg (weighing_ticket)"
#: als eine Zeile, die so tut, als gaebe es keine Quelle.
BELEGART: dict[str, str] = {
    "delivery_note": "Lieferschein",
    "sales_order": "Auftrag",
    "purchase_order": "Bestellung",
    "weighing_ticket": "Wiegeschein",
    "contract": "Kontrakt",
}

#: Rundungsrest, der keine Luecke ist: Mengen stehen mit sechs Nachkommastellen
#: in der Datenbank.
TOLERANZ = Decimal("0.001")


def belegart_label(typ: str) -> str:
    return BELEGART.get(typ, f"Beleg ({typ})")


@dataclass(frozen=True)
class Deckung:
    """Wie weit die berechnete Menge durch ihre Quellen belegt ist."""

    art: str
    text: str
    quellen: int


def _dezimal(wert: Any) -> Decimal | None:
    try:
        return Decimal(str(wert))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _zahl(wert: Decimal) -> str:
    """Zahl ohne unnoetige Nullen — die Anzeige rundet, der Wert nicht."""
    gekuerzt = wert.normalize()
    if gekuerzt == gekuerzt.to_integral_value():
        gekuerzt = gekuerzt.quantize(Decimal(1))
    return format(gekuerzt, "f")


def bewerte_herkunft(menge: Any, einheit: str, origins: list[dict[str, Any]]) -> Deckung:
    """Deckung einer Rechnungsposition durch ihre Zuordnungen."""
    if not origins:
        return Deckung("ohne", "Keine Herkunft", 0)

    summe = Decimal(0)
    for herkunft in origins:
        if str(herkunft.get("unit") or "") != einheit:
            return Deckung("unvergleichbar", "Abweichende Einheiten", len(origins))
        teil = _dezimal(herkunft.get("quantity"))
        if teil is None:
            return Deckung("unvergleichbar", "Abweichende Einheiten", len(origins))
        summe += teil

    berechnet = _dezimal(menge)
    if berechnet is None:
        return Deckung("unvergleichbar", "Abweichende Einheiten", len(origins))

    luecke = berechnet - summe
    if abs(luecke) < TOLERANZ:
        return Deckung("belegt", "Belegt", len(origins))
    return Deckung("teilweise", f"{_zahl(luecke)} {einheit} ohne Zuordnung", len(origins))


def lade_herkunft(db: Session, tenant_id: str, invoice_id: str) -> dict[str, list[dict[str, Any]]]:
    """Alle Zuordnungen der Rechnung, nach Positionsnummer gebuendelt.

    Eine Abfrage fuer den ganzen Beleg, nicht eine je Position: Eine Rechnung
    ueber zwanzig Positionen soll nicht zwanzig Abfragen ausloesen.
    """
    zeilen = (
        db.execute(
            text(
                """
                SELECT a.target_line_id AS line_no,
                       s.document_type AS source_document_type,
                       s.document_id AS source_document_id,
                       s.line_id AS source_line_id,
                       a.quantity AS quantity,
                       a.unit AS unit,
                       a.reason AS reason
                FROM domain_docs.doc_allocations a
                JOIN domain_docs.doc_allocation_sources s ON s.id = a.source_id
                WHERE a.tenant_id = :tenant_id
                  AND a.target_document_type = 'sales_invoice'
                  AND a.target_document_id = :invoice_id
                ORDER BY a.created_at ASC
                """
            ),
            {"tenant_id": tenant_id, "invoice_id": invoice_id},
        )
        .mappings()
        .all()
    )

    gebuendelt: dict[str, list[dict[str, Any]]] = {}
    for zeile in zeilen:
        gebuendelt.setdefault(str(zeile["line_no"]), []).append(dict(zeile))
    return gebuendelt


def positions_zeilen(
    positionen: list[Any], herkunft: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    """Die Positionstabelle der Maske — je Zeile auch ihr Deckungsstand."""
    zeilen: list[dict[str, Any]] = []
    for position in positionen:
        deckung = bewerte_herkunft(
            position.quantity, str(position.unit), herkunft.get(str(position.line_no), [])
        )
        zeilen.append(
            {
                "line_no": position.line_no,
                "article_number": position.article_number or "",
                "description": position.description or "",
                "quantity": float(position.quantity or 0),
                "unit": position.unit,
                "unit_price": float(position.unit_price or 0),
                "net_amount": float(position.net_amount or 0),
                "vat_rate": float(position.vat_rate) if position.vat_rate is not None else None,
                # Der Deckungsstand steht **an** der Position. Wer die Menge
                # sieht, sieht auch, ob sie belegt ist.
                "herkunft": deckung.text,
                "herkunft_art": deckung.art,
                "quellen": deckung.quellen,
            }
        )
    return zeilen


def herkunfts_zeilen(herkunft: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Die Herkunftstabelle: eine Zeile je Zuordnung, nicht je Position.

    Als eigene Tabelle, weil sie so sortierbar und filterbar ist — „welche
    Positionen kommen aus Lieferschein LS-7" ist damit eine Frage an die
    Tabelle und kein Aufklappen von zwanzig Zeilen.
    """
    zeilen: list[dict[str, Any]] = []
    for line_no in sorted(herkunft):
        for eintrag in herkunft[line_no]:
            zeilen.append(
                {
                    "line_no": line_no,
                    "source_type": belegart_label(str(eintrag["source_document_type"])),
                    "source_document_id": str(eintrag["source_document_id"]),
                    "source_line_id": str(eintrag["source_line_id"]),
                    "quantity": float(eintrag["quantity"] or 0),
                    "unit": str(eintrag["unit"] or ""),
                    "reason": str(eintrag["reason"] or ""),
                }
            )
    return zeilen


def ungedeckte_positionen(zeilen: list[dict[str, Any]]) -> list[str]:
    """Positionsnummern, deren Menge nicht vollstaendig belegt ist."""
    return [
        str(zeile["line_no"])
        for zeile in zeilen
        if zeile["herkunft_art"] in {"ohne", "teilweise"}
    ]
