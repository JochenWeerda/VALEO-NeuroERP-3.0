"""Doppelwiegung auf dem kanonischen Wiegeschein.

Der Doppelwiegungsweg schrieb `domain_agrar.wiegungen` — eine Tabelle, die keine
Migration anlegt. Hier steht, was stattdessen gilt: Geschrieben wird
`domain_inventory.weighing_tickets`, das Rueckgrat, auf das die
Rueckverfolgbarkeit zeigt.

Grundlage: MessEG (eine von Hand eingetragene Masse ist keine geeichte Messung),
GoBD Rz. 30 ff. (Nachvollziehbarkeit des Belegs). Siehe
``docs/quality-assurance/wiegung-kanonisch-20261005.md``.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

WIEGESCHEINE = "domain_inventory.weighing_tickets"

#: Zielscheintyp -> Richtung. `EL` ist ein Eingangslieferschein (Ware kommt),
#: `VL` ein Verkaufslieferschein (Ware geht). Die Rueckverfolgbarkeit kennt nur
#: `in` und `out`; ein dritter Wert liesse die Wiegung aus der Kette fallen.
RICHTUNG_JE_ZIELSCHEIN = {"EL": "in", "VL": "out"}

#: Deckungsgleich mit ``ck_wiegung_richtung``.
RICHTUNGEN = ("in", "out")

FELDER = (
    "id, ticket_number, tenant_id, scale_id, vehicle_plate, gross_weight, "
    "tare_weight, net_weight, weighing_date, status, direction, reference_doc, "
    "first_weighing_at, second_weighing_at, gosse, muster_nr, handwiegung, "
    "ident_nr, disposition_nr, charge_nr, article_id, contract_id, notes, created_at"
)

ZEITFELDER = (
    "weighing_date",
    "first_weighing_at",
    "second_weighing_at",
    "created_at",
)

GEWICHTSFELDER = ("gross_weight", "tare_weight", "net_weight")

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (wiegung_kanonisch_20261005)"
}


def als_dict(row: Any) -> dict:
    """Eine Datenbankzeile als Abbildung mit ISO-Zeitpunkten und Gleitkommazahlen."""
    d = dict(row)
    for schluessel in ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    for schluessel in GEWICHTSFELDER:
        if d.get(schluessel) is not None:
            d[schluessel] = float(d[schluessel])
    return d


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler auf einem Wiegeschein ist kein leerer Wiegeschein.

    Der Wiegeschein ist der Beleg der abgerechneten Menge. "Nicht gefunden" und
    "nicht lesbar" sind zwei verschiedene Aussagen, und nur eine davon darf eine
    Rechnung aufhalten.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def netto_aus_doppelwiegung(
    brutto: Optional[float], tara: Optional[float], netto: Optional[float]
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Brutto, Tara, Netto — in dieser Reihenfolge und ohne Absolutbetrag.

    Vorher: ``netto = abs(wiegung1 - wiegung2)``. Der Absolutbetrag verdeckt den
    Vorzeichenfehler. Eine Tara schwerer als das Brutto ist ein Messfehler oder
    eine Verwechslung der beiden Eingaben; daraus ein positives Nettogewicht zu
    machen heisst, auf einem Messfehler abzurechnen.

    Ist nur ein Netto angegeben (Handwiegung, Fremdwaage), wird es uebernommen —
    dann gibt es keine zwei Messungen, aus denen man es nachrechnen koennte.
    """
    if brutto is not None and tara is not None:
        if tara >= brutto:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Tara {tara} kg ist nicht kleiner als Brutto {brutto} kg. "
                    "Das ergibt kein Nettogewicht — sind die beiden Waegungen "
                    "vertauscht?"
                ),
            )
        return brutto, tara, round(brutto - tara, 3)
    if netto is not None:
        if netto <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"Ein Nettogewicht von {netto} kg ist keine Liefermenge.",
            )
        return brutto, tara, netto
    raise HTTPException(
        status_code=422,
        detail=(
            "Eine Wiegung braucht zwei Waegungen (Brutto und Tara) oder ein "
            "ausgewiesenes Nettogewicht. Ohne Gewicht ist der Wiegeschein kein Beleg."
        ),
    )


def richtung(zielschein_typ: Optional[str]) -> str:
    """Die Richtung aus dem Zielscheintyp. Unbekannt ist ein Fehler, kein Standard.

    Ein stillschweigendes ``in`` haette eine Verkaufslieferung als Zugang in die
    Rueckverfolgbarkeit gestellt.
    """
    if not zielschein_typ:
        return "in"
    schluessel = zielschein_typ.strip().upper()
    if schluessel in RICHTUNGEN:
        return schluessel
    if schluessel not in RICHTUNG_JE_ZIELSCHEIN:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Zielscheintyp {zielschein_typ!r} ist unbekannt. Erlaubt: "
                f"{', '.join(sorted(RICHTUNG_JE_ZIELSCHEIN))} "
                "(EL = Eingangslieferschein, VL = Verkaufslieferschein)."
            ),
        )
    return RICHTUNG_JE_ZIELSCHEIN[schluessel]


def naechste_scheinnummer(db: Session, tenant_id: str) -> str:
    """Die naechste Wiegescheinnummer des Mandanten.

    Gezaehlt wird die hoechste vergebene Nummer des Jahres, nicht die Anzahl der
    Zeilen: Ein geloeschter oder stornierter Schein gibt seine Nummer nicht frei.
    """
    jahr = db.execute(text("SELECT EXTRACT(YEAR FROM NOW())::int")).scalar()
    hoechste = db.execute(
        text(
            "SELECT MAX(SUBSTRING(ticket_number FROM '[0-9]+$')::int) "
            f"FROM {WIEGESCHEINE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND ticket_number ~ :muster"
        ),
        {"tid": tenant_id, "muster": f"^WS-{jahr}-[0-9]+$"},
    ).scalar()
    return f"WS-{jahr}-{(hoechste or 0) + 1:06d}"


def schreiben(
    db: Session,
    tenant_id: str,
    schein_id: str,
    scheinnummer: str,
    *,
    scale_id: Optional[str],
    vehicle_plate: Optional[str],
    brutto: Optional[float],
    tara: Optional[float],
    netto: Optional[float],
    richtung_: str,
    gosse: Optional[int],
    muster_nr: Optional[str],
    handwiegung: bool,
    ident_nr: Optional[str],
    disposition_nr: Optional[str],
    charge_nr: Optional[str],
    article_id: Optional[str],
    reference_doc: Optional[str],
    notes: Optional[str],
) -> None:
    """Schreibt den Wiegeschein auf das kanonische Rueckgrat.

    Beide Waegungszeitpunkte stehen auf jetzt: Der Weg nimmt sie in einem Zug
    entgegen. Ein erfundener Abstand waere eine Behauptung ueber den Ablauf.
    """
    db.execute(
        text(
            f"INSERT INTO {WIEGESCHEINE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, ticket_number, scale_id, vehicle_plate, "
            " gross_weight, tare_weight, net_weight, weighing_date, status, "
            " direction, reference_doc, first_weighing_at, second_weighing_at, "
            " gosse, muster_nr, handwiegung, ident_nr, disposition_nr, charge_nr, "
            " article_id, notes, created_at) "
            "VALUES (:id, :tid, :nr, :scale, :plate, :brutto, :tara, :netto, NOW(), "
            "        'closed', :richtung, :ref, NOW(), NOW(), :gosse, :muster, "
            "        :hand, :ident, :dispo, :charge, :artikel, :notes, NOW())"
        ),
        {
            "id": schein_id,
            "tid": tenant_id,
            "nr": scheinnummer,
            "scale": scale_id,
            "plate": vehicle_plate,
            "brutto": None if brutto is None else Decimal(str(brutto)),
            "tara": None if tara is None else Decimal(str(tara)),
            "netto": None if netto is None else Decimal(str(netto)),
            "richtung": richtung_,
            "ref": reference_doc,
            "gosse": gosse,
            "muster": muster_nr,
            "hand": handwiegung,
            "ident": ident_nr,
            "dispo": disposition_nr,
            "charge": charge_nr,
            "artikel": article_id,
            "notes": notes,
        },
    )


def holen(db: Session, tenant_id: str, schein_id: str) -> dict:
    """Einen Wiegeschein des Mandanten holen."""
    zeile = db.execute(
        text(
            f"SELECT {FELDER} FROM {WIEGESCHEINE} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": schein_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail=f"Wiegeschein {schein_id} nicht gefunden")
    return als_dict(zeile)
