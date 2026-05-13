"""Service layer for procurement order management (Einkauf Bestellungen)."""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models.einkauf_models import (
    EinkaufBestellung,
    EinkaufBestellungPosition,
    EinkaufBestellvorschlag,
)

logger = logging.getLogger(__name__)

VALID_ORDER_STATUSES = {"entwurf", "offen", "bestaetigt", "teilgeliefert", "abgeschlossen", "storniert"}


class ProcurementService:
    """Encapsulates Einkauf order creation, status transitions, and queries."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── queries ───────────────────────────────────────────────────────────────

    def get_order_by_id(self, order_id: str) -> EinkaufBestellung:
        obj = (
            self.db.query(EinkaufBestellung)
            .filter(
                EinkaufBestellung.id == order_id,
                EinkaufBestellung.tenant_id == self.tenant_id,
            )
            .first()
        )
        if obj is None:
            raise EntityNotFoundError("EinkaufBestellung", order_id)
        return obj

    def list_orders(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        lieferant_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Tuple[List[EinkaufBestellung], int]:
        q = self.db.query(EinkaufBestellung).filter(
            EinkaufBestellung.tenant_id == self.tenant_id
        )
        if status:
            q = q.filter(EinkaufBestellung.status == status)
        if lieferant_id:
            q = q.filter(EinkaufBestellung.lieferant_id == lieferant_id)
        if date_from:
            q = q.filter(EinkaufBestellung.bestelldatum >= date_from)
        if date_to:
            q = q.filter(EinkaufBestellung.bestelldatum <= date_to)
        total = q.count()
        items = (
            q.order_by(EinkaufBestellung.bestelldatum.desc())
            .offset(skip).limit(limit).all()
        )
        return items, total

    def list_positions(self, order_id: str) -> List[EinkaufBestellungPosition]:
        return (
            self.db.query(EinkaufBestellungPosition)
            .filter(EinkaufBestellungPosition.bestellung_id == order_id)
            .order_by(EinkaufBestellungPosition.position_nummer)
            .all()
        )

    # ── mutations ─────────────────────────────────────────────────────────────

    def create_order(
        self,
        lieferant_id: str,
        bestelldatum: date,
        positionen: List[Dict[str, Any]],
        bestellnummer: Optional[str] = None,
        bemerkung: Optional[str] = None,
    ) -> EinkaufBestellung:
        if not positionen:
            raise ValidationFailedError("Bestellung muss mindestens eine Position enthalten")

        order = EinkaufBestellung(
            id=uuid7(),
            tenant_id=self.tenant_id,
            lieferant_id=lieferant_id,
            bestelldatum=bestelldatum,
            bestellnummer=bestellnummer or f"PO-{uuid7()[:8].upper()}",
            status="entwurf",
            bemerkung=bemerkung,
        )
        self.db.add(order)
        self.db.flush()

        for idx, pos in enumerate(positionen, start=1):
            menge = Decimal(str(pos.get("menge", 0)))
            einzelpreis = Decimal(str(pos.get("einzelpreis", 0)))
            position = EinkaufBestellungPosition(
                id=uuid7(),
                bestellung_id=order.id,
                tenant_id=self.tenant_id,
                position_nummer=idx,
                artikel_id=pos.get("artikel_id"),
                bezeichnung=pos.get("bezeichnung", ""),
                menge=menge,
                einheit=pos.get("einheit", "t"),
                einzelpreis=einzelpreis,
                gesamtpreis=menge * einzelpreis,
            )
            self.db.add(position)

        self.db.commit()
        self.db.refresh(order)
        logger.info("Created EinkaufBestellung %s / %s", order.id, order.bestellnummer)
        return order

    def transition_status(self, order_id: str, new_status: str) -> EinkaufBestellung:
        if new_status not in VALID_ORDER_STATUSES:
            raise ValidationFailedError(f"Ungültiger Status: {new_status}")
        order = self.get_order_by_id(order_id)
        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        return order

    def cancel_order(self, order_id: str, grund: Optional[str] = None) -> EinkaufBestellung:
        order = self.get_order_by_id(order_id)
        if order.status == "storniert":
            return order
        if order.status == "abgeschlossen":
            raise ValidationFailedError("Abgeschlossene Bestellungen können nicht storniert werden")
        order.status = "storniert"
        if grund and hasattr(order, "storno_grund"):
            order.storno_grund = grund
        self.db.commit()
        self.db.refresh(order)
        return order

    # ── Bestellvorschlag ──────────────────────────────────────────────────────

    def get_vorschlag(self, vorschlag_id: str) -> EinkaufBestellvorschlag:
        obj = (
            self.db.query(EinkaufBestellvorschlag)
            .filter(
                EinkaufBestellvorschlag.id == vorschlag_id,
                EinkaufBestellvorschlag.tenant_id == self.tenant_id,
            )
            .first()
        )
        if obj is None:
            raise EntityNotFoundError("EinkaufBestellvorschlag", vorschlag_id)
        return obj

    def convert_vorschlag_to_order(self, vorschlag_id: str) -> EinkaufBestellung:
        """Create a draft order from a procurement suggestion."""
        vorschlag = self.get_vorschlag(vorschlag_id)
        positionen = [
            {
                "artikel_id": pos.artikel_id,
                "bezeichnung": getattr(pos, "bezeichnung", ""),
                "menge": float(pos.vorschlag_menge or 0),
                "einheit": getattr(pos, "einheit", "t"),
                "einzelpreis": float(pos.einstandspreis or 0),
            }
            for pos in getattr(vorschlag, "positionen", [])
        ]
        order = self.create_order(
            lieferant_id=vorschlag.lieferant_id,
            bestelldatum=date.today(),
            positionen=positionen,
            bemerkung=f"Aus Bestellvorschlag {vorschlag_id}",
        )
        vorschlag.status = "umgewandelt"
        self.db.commit()
        return order
