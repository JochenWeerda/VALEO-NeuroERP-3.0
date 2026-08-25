"""DOM-INV-005: kanonische Bewegungsrichtung fuer inventory_stock_movements.

In ``domain_inventory.inventory_stock_movements.movement_type`` schreiben
historisch sieben Vokabulare nebeneinander - englische Kuerzel aus den
Artikel-/Compat-Pfaden, deutsche Belegtypen aus der generischen Lagerbuchung,
Grossbuchstaben-Richtungen aus den Korrekturdiensten, dazu Einzelwerte aus
Wareneingang, Kasse, Kommissionierung und Bestandsvortrag.

Gelesen wurde das bis zu diesem Slice von sechs voneinander unabhaengigen
CASE-Ausdruecken, von denen jeder nur sein eigenes Vokabular kannte und fuer
alle anderen Werte still ein Vorzeichen geraten hat - mal ``ELSE 0`` (Zeile
verschwindet), mal ``ELSE quantity`` (jeder Abgang zaehlt positiv), mal
``ELSE -quantity`` (jeder Zugang zaehlt negativ). Dieselbe Ware hatte damit je
nach Endpunkt einen anderen Bestand.

Dieses Modul ist die eine Stelle, die die Richtung festlegt. Rohe SQL-Leser
holen sich das CASE-Fragment ueber :func:`direction_sql`, Python-Leser die Map
:data:`MOVEMENT_DIRECTION`.

Bewusst nicht Teil dieses Moduls: die geschriebenen Werte zu vereinheitlichen.
Die Bestandszeilen bleiben, wie sie geschrieben wurden; nur ihre Auswertung
wird einheitlich.
"""
from __future__ import annotations

from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

Direction = Literal[-1, 0, 1]

#: Bewegungstypen, die den Bestand erhoehen.
#:
#: ``inventur``, ``adjustment``, ``umbuchung`` und ``opening_balance`` stehen
#: hier, weil ihre Menge das Vorzeichen bereits selbst traegt
#: (``LagerbewegungIn``: "positiv = Zugang, negativ = Abgang"). Faktor +1 heisst
#: fuer sie: unveraendert uebernehmen, nicht "ist ein Zugang".
INBOUND_TYPES: tuple[str, ...] = (
    "in",
    "wareneingang",
    "umbuchung_eingang",
    "zugang",
    "einlagerung",
    "return",
    "retoure",
    "adjustment_in",
    "opening_balance",
    "inventur",
    "adjustment",
    "umbuchung",
)

#: Bewegungstypen, die den Bestand senken.
OUTBOUND_TYPES: tuple[str, ...] = (
    "out",
    "warenausgang",
    "umbuchung_ausgang",
    "abgang",
    "adjustment_out",
    "pick_out",
)

#: Bewegungstypen, die den Bestand nicht veraendern.
#:
#: ``reservation`` reserviert nur, es wird nichts bewegt.
#:
#: ``inventory_count`` ist der schwierige Fall: die mobile Zaehlung schreibt in
#: ``quantity`` den *absoluten* gezaehlten Bestand (``counted_qty``, laut ihrer
#: eigenen Validierung nie negativ), nicht die Differenz zum Buchbestand. Ein
#: absoluter Wert in einem Delta-Hauptbuch ist in keiner Richtung korrekt zu
#: summieren - er wuerde den Bestand verdoppeln, negieren oder verschwinden
#: lassen, je nachdem, welchen ``ELSE``-Zweig man erwischt. Bis geklaert ist,
#: wie eine Zaehlung in ein Delta uebersetzt gehoert, geht sie mit Faktor 0 ein.
#: Das ist nicht die Loesung, aber es ist die einzige Verrechnung, die nichts
#: Falsches behauptet.
NEUTRAL_TYPES: tuple[str, ...] = (
    "reservation",
    "inventory_count",
)

MOVEMENT_DIRECTION: dict[str, Direction] = {
    **{name: 1 for name in INBOUND_TYPES},
    **{name: -1 for name in OUTBOUND_TYPES},
    **{name: 0 for name in NEUTRAL_TYPES},
}

KNOWN_TYPES: frozenset[str] = frozenset(MOVEMENT_DIRECTION)


def direction_of(movement_type: str | None) -> Direction:
    """Richtung eines Bewegungstyps; unbekannte Typen ergeben 0.

    Unbekannt heisst hier bewusst 0 und nicht "raten": ein Vorzeichen zu
    erfinden ist genau der Fehler, den dieses Modul abloest. Damit ein
    unbekannter Typ nicht unsichtbar bleibt, gibt es
    :func:`unknown_movement_types`.
    """
    if not movement_type:
        return 0
    return MOVEMENT_DIRECTION.get(movement_type.strip().lower(), 0)


def signed_quantity(movement_type: str | None, quantity: float) -> float:
    """Bestandswirksame Menge einer Bewegung."""
    return direction_of(movement_type) * float(quantity or 0)


def _quoted(names: tuple[str, ...]) -> str:
    # Die Namen sind Modulkonstanten, keine Eingaben. Der Apostroph-Ersatz ist
    # trotzdem da, damit ein spaeter ergaenzter Wert nichts aufbrechen kann.
    return ", ".join("'" + name.replace("'", "''") + "'" for name in names)


def direction_sql(column: str = "movement_type", quantity: str = "quantity") -> str:
    """CASE-Fragment fuer die bestandswirksame Menge einer Bewegungszeile.

    Fuer rohe SQL-Aggregationen gedacht::

        SUM(%s) AS menge  %% direction_sql("sm.movement_type", "sm.quantity")

    ``column`` und ``quantity`` sind Spaltenausdruecke aus dem Aufrufer-Code,
    keine Nutzereingaben. Unbekannte Typen ergeben 0 statt eines geratenen
    Vorzeichens.
    """
    return (
        f"CASE"
        f" WHEN lower({column}) IN ({_quoted(INBOUND_TYPES)}) THEN {quantity}"
        f" WHEN lower({column}) IN ({_quoted(OUTBOUND_TYPES)}) THEN -{quantity}"
        f" ELSE 0 END"
    )


def inbound_sql(column: str = "movement_type", quantity: str = "quantity") -> str:
    """CASE-Fragment fuer den Zugangsanteil (immer positiv, sonst 0)."""
    return (
        f"CASE WHEN lower({column}) IN ({_quoted(INBOUND_TYPES)}) "
        f"THEN {quantity} ELSE 0 END"
    )


def outbound_sql(column: str = "movement_type", quantity: str = "quantity") -> str:
    """CASE-Fragment fuer den Abgangsanteil (immer positiv, sonst 0)."""
    return (
        f"CASE WHEN lower({column}) IN ({_quoted(OUTBOUND_TYPES)}) "
        f"THEN {quantity} ELSE 0 END"
    )


def unknown_movement_types(db: Session, tenant_id: str | None = None) -> dict[str, int]:
    """Bewegungstypen in der Datenbank, die diese Definition nicht kennt.

    Diagnosepfad fuer den Fall, dass ein Wert nicht als Literal im Repository
    steht, sondern aus Konfiguration oder Import kommt. Ergebnis ist
    ``{typ: anzahl}``; ein leeres Ergebnis heisst, dass jede Zeile in den
    Aggregaten mit einer bewussten Richtung gezaehlt wird.
    """
    sql = (
        "SELECT movement_type, COUNT(*) AS anzahl "
        "FROM domain_inventory.inventory_stock_movements "
        "WHERE lower(movement_type) NOT IN :known"
    )
    params: dict[str, object] = {"known": list(KNOWN_TYPES)}
    if tenant_id:
        sql += " AND tenant_id = :tenant_id"
        params["tenant_id"] = tenant_id
    sql += " GROUP BY movement_type ORDER BY anzahl DESC"

    from sqlalchemy import bindparam

    stmt = text(sql).bindparams(bindparam("known", expanding=True))
    return {row[0]: int(row[1]) for row in db.execute(stmt, params).all()}
