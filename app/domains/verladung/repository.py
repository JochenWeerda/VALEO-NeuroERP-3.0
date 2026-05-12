"""
Repository Pattern for Verladung Domain (Tours)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from app.core.uuid7 import prefixed_id

from app.domains.verladung.models import (
    Tour, TourStatus,
    TourStop, TourDeliveryNote,
    DeliveryNoteStatus, TourEvent,
    EventType
)


class TourRepository:
    """Repository for Tour operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
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
        query = self.db.query(Tour)
        
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
        return self.db.query(Tour).filter(Tour.id == tour_id).first()
    
    def get_by_tour_no(self, tour_no: str) -> Optional[Tour]:
        return self.db.query(Tour).filter(Tour.tour_no == tour_no).first()
    
    def get_by_week(self, week: str) -> List[Tour]:
        return self.db.query(Tour).filter(Tour.week == week).all()
    
    def get_by_date(self, date: datetime) -> List[Tour]:
        return self.db.query(Tour).filter(Tour.date == date).all()
    
    def create(self, tour_data: dict) -> Tour:
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
    
    def update(self, tour_id: str, tour_data: dict) -> Optional[Tour]:
        tour = self.get_by_id(tour_id)
        if tour:
            for key, value in tour_data.items():
                setattr(tour, key, value)
            self.db.commit()
            self.db.refresh(tour)
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
        
        stops = self.db.query(TourStop).filter(TourStop.tour_id == tour_id).all()
        dns = self.db.query(TourDeliveryNote).filter(TourDeliveryNote.tour_id == tour_id).all()
        
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
    
    def start_loading(self, tour_id: str, user_id: str, user_name: str) -> Optional[Tour]:
        """Mark tour as loading"""
        tour = self.update(tour_id, {"status": TourStatus.LOADING.value})
        if tour:
            self.add_event(tour_id, EventType.LOADING_STARTED.value, "Loading started", user_id, user_name)
        return tour
    
    def finish_loading(self, tour_id: str, user_id: str, user_name: str) -> Optional[Tour]:
        """Mark loading as finished"""
        tour = self.update(tour_id, {"status": TourStatus.IN_TRANSIT.value})
        if tour:
            self.add_event(tour_id, EventType.LOADING_FINISHED.value, "Loading finished", user_id, user_name)
        return tour
    
    def add_event(
        self,
        tour_id: str,
        event_type: str,
        message: str = None,
        user_id: str = None,
        user_name: str = None,
        metadata: dict = None
    ) -> TourEvent:
        """Add event to tour"""
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
        self.db.commit()
        self.db.refresh(event)
        return event


class TourStopRepository:
    """Repository for TourStop operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, tour_id: str) -> List[TourStop]:
        return self.db.query(TourStop).filter(
            TourStop.tour_id == tour_id
        ).order_by(TourStop.sequence).all()
    
    def get_by_id(self, stop_id: str) -> Optional[TourStop]:
        return self.db.query(TourStop).filter(TourStop.id == stop_id).first()
    
    def create(self, stop_data: dict) -> TourStop:
        # Auto-increment sequence if not provided
        if "sequence" not in stop_data or stop_data["sequence"] is None:
            max_seq = self.db.query(TourStop).filter(
                TourStop.tour_id == stop_data.get("tour_id")
            ).with_entities(func.max(TourStop.sequence)).scalar() or 0
            stop_data["sequence"] = max_seq + 1
        
        stop = TourStop(id=prefixed_id("STOP"), **stop_data)
        self.db.add(stop)
        self.db.commit()
        self.db.refresh(stop)
        return stop
    
    def update(self, stop_id: str, stop_data: dict) -> Optional[TourStop]:
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
        dns = self.db.query(TourDeliveryNote).filter(
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


class TourDeliveryNoteRepository:
    """Repository for Delivery Note operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, stop_id: str) -> List[TourDeliveryNote]:
        return self.db.query(TourDeliveryNote).filter(
            TourDeliveryNote.stop_id == stop_id
        ).all()
    
    def get_by_id(self, dn_id: str) -> Optional[TourDeliveryNote]:
        return self.db.query(TourDeliveryNote).filter(TourDeliveryNote.id == dn_id).first()
    
    def get_by_dn_no(self, dn_no: str) -> Optional[TourDeliveryNote]:
        return self.db.query(TourDeliveryNote).filter(TourDeliveryNote.dn_no == dn_no).first()
    
    def create(self, dn_data: dict) -> TourDeliveryNote:
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
        results = []
        for dn_id in dn_ids:
            dn = self.get_by_id(dn_id)
            if dn:
                dn.tour_id = tour_id
                dn.stop_id = stop_id
                dn.status = DeliveryNoteStatus.LOADED.value
                dn.loaded_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(dn)
                results.append(dn)
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


class TourEventRepository:
    """Repository for TourEvent operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, tour_id: str) -> List[TourEvent]:
        return self.db.query(TourEvent).filter(
            TourEvent.tour_id == tour_id
        ).order_by(desc(TourEvent.at)).all()
    
    def get_by_id(self, event_id: str) -> Optional[TourEvent]:
        return self.db.query(TourEvent).filter(TourEvent.id == event_id).first()
