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
from typing import Any, Optional

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


def _belegtag() -> datetime:
    """Belegdatum ohne Angabe: der Geschaeftstag (00:00 UTC), nicht die Uhrzeit.

    Mit der Uhrzeit trug jede Wiederholung einen anderen Inhalt, und der Wiederholungsschutz von DocFlow lehnte
    denselben Auftrag als "anderer Inhalt" ab (09.11.2026).
    """
    from datetime import time

    from app.core.business_time import business_today

    return datetime.combine(business_today(), time(), tzinfo=timezone.utc)


def position_in_preiseinheit(*, artikel_nr: str, menge: Any, einheit: Optional[str], einzelpreis: Any,
                             preis_einheit: Optional[str], bezeichnung: Optional[str] = None) -> Position:
    """Position mit der Menge in der Einheit des Preises (Preis je 100 kg -> Menge in dt).

    Umrechnung nur ueber ``app/core/agrar_units.py``; ohne bekannten Faktor bleiben Menge und Einheit, wie sie sind.
    """
    from decimal import Decimal

    from app.core.agrar_units import globaler_faktor

    betrag, einheit_ = Decimal(str(menge or 0)), einheit or "t"
    preiseinheit = {"100kg": "dt", "je_100kg": "dt"}.get(str(preis_einheit or ""), preis_einheit)
    faktor = globaler_faktor(einheit_, preiseinheit) if preiseinheit else None
    if faktor is not None:
        betrag, einheit_ = (betrag * faktor).quantize(Decimal("0.0001")), preiseinheit
    return Position(artikel_nr=artikel_nr, bezeichnung=bezeichnung, menge=float(betrag), einheit=einheit_,
                    einzelpreis=float(Decimal(str(einzelpreis or 0))))


def lege_beleg_an(db: Session, tenant_id: str, belegart: str, *, partner_id: Optional[str],
                  positionen: list[Position], quelle: str, referenz: str, akteur: str,
                  entwurf_nr: Optional[str] = None, idempotenz: Optional[str] = None,
                  belegdatum: Optional[datetime] = None) -> str:
    """Legt einen DocFlow-Entwurf an und liefert seine Kennung. ``idempotenz`` wiederholt denselben Auftrag."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    from hashlib import sha256
    from uuid import uuid4

    variante = BELEGARTEN[belegart]
    # Die Entwurfsnummer ist ein Platzhalter (die Freigabe vergibt die Belegnummer), muss aber je Mandant und
    # Belegart eindeutig sein: Anhang statt eines zeitbasierten ID-Praefixes (uuid7 kollidierte). Mit
    # Wiederholungsschluessel folgt der Anhang aus dem Schluessel, damit die Wiederholung denselben Inhalt traegt.
    anhang = sha256(idempotenz.encode()).hexdigest()[:6] if idempotenz else uuid4().hex[:6]
    entwurf = f"{entwurf_nr or f'{quelle.upper()}-{referenz}'}"[:72] + f"-{anhang}"
    partner = {"supplier_id": partner_id} if variante.partnerrolle == "lieferant" else {"customer_id": partner_id}
    anfrage = DocflowCreateRequest(
        doc_type=belegart, doc_number=entwurf, status="draft",
        source_system=quelle[:40], source_ref=referenz[:80], currency="EUR",
        document_date=belegdatum or _belegtag(), idempotency_key=idempotenz, **partner,
        items=[DocflowLineInput(article_number=p.artikel_nr, description=p.bezeichnung, quantity=p.menge,
                                unit=p.einheit, unit_price=p.einzelpreis if variante.mit_preisen else 0,
                                tax_code=p.steuerschluessel)
               for p in positionen],
    )
    return DocflowService(db, tenant_id, akteur).create_document(anfrage)
