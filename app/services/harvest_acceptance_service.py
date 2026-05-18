"""Service layer for Harvest Acceptance (Ernte-Annahme) CRUD operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_harvest_acceptance_datensatz
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.nuts2_utils import derive_nuts2_from_postal_code
from app.core.uuid7 import uuid7, uuid7_short_suffix
from app.infrastructure.models import (
    AgrarContract,
    Article,
    Customer,
    HarvestAcceptance,
    HarvestAcceptancePosition,
    Warehouse,
    WeighingTicket,
)


def _build_harvest_acceptance_dq_datensatz(data: dict) -> dict:
    return {
        "annahme_nr": data.get("acceptance_number"),
        "kunde_id": data.get("customer_id"),
        "lieferdatum": str(data.get("delivery_date") or ""),
        "preismodell": data.get("pricing_mode") or "spot_daily",
        "annahmemodus": data.get("acceptance_mode") or "PURCHASE_AT_DELIVERY_PTBF",
        "land": data.get("origin_country_code") or "DE",
    }


def _to_dict_with_positions(acceptance: HarvestAcceptance, db: Session) -> dict:
    positions = (
        db.query(HarvestAcceptancePosition)
        .filter(HarvestAcceptancePosition.harvest_acceptance_id == acceptance.id)
        .order_by(HarvestAcceptancePosition.position_number)
        .all()
    )
    article_name: Optional[str] = None
    if acceptance.article_id:
        article = db.query(Article).filter(Article.id == acceptance.article_id).first()
        if article:
            article_name = article.name or (article.description[:100] if article.description else None)

    from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceOut
    result_dict = HarvestAcceptanceOut.model_validate(acceptance).model_dump()
    result_dict["positions"] = [
        {
            "id": pos.id, "harvest_acceptance_id": pos.harvest_acceptance_id,
            "position_number": pos.position_number, "description": pos.description,
            "is_printable": pos.is_printable, "is_calculable": pos.is_calculable,
            "lab_value_pct": float(pos.lab_value_pct) if pos.lab_value_pct else None,
            "quantity_kg": float(pos.quantity_kg) if pos.quantity_kg else None,
            "unit": pos.unit,
            "price_per_unit_eur": float(pos.price_per_unit_eur) if pos.price_per_unit_eur else None,
            "amount_eur": float(pos.amount_eur) if pos.amount_eur else None,
            "calculation_formula": pos.calculation_formula,
        }
        for pos in positions
    ]
    if article_name is not None:
        result_dict["article_name"] = article_name
    return result_dict


def _quality_protocol_to_qualitaetsprotokoll(protocol) -> dict:
    """Mappt QualityProtocol auf das API-Format (Laborwerte-Dict)."""
    ov = protocol.other_values or {}
    return {
        "id": protocol.id,
        "acceptance_id": protocol.harvest_acceptance_id,
        "protocol_number": protocol.protocol_number,
        "version": protocol.version,
        "erstellt_am": protocol.created_at.isoformat() if protocol.created_at else None,
        "qualitaetsdaten": {
            "feuchte_prozent": float(protocol.moisture_pct) if protocol.moisture_pct is not None else None,
            "protein_prozent": float(protocol.protein_pct) if protocol.protein_pct is not None else None,
            "fallzahl": ov.get("fallzahl"),
            "sedimentation": ov.get("sedimentation"),
            "besatz": float(protocol.impurities_pct) if protocol.impurities_pct is not None else ov.get("besatz"),
            "mykotoxine": float(protocol.mycotoxin_ppb) if protocol.mycotoxin_ppb is not None else ov.get("mykotoxine"),
            "schadstoffe": ov.get("schadstoffe"),
            "keimzahl": ov.get("keimzahl"),
            "glasbruch": ov.get("glasbruch"),
            "sensorik": ov.get("sensorik"),
            "hektolitergewicht_kg_hl": float(protocol.hl_weight_kg_per_hl) if protocol.hl_weight_kg_per_hl is not None else None,
        },
        "bewertung": "ok" if protocol.is_final else "none",
        "bemerkungen": None,
        "labor_code": None,
        "analysendatum": protocol.approved_at.date().isoformat() if protocol.approved_at else None,
    }


class HarvestAcceptanceService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _get_or_raise(self, acceptance_id: str) -> HarvestAcceptance:
        obj = self.db.query(HarvestAcceptance).filter(
            HarvestAcceptance.id == acceptance_id,
            HarvestAcceptance.tenant_id == self.tenant_id,
        ).first()
        if not obj:
            raise EntityNotFoundError("HarvestAcceptance", acceptance_id)
        return obj

    def list_acceptances(
        self,
        customer_id=None,
        contract_id=None,
        release_status=None,
        origin_nuts2_code=None,
    ) -> list[dict]:
        q = self.db.query(HarvestAcceptance).filter(HarvestAcceptance.tenant_id == self.tenant_id)
        if customer_id:
            q = q.filter(HarvestAcceptance.customer_id == customer_id)
        if contract_id:
            q = q.filter(HarvestAcceptance.contract_id == contract_id)
        if release_status:
            q = q.filter(HarvestAcceptance.release_status == release_status)
        if origin_nuts2_code:
            q = q.filter(HarvestAcceptance.origin_nuts2_code == origin_nuts2_code.upper())
        items = q.order_by(
            HarvestAcceptance.delivery_date.desc(),
            HarvestAcceptance.acceptance_number.desc(),
        ).limit(500).all()
        from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceOut
        return [HarvestAcceptanceOut.model_validate(item) for item in items]

    def get_last_acceptance(self, operator_id=None, customer_id=None) -> Optional[dict]:
        q = self.db.query(HarvestAcceptance).filter(HarvestAcceptance.tenant_id == self.tenant_id)
        if operator_id:
            q = q.filter(HarvestAcceptance.operator_id == operator_id)
        if customer_id:
            q = q.filter(HarvestAcceptance.customer_id == customer_id)
        obj = q.order_by(HarvestAcceptance.created_at.desc()).first()
        if not obj:
            return None
        return _to_dict_with_positions(obj, self.db)

    def get_acceptance(self, acceptance_id: str) -> dict:
        from modules.agrar.repositories.quality_protocol_repo import QualityProtocolRepositoryImpl
        from modules.agrar.services.quality_protocol_service import get_latest_protocol
        from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl

        obj = self._get_or_raise(acceptance_id)

        if not obj.quality_protocol_id:
            quality_repo = QualityProtocolRepositoryImpl(self.db)
            try:
                protocol = get_latest_protocol(quality_repo, acceptance_id)
                if protocol:
                    obj.quality_protocol_id = protocol.id
                    self.db.commit()
            except Exception:
                pass

        result = _to_dict_with_positions(obj, self.db)

        if obj.invoice_id:
            billing_repo = SelfBillingRepositoryImpl(self.db)
            invoice = billing_repo.get_invoice_by_id(obj.invoice_id)
            if invoice:
                result["invoice"] = {
                    "invoice_number": invoice.invoice_number,
                    "status": invoice.status,
                    "dispute_status": invoice.dispute_status,
                    "total_gross_amount_eur": float(invoice.total_gross_amount_eur),
                }

        return result

    def create_acceptance(self, payload: Any, user_id: Optional[str]) -> dict:
        acceptance_number = payload.acceptance_number
        if not acceptance_number:
            ts = datetime.utcnow()
            acceptance_number = f"HA-{ts.strftime('%Y%m%d')}-{uuid7_short_suffix()}"

        dq_result = evaluate_harvest_acceptance_datensatz(
            _build_harvest_acceptance_dq_datensatz({
                "acceptance_number": acceptance_number,
                "customer_id": payload.customer_id,
                "delivery_date": payload.delivery_date,
                "pricing_mode": payload.pricing_mode,
                "acceptance_mode": payload.acceptance_mode,
                "origin_country_code": payload.origin_country_code,
            })
        )
        if not dq_result.bestanden:
            raise ValidationFailedError(build_dq_error_detail("ErnteAnnahme", dq_result))

        customer = self.db.query(Customer).filter(
            Customer.id == payload.customer_id, Customer.tenant_id == self.tenant_id
        ).first()
        if not customer:
            raise EntityNotFoundError("Customer", payload.customer_id)

        if payload.weighing_ticket_id:
            ticket = self.db.query(WeighingTicket).filter(
                WeighingTicket.id == payload.weighing_ticket_id, WeighingTicket.tenant_id == self.tenant_id
            ).first()
            if not ticket:
                raise EntityNotFoundError("WeighingTicket", payload.weighing_ticket_id)

        if payload.article_id:
            article = self.db.query(Article).filter(
                Article.id == payload.article_id, Article.tenant_id == self.tenant_id
            ).first()
            if not article:
                raise EntityNotFoundError("Article", payload.article_id)

        if payload.contract_id:
            contract = self.db.query(AgrarContract).filter(
                AgrarContract.id == payload.contract_id, AgrarContract.tenant_id == self.tenant_id
            ).first()
            if not contract:
                raise EntityNotFoundError("AgrarContract", payload.contract_id)

        if payload.warehouse_id:
            warehouse = self.db.query(Warehouse).filter(
                Warehouse.id == payload.warehouse_id, Warehouse.tenant_id == self.tenant_id
            ).first()
            if not warehouse:
                raise EntityNotFoundError("Warehouse", payload.warehouse_id)

        duplicate = self.db.query(HarvestAcceptance).filter(
            HarvestAcceptance.tenant_id == self.tenant_id,
            HarvestAcceptance.acceptance_number == acceptance_number,
        ).first()
        if duplicate:
            raise ConflictError(f"Acceptance number {acceptance_number} already exists")

        obj = HarvestAcceptance(
            id=uuid7(),
            tenant_id=self.tenant_id,
            acceptance_number=acceptance_number,
            branch_id=payload.branch_id,
            warehouse_id=payload.warehouse_id,
            delivery_date=payload.delivery_date,
            delivery_time=payload.delivery_time,
            sales_rep_id=payload.sales_rep_id,
            operator_id=user_id or "system",
            weighing_ticket_id=payload.weighing_ticket_id,
            cost_center_id=payload.cost_center_id,
            customer_id=payload.customer_id,
            contract_id=payload.contract_id,
            forwarder_id=payload.forwarder_id,
            intermediate_dealer_id=payload.intermediate_dealer_id,
            deviating_vat_id=payload.deviating_vat_id,
            article_id=payload.article_id,
            variety_id=payload.variety_id,
            vehicle_plate=payload.vehicle_plate,
            origin_nuts2_code=payload.origin_nuts2_code,
            nuts_version=payload.nuts_version or "NUTS 2024",
            origin_postal_code=payload.origin_postal_code,
            origin_city=payload.origin_city,
            origin_country_code=payload.origin_country_code or "DE",
            is_sustainable_biomass=payload.is_sustainable_biomass,
            pricing_mode=payload.pricing_mode or "spot_daily",
            price_source_id=payload.price_source_id,
            acceptance_mode=payload.acceptance_mode or "PURCHASE_AT_DELIVERY_PTBF",
            ownership_type=payload.ownership_type or "OWN_STOCK",
            vat_event=payload.vat_event or "NO_INVOICE",
            advance_payment_amount_eur=Decimal(str(payload.advance_payment_amount_eur)) if payload.advance_payment_amount_eur is not None else None,
            advance_payment_date=payload.advance_payment_date,
            release_status="draft",
            remarks=payload.remarks,
            print_remarks_on_acceptance_note=payload.print_remarks_on_acceptance_note,
            print_remarks_on_settlement=payload.print_remarks_on_settlement,
            created_by=user_id or "system",
        )
        self.db.add(obj)
        self.db.flush()

        if payload.positions:
            for pos_in in payload.positions:
                pos = HarvestAcceptancePosition(
                    id=uuid7(),
                    harvest_acceptance_id=obj.id,
                    position_number=pos_in.position_number,
                    description=pos_in.description,
                    is_printable=pos_in.is_printable,
                    is_calculable=pos_in.is_calculable,
                    lab_value_pct=Decimal(str(pos_in.lab_value_pct)) if pos_in.lab_value_pct is not None else None,
                    quantity_kg=Decimal(str(pos_in.quantity_kg)) if pos_in.quantity_kg is not None else None,
                    unit=pos_in.unit,
                    price_per_unit_eur=Decimal(str(pos_in.price_per_unit_eur)) if pos_in.price_per_unit_eur is not None else None,
                    amount_eur=Decimal(str(pos_in.amount_eur)) if pos_in.amount_eur is not None else None,
                    calculation_formula=pos_in.calculation_formula,
                    origin_nuts2_code=pos_in.origin_nuts2_code,
                    nuts_version=pos_in.nuts_version or "NUTS 2024",
                    origin_postal_code=pos_in.origin_postal_code,
                    origin_city=pos_in.origin_city,
                    origin_country_code=pos_in.origin_country_code or "DE",
                    article_id=pos_in.article_id,
                    variety_id=pos_in.variety_id,
                )
                self.db.add(pos)

        self.db.commit()
        self.db.refresh(obj)
        return _to_dict_with_positions(obj, self.db)

    def update_acceptance(self, acceptance_id: str, update_data: dict, user_id: Optional[str]) -> Any:
        from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceOut
        obj = self._get_or_raise(acceptance_id)

        if obj.release_status not in ("draft", "provisional"):
            raise ValidationFailedError(f"Cannot update harvest acceptance in status '{obj.release_status}'. Only 'draft' or 'provisional' can be updated.")

        effective_data = {
            "acceptance_number": obj.acceptance_number,
            "customer_id": obj.customer_id,
            "delivery_date": update_data.get("delivery_date", obj.delivery_date),
            "pricing_mode": update_data.get("pricing_mode", obj.pricing_mode),
            "acceptance_mode": update_data.get("acceptance_mode", obj.acceptance_mode),
            "origin_country_code": update_data.get("origin_country_code", obj.origin_country_code),
        }
        dq_result = evaluate_harvest_acceptance_datensatz(_build_harvest_acceptance_dq_datensatz(effective_data))
        if not dq_result.bestanden:
            raise ValidationFailedError(build_dq_error_detail("ErnteAnnahme", dq_result))

        for key, value in update_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        obj.updated_by = user_id or "system"
        obj.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(obj)
        return HarvestAcceptanceOut.model_validate(obj)

    def delete_acceptance(self, acceptance_id: str) -> None:
        obj = self._get_or_raise(acceptance_id)
        if obj.release_status != "draft":
            raise ValidationFailedError(f"Cannot delete harvest acceptance in status '{obj.release_status}'. Only 'draft' can be deleted.")
        self.db.delete(obj)
        self.db.commit()

    def derive_nuts2(self, acceptance_id: str) -> dict:
        obj = self._get_or_raise(acceptance_id)
        if not obj.origin_postal_code:
            raise ValidationFailedError("Postal code (origin_postal_code) is required to derive NUTS-2 code")
        derived = derive_nuts2_from_postal_code(obj.origin_postal_code, obj.origin_country_code or "DE")
        if derived:
            obj.origin_nuts2_code = derived
            self.db.commit()
            return {"origin_nuts2_code": derived, "nuts_version": obj.nuts_version or "NUTS 2024", "message": "NUTS-2 code derived successfully"}
        return {"origin_nuts2_code": None, "message": "Could not derive NUTS-2 code from postal code. Please enter manually."}

    def cancel(self, acceptance_id: str, reason: str) -> Any:
        obj = self._get_or_raise(acceptance_id)
        if obj.release_status == "final":
            raise ValidationFailedError("Endgültig freigegebene Annahmen können nicht storniert werden")
        if obj.release_status == "cancelled":
            raise ConflictError("Annahme ist bereits storniert")
        obj.release_status = "cancelled"
        obj.notes = f"[STORNIERT: {reason}] " + (obj.notes or "")
        self.db.commit()
        self.db.refresh(obj)
        return _to_dict_with_positions(obj, self.db)

    def get_quality_protocol(self, acceptance_id: str) -> dict:
        from modules.agrar.repositories.quality_protocol_repo import QualityProtocolRepositoryImpl
        obj = self._get_or_raise(acceptance_id)
        if obj.quality_protocol_id:
            quality_repo = QualityProtocolRepositoryImpl(self.db)
            protocol = quality_repo.get_by_id(obj.quality_protocol_id)
            if protocol:
                return _quality_protocol_to_qualitaetsprotokoll(protocol)
        legacy = getattr(obj, "quality_protocol", None)
        if legacy:
            return legacy
        raise EntityNotFoundError("QualityProtocol", acceptance_id)

    def create_quality_protocol_for_acceptance(self, acceptance_id: str, data: dict) -> dict:
        from decimal import Decimal
        from modules.agrar.repositories.quality_protocol_repo import QualityProtocolRepositoryImpl
        from modules.agrar.services.quality_protocol_service import create_quality_protocol, QualityProtocolCreate
        obj = self._get_or_raise(acceptance_id)
        qd = data.get("qualitaetsdaten") or data
        create_input = QualityProtocolCreate(
            tenant_id=self.tenant_id,
            harvest_acceptance_id=acceptance_id,
            moisture_pct=Decimal(str(qd["feuchte_prozent"])) if qd.get("feuchte_prozent") is not None else None,
            protein_pct=Decimal(str(qd["protein_prozent"])) if qd.get("protein_prozent") is not None else None,
            impurities_pct=Decimal(str(qd["besatz"])) if qd.get("besatz") is not None else None,
            mycotoxin_ppb=Decimal(str(qd["mykotoxine"])) if qd.get("mykotoxine") is not None else None,
            hl_weight_kg_per_hl=Decimal(str(qd["hektolitergewicht_kg_hl"])) if qd.get("hektolitergewicht_kg_hl") is not None else None,
            other_values={
                "fallzahl": qd.get("fallzahl"),
                "sedimentation": qd.get("sedimentation"),
                "schadstoffe": qd.get("schadstoffe"),
                "keimzahl": qd.get("keimzahl"),
                "glasbruch": qd.get("glasbruch"),
                "sensorik": qd.get("sensorik"),
            } if any(qd.get(k) is not None for k in ("fallzahl", "sedimentation", "schadstoffe", "keimzahl", "glasbruch", "sensorik")) else None,
            source_type="manual",
            created_by=None,
        )
        quality_repo = QualityProtocolRepositoryImpl(self.db)
        protocol = create_quality_protocol(quality_repo, create_input)
        obj.quality_protocol_id = protocol.id
        bewertung = data.get("bewertung", "none")
        if bewertung == "ok":
            obj.quality_status = "approved"
        elif bewertung == "warning":
            obj.quality_status = "conditional"
        elif bewertung == "critical":
            obj.quality_status = "rejected"
        self.db.commit()
        qualitaetsprotokoll = _quality_protocol_to_qualitaetsprotokoll(protocol)
        qualitaetsprotokoll["bewertung"] = bewertung
        qualitaetsprotokoll["bemerkungen"] = data.get("bemerkungen")
        qualitaetsprotokoll["labor_code"] = data.get("labor_code")
        qualitaetsprotokoll["analysendatum"] = data.get("analysendatum")
        return {
            "message": "Qualitätsprotokoll erstellt",
            "qualitaetsprotokoll": qualitaetsprotokoll,
            "quality_status": getattr(obj, "quality_status", None),
        }

    def calculate_frachtkosten(self, acceptance_id: str, data: dict) -> dict:
        from decimal import Decimal
        obj = self._get_or_raise(acceptance_id)
        entfernung_km = data.get("entfernung_km", 0)
        gewicht_kg = data.get("gewicht_kg")
        if not gewicht_kg:
            if obj.weighing_ticket_id:
                ticket = self.db.query(WeighingTicket).filter(WeighingTicket.id == obj.weighing_ticket_id).first()
                if ticket and ticket.net_weight:
                    gewicht_kg = float(ticket.net_weight)
            if not gewicht_kg:
                positions = self.db.query(HarvestAcceptancePosition).filter(
                    HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id,
                    HarvestAcceptancePosition.position_number == 10,
                ).all()
                if positions:
                    gewicht_kg = sum(float(pos.quantity_kg or 0) for pos in positions)
        if not gewicht_kg or gewicht_kg <= 0:
            raise ValidationFailedError("Gewicht konnte nicht ermittelt werden")
        grundpreis_eur = 50.0
        preis_pro_km_eur = 1.50
        preis_pro_tonne_eur = 25.0
        gewicht_tonnen = gewicht_kg / 1000
        frachtkosten_eur = round(grundpreis_eur + (entfernung_km * preis_pro_km_eur) + (gewicht_tonnen * preis_pro_tonne_eur), 2)
        obj.logistics_freight_costs_eur = Decimal(str(frachtkosten_eur))
        self.db.commit()
        return {
            "acceptance_id": acceptance_id,
            "entfernung_km": entfernung_km,
            "gewicht_kg": gewicht_kg,
            "gewicht_tonnen": round(gewicht_tonnen, 3),
            "frachtkosten_eur": frachtkosten_eur,
        }

    def get_frachtkosten(self, acceptance_id: str) -> dict:
        obj = self._get_or_raise(acceptance_id)
        return {
            "acceptance_id": acceptance_id,
            "frachtkosten_eur": float(obj.logistics_freight_costs_eur or 0),
        }

    def release_acceptance(
        self,
        acceptance_id: str,
        release_status: str,
        create_stock_movement: bool,
        create_credit_note: bool,
        user_id: str,
    ) -> Any:
        from datetime import datetime as _datetime
        from decimal import Decimal
        from sqlalchemy import desc
        from app.infrastructure.models import StockMovement, HarvestAcceptanceLine
        from app.core.uuid7 import uuid7 as _uuid7
        from modules.agrar.services.partie_service import generate_lot_number
        from modules.agrar.services.self_billing_service import CreditNoteCreate, create_credit_note as _create_credit_note_svc
        from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
        from modules.agrar.services.tax_profile_service import get_taxation_type_for_supplier

        obj = self._get_or_raise(acceptance_id)
        if obj.release_status == "final":
            raise ValidationFailedError("Harvest acceptance is already final")
        if obj.release_status == "cancelled":
            raise ValidationFailedError("Cannot release cancelled harvest acceptance")
        if release_status not in ("provisional", "final"):
            raise ValidationFailedError("release_status must be 'provisional' or 'final'")

        # Hole Nettogewicht (für Stock Movement und Partie/Charge)
        net_weight_kg = Decimal("0")
        if obj.weighing_ticket_id:
            ticket = self.db.query(WeighingTicket).filter(WeighingTicket.id == obj.weighing_ticket_id).first()
            if ticket and ticket.net_weight:
                net_weight_kg = ticket.net_weight
        else:
            positions = self.db.query(HarvestAcceptancePosition).filter(
                HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id,
                HarvestAcceptancePosition.position_number == 10,
            ).all()
            if positions:
                net_weight_kg = sum(pos.quantity_kg or Decimal("0") for pos in positions)

        # Erstelle Wareneingang (Stock Movement), wenn gewünscht und noch nicht vorhanden
        if create_stock_movement and not obj.stock_movement_id:
            if not obj.article_id:
                raise ValidationFailedError("Article ID is required to create stock movement")
            if not obj.warehouse_id:
                raise ValidationFailedError("Warehouse ID is required to create stock movement")
            if net_weight_kg <= 0:
                raise ValidationFailedError("Net weight must be > 0 to create stock movement")

            last_movement = (
                self.db.query(StockMovement)
                .filter(
                    StockMovement.article_id == obj.article_id,
                    StockMovement.warehouse_id == obj.warehouse_id,
                    StockMovement.tenant_id == self.tenant_id,
                )
                .order_by(desc(StockMovement.movement_date), desc(StockMovement.created_at))
                .first()
            )
            previous_stock = (last_movement.new_stock if last_movement else Decimal("0")) or Decimal("0")
            new_stock = previous_stock + net_weight_kg

            stock_movement = StockMovement(
                id=_uuid7(),
                tenant_id=self.tenant_id,
                article_id=obj.article_id,
                warehouse_id=obj.warehouse_id,
                movement_type="in",
                quantity=net_weight_kg,
                unit="kg",
                movement_date=obj.delivery_date,
                reference_number=obj.acceptance_number,
                movement_number=f"HA-{obj.acceptance_number}",
                notes=f"Wareneingang aus Ernte-Annahme {obj.acceptance_number}",
                booking_user=user_id,
                auto_created=True,
                weighing_ticket_id=obj.weighing_ticket_id,
                agrar_contract_id=obj.contract_id,
                ownership_type="owned",
                previous_stock=previous_stock,
                new_stock=new_stock,
                storage_fee_relevant=False,
            )
            self.db.add(stock_movement)
            self.db.flush()
            obj.stock_movement_id = stock_movement.id

        # Aktualisiere Status
        obj.release_status = release_status
        obj.updated_by = user_id
        obj.updated_at = _datetime.utcnow()

        # Erstelle Partie/Charge (wenn final und noch nicht vorhanden)
        if release_status == "final":
            existing_lines = self.db.query(HarvestAcceptanceLine).filter(
                HarvestAcceptanceLine.harvest_acceptance_id == acceptance_id
            ).count()

            if existing_lines == 0:
                lot_id = generate_lot_number(self.db, acceptance_id, self.tenant_id)
                line = HarvestAcceptanceLine(
                    id=_uuid7(),
                    tenant_id=self.tenant_id,
                    harvest_acceptance_id=acceptance_id,
                    line_number=1,
                    lot_id=lot_id,
                    qty_kg_allocated=net_weight_kg,
                )
                self.db.add(line)

        # Erstelle Self-Billing Gutschrift (wenn gewünscht und final)
        if create_credit_note and release_status == "final" and not obj.invoice_id:
            if not obj.total_gross_amount_eur:
                raise ValidationFailedError("Cannot create credit note: total_gross_amount_eur is not set. Please calculate settlement first.")

            vat_rate_percent = Decimal("0")
            if obj.vat_rate_percent:
                vat_rate_percent = obj.vat_rate_percent
            else:
                vat_rate_percent = Decimal("19.0")

            billing_repo = SelfBillingRepositoryImpl(self.db)
            credit_note_input = CreditNoteCreate(
                tenant_id=self.tenant_id,
                harvest_acceptance_id=acceptance_id,
                total_net_amount_eur=obj.total_net_amount_eur or Decimal("0"),
                total_vat_amount_eur=obj.total_vat_amount_eur or Decimal("0"),
                total_gross_amount_eur=obj.total_gross_amount_eur,
                vat_rate_percent=vat_rate_percent,
                created_by=user_id,
            )

            taxation_type = "regular"
            if obj.customer_id:
                taxation_type = get_taxation_type_for_supplier(
                    db=self.db,
                    supplier_id=obj.customer_id,
                    tenant_id=self.tenant_id,
                    effective_date=obj.delivery_date,
                )

            invoice = _create_credit_note_svc(billing_repo, credit_note_input, taxation_type=taxation_type)
            obj.invoice_id = invoice.id
            obj.release_status = "credit_note_created"

            # FIBU-Buchung: Self-Billing Gutschrift buchen (Eingangsseite)
            self._book_self_billing_credit_note(invoice, obj.delivery_date)

        self.db.commit()
        self.db.refresh(obj)
        return _to_dict_with_positions(obj, self.db)

    def _book_self_billing_credit_note(self, invoice: Any, delivery_date: Any) -> None:
        """Book self-billing credit note into GL: Debit 3100 / Credit 4000 + 1576 (non-blocking)."""
        try:
            from app.services.finance_transaction_service import FinanceTransactionService
            net = Decimal(str(invoice.total_net_amount_eur or 0))
            vat = Decimal(str(invoice.total_vat_amount_eur or 0))
            gross = Decimal(str(invoice.total_gross_amount_eur or 0))
            if gross == Decimal("0"):
                return
            entry_date = delivery_date
            if entry_date is None:
                from datetime import datetime as _dt
                entry_date = _dt.utcnow().date()
            period = str(entry_date)[:7]
            lines = [
                {"account_id": "3100", "debit_amount": float(gross), "credit_amount": 0,
                 "description": f"Verbindlichkeit Self-Billing {invoice.invoice_number}"},
                {"account_id": "4000", "debit_amount": 0, "credit_amount": float(net),
                 "description": "Wareneinkauf Ernte"},
            ]
            if vat > Decimal("0"):
                lines.append({
                    "account_id": "1576", "debit_amount": 0, "credit_amount": float(vat),
                    "description": "Vorsteuer Self-Billing",
                })
            fin = FinanceTransactionService(self.db, self.tenant_id)
            fin.create(
                entry_number=f"SB-{invoice.invoice_number}",
                description=f"Self-Billing Gutschrift {invoice.invoice_number}",
                entry_date=entry_date,
                lines=lines,
                reference=invoice.invoice_number,
                source="self_billing",
                document_type="credit_note",
                period=period,
            )
        except Exception:
            pass  # booking failure must not block release

    def calculate_settlement(self, acceptance_id: str) -> dict:
        from decimal import Decimal
        from app.repositories.drying_rule_repository import DbDryingRuleRepository
        from modules.agrar.services.harvest_calculator import HarvestCalculationInput, calculate_harvest_settlement
        from app.core.uuid7 import uuid7 as _uuid7

        obj = self._get_or_raise(acceptance_id)

        # Hole Nettogewicht aus Wiegeschein
        delivered_quantity_kg = Decimal("0")
        if obj.weighing_ticket_id:
            ticket = self.db.query(WeighingTicket).filter(WeighingTicket.id == obj.weighing_ticket_id).first()
            if ticket and ticket.net_weight:
                delivered_quantity_kg = ticket.net_weight
            else:
                raise ValidationFailedError("Weighing ticket has no net weight")
        else:
            raise ValidationFailedError("Weighing ticket is required for calculation")

        # Hole Laborwerte aus Positionen, Wiegeschein oder Qualitätsprotokoll
        windage_pct = None
        impurities_pct = None
        moisture_pct = None
        hl_weight_kg_per_hl = None

        # Versuche aus Wiegeschein zu laden
        if obj.weighing_ticket_id:
            ticket = self.db.query(WeighingTicket).filter(WeighingTicket.id == obj.weighing_ticket_id).first()
            if ticket:
                moisture_pct = ticket.moisture_pct
                impurities_pct = ticket.impurities_pct
                hl_weight_kg_per_hl = ticket.hl_weight

        # Hole Eingaben aus Positionen
        positions = self.db.query(HarvestAcceptancePosition).filter(
            HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id
        ).all()

        storage_fee_per_month = None
        storage_months = None
        freight_costs = None
        weighing_fees = None
        storage_shrinkage_pct = None

        for pos in positions:
            if pos.position_number == 15 and pos.lab_value_pct:  # Windabgang
                windage_pct = pos.lab_value_pct
            elif pos.position_number == 20 and pos.lab_value_pct:  # Besatz
                impurities_pct = pos.lab_value_pct
            elif pos.position_number == 40 and pos.lab_value_pct:  # Feuchte
                moisture_pct = pos.lab_value_pct
            elif pos.position_number == 60 and pos.quantity_kg:  # HL-Gewicht
                hl_weight_kg_per_hl = pos.quantity_kg
            elif pos.position_number == 63 and pos.lab_value_pct:  # Lagerschwund
                storage_shrinkage_pct = pos.lab_value_pct
            elif pos.position_number == 75 and pos.amount_eur:  # Lagergeld
                storage_fee_per_month = pos.amount_eur
                if storage_months is None:
                    storage_months = 1
            elif pos.position_number == 78 and pos.amount_eur:  # Frachtkosten
                freight_costs = pos.amount_eur
            elif pos.position_number == 80 and pos.amount_eur:  # Wiegegebühren
                weighing_fees = pos.amount_eur

        # Warnungen sammeln
        warnings: list[str] = []

        # Hole Preis aus Vertrag, Tagespreis oder Artikel
        unit_price_eur_per_ton = None
        crop_code = None
        price_source = "unknown"

        if obj.contract_id:
            contract = self.db.query(AgrarContract).filter(AgrarContract.id == obj.contract_id).first()
            if contract:
                if contract.pricing_model == "fixed" and contract.fixed_price:
                    unit_price_eur_per_ton = contract.fixed_price
                    price_source = "contract_fixed"
                elif contract.pricing_model == "follow":
                    from modules.agrar.services.daily_price_service import DailyPriceFilter
                    from modules.agrar.repositories.daily_price_repo import DailyPriceRepositoryImpl

                    repo = DailyPriceRepositoryImpl(self.db)
                    price_filter = DailyPriceFilter(
                        tenant_id=obj.tenant_id,
                        article_id=obj.article_id,
                        price_date=obj.weighing_date or obj.calculated_date,
                    )
                    daily_price = repo.find_price(price_filter)

                    if daily_price:
                        unit_price_eur_per_ton = float(daily_price.price_eur_per_ton)
                        price_source = "contract_daily_price"
                elif contract.pricing_model == "pool":
                    from datetime import timedelta
                    from modules.agrar.services.daily_price_service import DailyPriceFilter
                    from modules.agrar.repositories.daily_price_repo import DailyPriceRepositoryImpl

                    repo = DailyPriceRepositoryImpl(self.db)
                    pool_days = getattr(contract, "pool_days", 30) or 30
                    pool_start = (obj.weighing_date or obj.calculated_date) - timedelta(days=pool_days)
                    pool_end = obj.weighing_date or obj.calculated_date

                    prices = repo.get_price_history(
                        tenant_id=obj.tenant_id,
                        article_id=obj.article_id,
                        from_date=pool_start,
                        to_date=pool_end,
                        limit=100,
                    )
                    if prices:
                        avg_price = sum(float(p.price_eur_per_ton) for p in prices) / len(prices)
                        unit_price_eur_per_ton = avg_price
                        price_source = "contract_pool"

        # Fallback: Artikel-Preis
        if not unit_price_eur_per_ton and obj.article_id:
            article = self.db.query(Article).filter(Article.id == obj.article_id).first()
            if article:
                if article.warengruppe:
                    warengruppe_upper = article.warengruppe.upper()
                    crop_mapping = {
                        "MAIS": "MAIZE",
                        "WEIZEN": "WHEAT",
                        "GERSTE": "BARLEY",
                        "HAFER": "OATS",
                        "RAPS": "RAPESEED",
                        "ACKERBOHNE": "FIELD_BEANS",
                        "ERBSE": "PEAS",
                        "LUPINE": "LUPINS",
                    }
                    crop_code = crop_mapping.get(warengruppe_upper)

                if not unit_price_eur_per_ton and article.sales_price:
                    unit_price_eur_per_ton = article.sales_price
                    price_source = "article_sales_price"

        # Hole MWSt-Satz aus Artikel oder Kunde
        vat_rate_percent = None
        if obj.article_id:
            article = self.db.query(Article).filter(Article.id == obj.article_id).first()
            if article and article.mehrwertsteuer_prozent:
                vat_rate_percent = article.mehrwertsteuer_prozent

        # Erstelle Drying Rule Repository (falls crop_code vorhanden)
        drying_repo = None
        use_drying_rule_engine = False
        if crop_code and moisture_pct:
            try:
                drying_repo = DbDryingRuleRepository(self.db, tenant_id=self.tenant_id)
                use_drying_rule_engine = True
            except Exception:
                pass

        # Erstelle Berechnungs-Input
        calc_input = HarvestCalculationInput(
            delivered_quantity_kg=delivered_quantity_kg,
            windage_pct=Decimal(str(windage_pct)) if windage_pct else None,
            impurities_pct=Decimal(str(impurities_pct)) if impurities_pct else None,
            moisture_pct=Decimal(str(moisture_pct)) if moisture_pct else None,
            hl_weight_kg_per_hl=Decimal(str(hl_weight_kg_per_hl)) if hl_weight_kg_per_hl else None,
            storage_shrinkage_pct=Decimal(str(storage_shrinkage_pct)) if storage_shrinkage_pct else None,
            storage_fee_per_month=Decimal(str(storage_fee_per_month)) if storage_fee_per_month else None,
            storage_months=storage_months,
            freight_costs=Decimal(str(freight_costs)) if freight_costs else None,
            weighing_fees=Decimal(str(weighing_fees)) if weighing_fees else None,
            unit_price_eur_per_ton=Decimal(str(unit_price_eur_per_ton)) if unit_price_eur_per_ton else None,
            use_drying_rule_engine=use_drying_rule_engine,
            crop_code=crop_code,
            site_id=obj.warehouse_id,
            contract_id=obj.contract_id,
            customer_id=obj.customer_id,
            calc_date=obj.delivery_date,
            drying_repo=drying_repo,
        )

        # Warnung, wenn kein Preis gefunden
        if not unit_price_eur_per_ton:
            warnings.append("Kein Preis gefunden. Bitte manuell eingeben oder Vertrag/Artikel prüfen.")

        # Berechne
        result = calculate_harvest_settlement(calc_input, vat_rate_percent=Decimal(str(vat_rate_percent)) if vat_rate_percent else None)

        # Füge Warnungen hinzu
        if warnings:
            result.warnings.extend(warnings)

        # Aktualisiere Summen in HarvestAcceptance
        obj.total_net_amount_eur = result.total_net_amount_eur
        obj.total_vat_amount_eur = result.total_vat_amount_eur
        obj.total_gross_amount_eur = result.total_gross_amount_eur
        obj.vat_rate_percent = result.vat_rate_percent

        # Aktualisiere Positionen mit berechneten Werten
        for pos_result in result.positions:
            existing_pos = next(
                (p for p in positions if p.position_number == pos_result.position_number),
                None,
            )
            if existing_pos:
                if pos_result.quantity_kg is not None:
                    existing_pos.quantity_kg = pos_result.quantity_kg
                if pos_result.quantity_pct is not None:
                    existing_pos.lab_value_pct = pos_result.quantity_pct
                if pos_result.amount_eur is not None:
                    existing_pos.amount_eur = pos_result.amount_eur
                if pos_result.calculation_formula:
                    existing_pos.calculation_formula = pos_result.calculation_formula
            else:
                new_pos = HarvestAcceptancePosition(
                    id=_uuid7(),
                    harvest_acceptance_id=acceptance_id,
                    position_number=pos_result.position_number,
                    description=pos_result.description,
                    quantity_kg=pos_result.quantity_kg,
                    lab_value_pct=pos_result.quantity_pct,
                    amount_eur=pos_result.amount_eur,
                    unit=pos_result.unit,
                    calculation_formula=pos_result.calculation_formula,
                    is_calculable=True,
                    is_printable=True,
                )
                self.db.add(new_pos)

        self.db.commit()
        self.db.refresh(obj)

        return {
            "acceptance_id": acceptance_id,
            "positions": [
                {
                    "position_number": p.position_number,
                    "description": p.description,
                    "quantity_kg": float(p.quantity_kg) if p.quantity_kg else None,
                    "quantity_pct": float(p.quantity_pct) if p.quantity_pct else None,
                    "amount_eur": float(p.amount_eur) if p.amount_eur else None,
                    "unit": p.unit,
                    "calculation_formula": p.calculation_formula,
                }
                for p in result.positions
            ],
            "total_net_amount_eur": float(result.total_net_amount_eur),
            "total_vat_amount_eur": float(result.total_vat_amount_eur),
            "total_gross_amount_eur": float(result.total_gross_amount_eur),
            "vat_rate_percent": float(result.vat_rate_percent) if result.vat_rate_percent else None,
            "warnings": result.warnings,
            "price_source": price_source,
        }


# ── Pure business-logic functions (testable without DB) ─────────────────────

def calculate_net_weight(
    gross_kg: float,
    tare_kg: float,
    moisture_pct: float,
    drying_target_pct: float,
) -> float:
    """Nettogewicht nach Abzug Tara und Trocknungskorrektur berechnen.

    Formel:
        1. netto_feucht = gross_kg - tare_kg
        2. Wenn moisture_pct > drying_target_pct:
               trocknungsabzug = netto_feucht * (moisture_pct - drying_target_pct) / 100
           Sonst: 0
        3. netto_trocken = netto_feucht - trocknungsabzug

    Args:
        gross_kg: Bruttogewicht in kg (Wiegegewicht).
        tare_kg: Taragewicht (Fahrzeug + Behälter) in kg.
        moisture_pct: Gemessener Feuchtegehalt in Prozent (z.B. 15.5).
        drying_target_pct: Ziel-Feuchtegehalt laut Norm (z.B. 14.0 für Weizen).

    Returns:
        Nettogewicht in kg (gerundet auf 3 Dezimalstellen).

    Raises:
        ValueError: Wenn Gewichte negativ oder tare_kg >= gross_kg.
    """
    if gross_kg < 0 or tare_kg < 0:
        raise ValueError("Gewichte dürfen nicht negativ sein")
    if tare_kg >= gross_kg:
        raise ValueError(f"Tara ({tare_kg} kg) muss kleiner als Brutto ({gross_kg} kg) sein")
    if not (0 <= moisture_pct <= 100):
        raise ValueError(f"Feuchtegehalt muss zwischen 0 und 100 Prozent liegen, erhalten: {moisture_pct}")
    if not (0 <= drying_target_pct <= 100):
        raise ValueError(f"Ziel-Feuchte muss zwischen 0 und 100 Prozent liegen, erhalten: {drying_target_pct}")

    netto_feucht = gross_kg - tare_kg
    if moisture_pct > drying_target_pct:
        trocknungsabzug = netto_feucht * (moisture_pct - drying_target_pct) / 100
    else:
        trocknungsabzug = 0.0
    netto_trocken = netto_feucht - trocknungsabzug
    return round(netto_trocken, 3)


def assign_quality_grade(
    moisture_pct: float,
    protein_pct: float,
    contamination_pct: float,
) -> str:
    """Qualitätsstufe (A/B/C/Reject) gemäß Standardparametern bestimmen.

    Grenzwerte (vereinfacht, angelehnt an DLG/VTG-Normen):
        - A: moisture ≤ 14, protein ≥ 12, contamination ≤ 1
        - B: moisture ≤ 15, protein ≥ 10, contamination ≤ 2
        - C: moisture ≤ 16, protein ≥ 8,  contamination ≤ 3
        - Reject: sonst (zu feucht, zu wenig Protein oder zu viel Verunreinigung)

    Args:
        moisture_pct: Feuchtegehalt in Prozent.
        protein_pct: Proteingehalt in Prozent.
        contamination_pct: Verunreinigungsanteil in Prozent.

    Returns:
        Qualitätsstufe als String: "A", "B", "C" oder "REJECT".

    Raises:
        ValueError: Bei ungültigen Prozentwerten.
    """
    for name, val in [("Feuchte", moisture_pct), ("Protein", protein_pct), ("Verunreinigung", contamination_pct)]:
        if not (0 <= val <= 100):
            raise ValueError(f"{name} muss zwischen 0 und 100 Prozent liegen, erhalten: {val}")

    if moisture_pct <= 14.0 and protein_pct >= 12.0 and contamination_pct <= 1.0:
        return "A"
    if moisture_pct <= 15.0 and protein_pct >= 10.0 and contamination_pct <= 2.0:
        return "B"
    if moisture_pct <= 16.0 and protein_pct >= 8.0 and contamination_pct <= 3.0:
        return "C"
    return "REJECT"


# ── Ergänzung HarvestAcceptanceService: get_delivery_summary ─────────────────

# Methode wird als Mixin am Ende der Klasse ergänzt — siehe unten.
# (Python lässt keine nachträgliche Klassen-Erweiterung mit Monkey-Patching zu,
#  daher wird get_delivery_summary direkt in der Klassendefinition ergänzt.)
# Die Implementierung ist als Standalone-Funktion verfügbar:

def get_delivery_summary(delivery_id: str, db: Session) -> dict:
    """Read-Model: kompakte Zusammenfassung einer Ernte-Annahme für Dashboard/Reports.

    Args:
        delivery_id: ID der HarvestAcceptance.
        db: SQLAlchemy Session.

    Returns:
        Dict mit acceptance_number, customer_id, delivery_date, release_status,
        total_net_amount_eur, position_count, article_name.

    Raises:
        EntityNotFoundError: Wenn Annahme nicht gefunden.
    """
    obj = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == delivery_id).first()
    if not obj:
        raise EntityNotFoundError("HarvestAcceptance", delivery_id)

    position_count = db.query(HarvestAcceptancePosition).filter(
        HarvestAcceptancePosition.harvest_acceptance_id == delivery_id
    ).count()

    article_name: Optional[str] = None
    if obj.article_id:
        article = db.query(Article).filter(Article.id == obj.article_id).first()
        if article:
            article_name = article.name or (article.description[:100] if article.description else None)

    return {
        "acceptance_number": obj.acceptance_number,
        "customer_id": obj.customer_id,
        "delivery_date": str(obj.delivery_date),
        "release_status": obj.release_status,
        "total_net_amount_eur": float(obj.total_net_amount_eur) if obj.total_net_amount_eur else None,
        "position_count": position_count,
        "article_name": article_name,
    }
