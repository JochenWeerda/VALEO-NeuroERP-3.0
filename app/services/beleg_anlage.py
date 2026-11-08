"""Belege aus Fachwegen anlegen: immer in DocFlow (BELEG-052 Stufe 3, Nutzerentscheidung 08.11.2026).

Fachwege, die bisher direkt in einen Eigenspeicher schrieben (RFQ-Zuschlag -> ``domain_einkauf.bestellungen``,
Webshop -> ``domain_crm.sales_orders``, Sammellieferschein -> ``domain_sales.delivery_notes`` ...), legen ihren Beleg
hier an: als DocFlow-Entwurf der passenden Belegart, mit Herkunft (``source_system``/``source_ref``) und
Wiederholungsschutz. Freigeben, Umwandeln und Buchen laufen danach wie bei jedem Beleg ueber die Belegmaske.

Steuer: Ohne Steuerschluessel kommt kein Satz in den Beleg (keine Vorgabe 19 %); gebucht wird erst mit Schluessel
(``docs`` Steuerlogik eine Quelle).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.belegvertrag import BELEGARTEN


@dataclass(frozen=True)
class Position:
    artikel_nr: str
    menge: float
    einheit: Optional[str] = None
    bezeichnung: Optional[str] = None
    einzelpreis: float = 0
    steuerschluessel: Optional[str] = None


def lege_beleg_an(db: Session, tenant_id: str, belegart: str, *, partner_id: Optional[str],
                  positionen: list[Position], quelle: str, referenz: str, akteur: str,
                  entwurf_nr: Optional[str] = None, idempotenz: Optional[str] = None,
                  belegdatum: Optional[datetime] = None) -> str:
    """Legt einen DocFlow-Entwurf an und liefert seine Kennung. ``idempotenz`` wiederholt denselben Auftrag."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    variante = BELEGARTEN[belegart]
    partner = {"supplier_id": partner_id} if variante.partnerrolle == "lieferant" else {"customer_id": partner_id}
    anfrage = DocflowCreateRequest(
        doc_type=belegart, doc_number=entwurf_nr or f"{quelle.upper()}-{referenz}"[:80], status="draft",
        source_system=quelle[:40], source_ref=referenz[:80], currency="EUR",
        document_date=belegdatum or datetime.now(timezone.utc), idempotency_key=idempotenz, **partner,
        items=[DocflowLineInput(article_number=p.artikel_nr, description=p.bezeichnung, quantity=p.menge,
                                unit=p.einheit, unit_price=p.einzelpreis if variante.mit_preisen else 0,
                                tax_code=p.steuerschluessel)
               for p in positionen],
    )
    return DocflowService(db, tenant_id, akteur).create_document(anfrage)
