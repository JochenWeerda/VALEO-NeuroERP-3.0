"""FSX-MENGENMODELL — Endpunkte fuer die positionsbezogene Mengenzuordnung.

Der Zweck ist eine einzige Auskunft, die eine Belegmaske an der Position zeigen
koennen muss:

    100 dt geliefert · 60 dt berechnet · 40 dt offen

Das ist K5 des Ebene-1-Kriterienkatalogs. Ohne diese Auskunft in der Maske ist
das Mengenmodell zwar vorhanden, aber fuer den Sachbearbeiter nicht da — und
**Anzeigen ist nicht Aufloesen**, weshalb die Zuordnungen mitkommen, nicht nur
die Summen.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant_context import get_current_tenant_id
from app.domains.documents.allocation_models import (
    DocumentAllocation,
    DocumentAllocationSource,
)
from app.services.document_allocation_service import (
    AllocationError,
    DocumentAllocationService,
    NotDivisibleError,
    OverAllocationError,
    PositionRef,
    UnitNotConvertibleError,
)


class AllocationOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


router = APIRouter()


class AllocateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_document_type: str = Field(min_length=1, max_length=80)
    source_document_id: str = Field(min_length=1, max_length=120)
    source_line_id: str = Field(min_length=1, max_length=120)
    target_document_type: str = Field(min_length=1, max_length=80)
    target_document_id: str = Field(min_length=1, max_length=120)
    target_line_id: str = Field(min_length=1, max_length=120)
    quantity: Decimal = Field(gt=0)
    unit: str = Field(min_length=1, max_length=20)
    reason: Optional[str] = Field(default=None, max_length=80)
    note: Optional[str] = None
    user_id: Optional[str] = None


class ReleaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    #: Ohne Vorgabewert — die Entscheidung ist fachlich und wird nicht geraten.
    #: Warenrueckgabe gibt die Menge frei, ein Preisnachlass nicht.
    frees_quantity: bool


def _zahl(wert: Any) -> str:
    """Mengen als Zeichenkette ausgeben, ohne Nachkommaballast.

    Dezimalzahlen ueber JSON als Gleitkomma zu schicken, waere bei Mengen ein
    unnoetiges Risiko — die Anzeige rundet, der Wert nicht. Deshalb eine
    Zeichenkette.

    Die Spalte ist ``NUMERIC(18,6)``, also liefert die Datenbank ``40.000000``.
    Niemand will "40.000000 dt" lesen, deshalb werden nachlaufende Nullen
    entfernt. ``Decimal.normalize`` allein genuegt dafuer nicht: Aus 100 wird
    dabei ``1E+2``. Der zweite Schritt holt ganze Zahlen in die uebliche
    Schreibweise zurueck.
    """
    zahl = Decimal(str(wert)).normalize()
    if zahl == zahl.to_integral_value():
        zahl = zahl.quantize(Decimal(1))
    return format(zahl, "f")


def _fehler(fehler: AllocationError) -> HTTPException:
    """Fachliche Ablehnungen mit sprechendem Status und Grund."""
    if isinstance(fehler, UnitNotConvertibleError):
        status = 422
    elif isinstance(fehler, NotDivisibleError):
        status = 422
    elif isinstance(fehler, OverAllocationError):
        status = 409
    else:
        status = 400
    return HTTPException(status_code=status, detail=str(fehler))


@router.get(
    "/documents/{document_type}/{document_id}/allocations",
    response_model=AllocationOut,
    summary="Mengenstand aller Positionen eines Belegs",
)
def document_allocations(
    document_type: str,
    document_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Je Position: geliefert, berechnet, offen — plus die Zuordnungen selbst.

    Bewusst **eine** Abfrage je Beleg und nicht eine je Position: Eine Maske mit
    zwanzig Positionen soll nicht zwanzig Aufrufe ausloesen.
    """
    tenant_id = get_current_tenant_id()
    quellen = (
        db.query(DocumentAllocationSource)
        .filter(
            DocumentAllocationSource.tenant_id == tenant_id,
            DocumentAllocationSource.document_type == document_type,
            DocumentAllocationSource.document_id == document_id,
        )
        .order_by(DocumentAllocationSource.line_id.asc())
        .all()
    )
    if not quellen:
        return {
            "document_type": document_type,
            "document_id": document_id,
            "lines": [],
            "total": 0,
        }

    ids = [q.id for q in quellen]
    zuordnungen = (
        db.query(DocumentAllocation)
        .filter(
            DocumentAllocation.tenant_id == tenant_id,
            DocumentAllocation.source_id.in_(ids),
        )
        .order_by(DocumentAllocation.created_at.asc())
        .all()
    )
    je_quelle: dict[str, list[DocumentAllocation]] = {}
    for zuordnung in zuordnungen:
        je_quelle.setdefault(zuordnung.source_id, []).append(zuordnung)

    zeilen = []
    for quelle in quellen:
        gesamt = Decimal(str(quelle.quantity))
        belegt = Decimal(str(quelle.allocated_quantity))
        zeilen.append(
            {
                "line_id": quelle.line_id,
                "article_id": quelle.article_id,
                "unit": quelle.unit,
                "quantity": _zahl(gesamt),
                "allocated_quantity": _zahl(belegt),
                "open_quantity": _zahl(gesamt - belegt),
                "status": (
                    "offen" if belegt <= 0 else "vollstaendig" if belegt >= gesamt else "teilweise"
                ),
                "allocations": [
                    {
                        "id": z.id,
                        "target_document_type": z.target_document_type,
                        "target_document_id": z.target_document_id,
                        "target_line_id": z.target_line_id,
                        "quantity": _zahl(z.quantity),
                        "unit": z.unit,
                        # Die Eingabe bleibt erhalten, damit die Anzeige
                        # "2 Big Bag (= 12 dt)" moeglich ist.
                        "entered_quantity": (
                            _zahl(z.entered_quantity) if z.entered_quantity is not None else None
                        ),
                        "entered_unit": z.entered_unit,
                        "reason": z.reason,
                    }
                    for z in je_quelle.get(quelle.id, [])
                ],
            }
        )

    return {
        "document_type": document_type,
        "document_id": document_id,
        "lines": zeilen,
        "total": len(zeilen),
    }


@router.get(
    "/documents/{document_type}/{document_id}/allocation-origins",
    response_model=AllocationOut,
    summary="Herkunft der Mengen eines Belegs",
)
def document_allocation_origins(
    document_type: str,
    document_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Die Gegenrichtung: Woher kommen die Mengen **dieses** Belegs?

    Der Mengenstand oben blickt vom Lieferschein nach vorn — "60 dt berechnet".
    Eine Rechnung braucht den Blick zurueck: "Position 1: 60 dt aus
    Lieferschein LS-A/1". Beides ist dieselbe Zuordnung, von zwei Seiten
    gelesen, und beide Seiten werden gebraucht: Ohne die Herkunft steht in der
    Rechnung eine Menge ohne Nachweis.

    Auch hier **eine** Abfrage je Beleg statt einer je Position.
    """
    tenant_id = get_current_tenant_id()
    zuordnungen = (
        db.query(DocumentAllocation, DocumentAllocationSource)
        .join(
            DocumentAllocationSource,
            DocumentAllocation.source_id == DocumentAllocationSource.id,
        )
        .filter(
            DocumentAllocation.tenant_id == tenant_id,
            DocumentAllocation.target_document_type == document_type,
            DocumentAllocation.target_document_id == document_id,
        )
        .order_by(DocumentAllocation.target_line_id.asc(), DocumentAllocation.created_at.asc())
        .all()
    )

    je_zeile: dict[str, list[dict[str, Any]]] = {}
    for zuordnung, quelle in zuordnungen:
        je_zeile.setdefault(zuordnung.target_line_id, []).append(
            {
                "id": zuordnung.id,
                "source_document_type": quelle.document_type,
                "source_document_id": quelle.document_id,
                "source_line_id": quelle.line_id,
                "article_id": quelle.article_id,
                "quantity": _zahl(zuordnung.quantity),
                "unit": zuordnung.unit,
                "entered_quantity": (
                    _zahl(zuordnung.entered_quantity)
                    if zuordnung.entered_quantity is not None
                    else None
                ),
                "entered_unit": zuordnung.entered_unit,
                "reason": zuordnung.reason,
            }
        )

    zeilen = [
        {
            "line_id": line_id,
            "quantity": _zahl(sum(Decimal(h["quantity"]) for h in herkuenfte)),
            "unit": herkuenfte[0]["unit"],
            "origins": herkuenfte,
        }
        for line_id, herkuenfte in je_zeile.items()
    ]

    return {
        "document_type": document_type,
        "document_id": document_id,
        "lines": zeilen,
        "total": len(zeilen),
    }


@router.post(
    "/allocations",
    response_model=AllocationOut,
    status_code=201,
    summary="Teilmenge einer Position zuordnen",
)
def allocate(
    body: AllocateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    tenant_id = get_current_tenant_id()
    service = DocumentAllocationService(db, tenant_id)
    try:
        ergebnis = service.allocate(
            PositionRef(body.source_document_type, body.source_document_id, body.source_line_id),
            PositionRef(body.target_document_type, body.target_document_id, body.target_line_id),
            body.quantity,
            body.unit,
            reason=body.reason,
            note=body.note,
            user_id=body.user_id,
        )
    except AllocationError as fehler:
        db.rollback()
        raise _fehler(fehler) from fehler
    db.commit()
    return {
        "allocation_id": ergebnis.allocation_id,
        "quantity": _zahl(ergebnis.quantity),
        "unit": ergebnis.unit,
        "open_quantity": _zahl(ergebnis.remaining),
        "status": ergebnis.status,
    }


@router.post(
    "/allocations/{allocation_id}/release",
    response_model=AllocationOut,
    summary="Zuordnung loesen",
)
def release(
    allocation_id: str,
    body: ReleaseRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Eine Zuordnung loesen; ``frees_quantity`` entscheidet ueber die Menge.

    Es gibt bewusst keinen Vorgabewert: Eine Gutschrift kann Warenrueckgabe sein
    — dann wird die Menge wieder berechenbar — oder Preisnachlass, dann nicht.
    """
    tenant_id = get_current_tenant_id()
    service = DocumentAllocationService(db, tenant_id)
    try:
        ergebnis = service.release(allocation_id, frees_quantity=body.frees_quantity)
    except AllocationError as fehler:
        db.rollback()
        raise _fehler(fehler) from fehler
    db.commit()
    return {
        "allocation_id": ergebnis.allocation_id,
        "released_quantity": _zahl(ergebnis.quantity),
        "unit": ergebnis.unit,
        "open_quantity": _zahl(ergebnis.remaining),
        "status": ergebnis.status,
        "freed": body.frees_quantity,
    }
