"""
Repository Pattern for Verladung Domain (Tours)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException
from datetime import datetime
from app.core.uuid7 import prefixed_id

from app.domains.verladung.models import (
    Tour, TourStatus,
    TourStop, TourDeliveryNote,
    DeliveryNoteStatus, TourEvent,
    EventType
)


class TenantTourRepository:
    """One explicit verified context; children inherit ownership through the tour."""

    def __init__(self, db: Session, tenant_id: str):
        if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id.strip() == "legacy-unassigned":
            raise HTTPException(403, "Verified tenant context required")
        self.db, self.tenant_id = db, tenant_id.strip()

    def scoped(self, model):
        query = self.db.query(model)
        if model is not Tour:
            query = query.join(Tour, model.tour_id == Tour.id)
        return query.filter(Tour.tenant_id == self.tenant_id)

    def require_tour(self, tour_id):
        tour = self.scoped(Tour).filter(Tour.id == tour_id).first()
        if tour is None:
            raise HTTPException(404, "Tour not found")
        return tour

    def require_stop(self, stop_id, tour_id):
        stop = self.scoped(TourStop).filter(TourStop.id == stop_id, TourStop.tour_id == tour_id).first()
        if stop is None:
            raise HTTPException(404, "Stop not found")
        return stop

    def protect_identity(self, data, *, creating=False):
        forbidden = {"created_by", "updated_by", "created_at", "updated_at", "created_at_record"}
        allowed = set(self.row_model.__table__.columns.keys()) - forbidden
        if set(data) - allowed - {"tenant_id"}:
            raise HTTPException(422, "Unsupported or managed fields")
        if "tenant_id" in data and data["tenant_id"] != self.tenant_id:
            raise HTTPException(403, "Tenant override forbidden")
        if "id" in data or (not creating and "tour_id" in data):
            raise HTTPException(422, "Object identity is immutable")
        return {k: v for k, v in data.items() if k != "tenant_id"}

    def validate_tour_references(self, data):
        # Fahrer has no ownership column: never guess it from a vehicle.
        if data.get("driver_id"):
            raise HTTPException(422, "Driver tenant ownership is not available")
        if data.get("vehicle_id"):
            from app.domains.operations.models import Fahrzeug
            vehicle = self.db.query(Fahrzeug).filter(Fahrzeug.id == data["vehicle_id"], Fahrzeug.tenant_id == self.tenant_id).first()
            if vehicle is None:
                raise HTTPException(404, "Vehicle not found")


class TourRepository(TenantTourRepository):
    row_model = Tour
    """Repository for Tour operations"""
    
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        driver_id: Optional[str] = None,
        vehicle_id: Optional[str] = None
    ) -> List[Tour]:
        query = self.scoped(Tour)
        
        if status:
            query = query.filter(Tour.status == status)
        if date_from:
            query = query.filter(Tour.date >= date_from)
        if date_to:
            query = query.filter(Tour.date <= date_to)
        if driver_id:
            query = query.filter(Tour.driver_id == driver_id)
        if vehicle_id:
            query = query.filter(Tour.vehicle_id == vehicle_id)
        
        return query.order_by(desc(Tour.date)).offset(skip).limit(limit).all()
    
    def get_by_id(self, tour_id: str) -> Optional[Tour]:
        return self.scoped(Tour).filter(Tour.id == tour_id).first()
    
    def get_by_tour_no(self, tour_no: str) -> Optional[Tour]:
        return self.scoped(Tour).filter(Tour.tour_no == tour_no).first()
    
    def get_by_week(self, week: str) -> List[Tour]:
        return self.scoped(Tour).filter(Tour.week == week).all()
    
    def get_by_date(self, date: datetime) -> List[Tour]:
        return self.scoped(Tour).filter(Tour.date == date).all()
    
    def create(self, tour_data: dict) -> Tour:
        tour_data = self.protect_identity(tour_data, creating=True)
        self.validate_tour_references(tour_data)
        tour_data["tenant_id"] = self.tenant_id
        # Auto-generate tour_no if not provided
        if "tour_no" not in tour_data or not tour_data["tour_no"]:
            tour_data["tour_no"] = self._generate_tour_no(tour_data.get("date"))
        
        tour = Tour(id=prefixed_id("TOUR"), **tour_data)
        self.db.add(tour)
        self.db.commit()
        self.db.refresh(tour)
        return tour
    
    def _generate_tour_no(self, date: datetime) -> str:
        """Generate tour number like STK-2026-W07"""
        if date:
            year = date.strftime("%Y")
            week = date.isocalendar()[1]
            return f"STK-{year}-W{week:02d}"
        return f"STK-{datetime.utcnow().strftime('%Y-%W%w')}"
    
    def update(self, tour_id: str, tour_data: dict, *, commit: bool = True) -> Optional[Tour]:
        tour_data = self.protect_identity(tour_data)
        self.validate_tour_references(tour_data)
        tour = self.get_by_id(tour_id)
        if tour:
            for key, value in tour_data.items():
                setattr(tour, key, value)
            if commit:
                self.db.commit()
                self.db.refresh(tour)
            else:
                self.db.flush()
        return tour
    
    def delete(self, tour_id: str) -> bool:
        tour = self.get_by_id(tour_id)
        if tour:
            self.db.delete(tour)
            self.db.commit()
            return True
        return False
    
    def calculate_totals(self, tour_id: str) -> dict:
        """Calculate and update tour totals"""
        tour = self.get_by_id(tour_id)
        if not tour:
            return {}
        
        stops = self.scoped(TourStop).filter(TourStop.tour_id == tour_id).all()
        dns = self.scoped(TourDeliveryNote).filter(TourDeliveryNote.tour_id == tour_id).all()
        
        totals = {
            "stops": len(stops),
            "delivery_notes": len(dns),
            "pieces": sum(dn.items_pieces or 0 for dn in dns),
            "weight_kg": sum(dn.items_weight_kg or 0 for dn in dns),
            "volume_m3": sum(dn.items_volume_m3 or 0 for dn in dns)
        }
        
        # Update tour with totals
        self.update(tour_id, {"totals_json": totals})
        return totals
    
    def dispatch(self, tour_id: str, user_id: str, user_name: str) -> Optional[Tour]:
        """Mark tour as dispatched and add event"""
        tour = self.update(tour_id, {
            "status": TourStatus.DISPATCHED.value,
            "actual_departure_at": datetime.utcnow()
        })
        
        if tour:
            self.add_event(tour_id, EventType.DISPATCHED.value, "Tour dispatched", user_id, user_name)
        
        return tour
    
    def start_loading(self, tour_id: str, user_id: str, user_name: str, *, commit: bool = True) -> Optional[Tour]:
        """Mark tour as loading"""
        tour = self.update(tour_id, {"status": TourStatus.LOADING.value}, commit=False)
        if tour:
            self.add_event(tour_id, EventType.LOADING_STARTED.value, "Loading started", user_id, user_name, commit=False)
        if tour and commit:
            self.db.commit()
            self.db.refresh(tour)
        return tour
    
    def finish_loading(self, tour_id: str, user_id: str, user_name: str, *, commit: bool = True) -> Optional[Tour]:
        """Mark loading as finished"""
        tour = self.update(tour_id, {"status": TourStatus.IN_TRANSIT.value}, commit=False)
        if tour:
            self.add_event(tour_id, EventType.LOADING_FINISHED.value, "Loading finished", user_id, user_name, commit=False)
        if tour and commit:
            self.db.commit()
            self.db.refresh(tour)
        return tour
    
    def add_event(
        self,
        tour_id: str,
        event_type: str,
        message: str = None,
        user_id: str = None,
        user_name: str = None,
        metadata: dict = None,
        *, commit: bool = True
    ) -> TourEvent:
        """Add event to tour"""
        self.require_tour(tour_id)
        event = TourEvent(
            id=prefixed_id("EVT"),
            tour_id=tour_id,
            type=event_type,
            message=message,
            user_id=user_id,
            user_name=user_name,
            metadata_json=metadata,
            at=datetime.utcnow()
        )
        self.db.add(event)
        if commit:
            self.db.commit()
            self.db.refresh(event)
        else:
            self.db.flush()
        return event


class TourStopRepository(TenantTourRepository):
    row_model = TourStop
    """Repository for TourStop operations"""
    
    
    def get_all(self, tour_id: str) -> List[TourStop]:
        return self.scoped(TourStop).filter(
            TourStop.tour_id == tour_id
        ).order_by(TourStop.sequence).all()
    
    def get_by_id(self, stop_id: str) -> Optional[TourStop]:
        return self.scoped(TourStop).filter(TourStop.id == stop_id).first()
    
    def create(self, stop_data: dict) -> TourStop:
        stop_data = self.protect_identity(stop_data, creating=True)
        self.require_tour(stop_data.get("tour_id"))
        # Auto-increment sequence if not provided
        if "sequence" not in stop_data or stop_data["sequence"] is None:
            max_seq = self.scoped(TourStop).filter(
                TourStop.tour_id == stop_data.get("tour_id")
            ).with_entities(func.max(TourStop.sequence)).scalar() or 0
            stop_data["sequence"] = max_seq + 1
        
        stop = TourStop(id=prefixed_id("STOP"), **stop_data)
        self.db.add(stop)
        self.db.commit()
        self.db.refresh(stop)
        return stop
    
    def update(self, stop_id: str, stop_data: dict) -> Optional[TourStop]:
        stop_data = self.protect_identity(stop_data)
        stop = self.get_by_id(stop_id)
        if stop:
            for key, value in stop_data.items():
                setattr(stop, key, value)
            self.db.commit()
            self.db.refresh(stop)
        return stop
    
    def delete(self, stop_id: str) -> bool:
        stop = self.get_by_id(stop_id)
        if stop:
            self.db.delete(stop)
            self.db.commit()
            return True
        return False
    
    def calculate_stop_totals(self, stop_id: str) -> dict:
        """Calculate and update stop totals"""
        dns = self.scoped(TourDeliveryNote).filter(
            TourDeliveryNote.stop_id == stop_id
        ).all()
        
        totals = {
            "delivery_notes": len(dns),
            "pieces": sum(dn.items_pieces or 0 for dn in dns),
            "weight_kg": sum(dn.items_weight_kg or 0 for dn in dns),
            "volume_m3": sum(dn.items_volume_m3 or 0 for dn in dns)
        }
        
        self.update(stop_id, {"totals_json": totals})
        return totals


class TourDeliveryNoteRepository(TenantTourRepository):
    row_model = TourDeliveryNote
    """Repository for Delivery Note operations"""
    
    
    def get_all(self, stop_id: str) -> List[TourDeliveryNote]:
        return self.scoped(TourDeliveryNote).filter(
            TourDeliveryNote.stop_id == stop_id
        ).all()
    
    def get_by_id(self, dn_id: str) -> Optional[TourDeliveryNote]:
        return self.scoped(TourDeliveryNote).filter(TourDeliveryNote.id == dn_id).first()
    
    def get_by_dn_no(self, dn_no: str) -> Optional[TourDeliveryNote]:
        return self.scoped(TourDeliveryNote).filter(TourDeliveryNote.dn_no == dn_no).first()
    
    def create(self, dn_data: dict) -> TourDeliveryNote:
        dn_data = self.protect_identity(dn_data, creating=True)
        self.require_tour(dn_data.get("tour_id"))
        if dn_data.get("stop_id"):
            self.require_stop(dn_data["stop_id"], dn_data["tour_id"])
        dn = TourDeliveryNote(id=prefixed_id("DN"), **dn_data)
        self.db.add(dn)
        self.db.commit()
        self.db.refresh(dn)
        return dn
    
    def assign_to_stop(
        self,
        tour_id: str,
        stop_id: str,
        dn_ids: List[str]
    ) -> List[TourDeliveryNote]:
        """Assign delivery notes to a stop"""
        self.require_tour(tour_id)
        self.require_stop(stop_id, tour_id)
        notes = [self.get_by_id(dn_id) for dn_id in dn_ids]
        if any(dn is None for dn in notes):
            raise HTTPException(404, "Delivery note not found")
        results = []
        for dn in notes:
            if dn:
                dn.tour_id = tour_id
                dn.stop_id = stop_id
                dn.status = DeliveryNoteStatus.LOADED.value
                dn.loaded_at = datetime.utcnow()
                results.append(dn)
        self.db.commit()
        for dn in results:
            self.db.refresh(dn)
        return results
    
    def mark_delivered(self, dn_id: str) -> Optional[TourDeliveryNote]:
        """Mark DN as delivered"""
        dn = self.get_by_id(dn_id)
        if dn:
            dn.status = DeliveryNoteStatus.DELIVERED.value
            dn.delivered_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(dn)
        return dn
    
    def delete(self, dn_id: str) -> bool:
        dn = self.get_by_id(dn_id)
        if dn:
            self.db.delete(dn)
            self.db.commit()
            return True
        return False


class TourEventRepository(TenantTourRepository):
    """Repository for TourEvent operations"""
    
    
    def get_all(self, tour_id: str) -> List[TourEvent]:
        return self.scoped(TourEvent).filter(
            TourEvent.tour_id == tour_id
        ).order_by(desc(TourEvent.at)).all()
    
    def get_by_id(self, event_id: str) -> Optional[TourEvent]:
        return self.scoped(TourEvent).filter(TourEvent.id == event_id).first()
