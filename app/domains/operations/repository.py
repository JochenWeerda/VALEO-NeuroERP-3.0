"""
Repository Pattern for Operations Domain
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timezone
from app.core.uuid7 import uuid7

from app.domains.operations.models import (
    Waage, WaageStatus,
    Wiegung,
    Fahrzeug, FahrzeugStatus,
    Fahrer, FahrerStatus,
    FahrzeugTour,
    Dokument, DokumentStatus,
    DokumentVersion,
    Charge,
    ChargeStatus,
    BankKonto,
    Rahmenvertrag,
)


class WaageRepository:
    """Repository for Waage operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Waage]:
        return self.db.query(Waage).offset(skip).limit(limit).all()
    
    def get_by_id(self, waage_id: str) -> Optional[Waage]:
        return self.db.query(Waage).filter(Waage.id == waage_id).first()
    
    def get_by_status(self, status: str) -> List[Waage]:
        return self.db.query(Waage).filter(Waage.status == status).all()
    
    def create(self, waage_data: dict) -> Waage:
        waage = Waage(
            id=f"W-{str(__import__('uuid').uuid4())[:8].upper()}",
            **waage_data
        )
        self.db.add(waage)
        self.db.commit()
        self.db.refresh(waage)
        return waage
    
    def update(self, waage_id: str, waage_data: dict) -> Optional[Waage]:
        waage = self.get_by_id(waage_id)
        if waage:
            for key, value in waage_data.items():
                setattr(waage, key, value)
            self.db.commit()
            self.db.refresh(waage)
        return waage
    
    def delete(self, waage_id: str) -> bool:
        waage = self.get_by_id(waage_id)
        if waage:
            self.db.delete(waage)
            self.db.commit()
            return True
        return False


class WiegungRepository:
    """Repository for Wiegung operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Wiegung]:
        return self.db.query(Wiegung).order_by(desc(Wiegung.zeitstempel)).offset(skip).limit(limit).all()
    
    def get_by_id(self, wiegung_id: str) -> Optional[Wiegung]:
        return self.db.query(Wiegung).filter(Wiegung.id == wiegung_id).first()
    
    def get_by_waage(self, waage_id: str) -> List[Wiegung]:
        return self.db.query(Wiegung).filter(Wiegung.waage_id == waage_id).all()
    
    def get_by_kennzeichen(self, kennzeichen: str) -> List[Wiegung]:
        return self.db.query(Wiegung).filter(Wiegung.kennzeichen == kennzeichen).all()
    
    def create(self, wiegung_data: dict) -> Wiegung:
        wiegung = Wiegung(
            id=f"WG-{str(__import__('uuid').uuid4())[:8].upper()}",
            **wiegung_data
        )
        self.db.add(wiegung)
        self.db.commit()
        self.db.refresh(wiegung)
        return wiegung
    
    def delete(self, wiegung_id: str) -> bool:
        wiegung = self.get_by_id(wiegung_id)
        if wiegung:
            self.db.delete(wiegung)
            self.db.commit()
            return True
        return False


class FahrzeugRepository:
    """Repository for Fahrzeug operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Fahrzeug]:
        return self.db.query(Fahrzeug).offset(skip).limit(limit).all()
    
    def get_by_id(self, fahrzeug_id: str) -> Optional[Fahrzeug]:
        return self.db.query(Fahrzeug).filter(Fahrzeug.id == fahrzeug_id).first()
    
    def get_by_status(self, status: str) -> List[Fahrzeug]:
        return self.db.query(Fahrzeug).filter(Fahrzeug.status == status).all()
    
    def get_by_kennzeichen(self, kennzeichen: str) -> Optional[Fahrzeug]:
        return self.db.query(Fahrzeug).filter(Fahrzeug.kennzeichen == kennzeichen).first()
    
    def create(self, fahrzeug_data: dict) -> Fahrzeug:
        fahrzeug = Fahrzeug(
            id=f"F-{str(__import__('uuid').uuid4())[:8].upper()}",
            **fahrzeug_data
        )
        self.db.add(fahrzeug)
        self.db.commit()
        self.db.refresh(fahrzeug)
        return fahrzeug
    
    def update(self, fahrzeug_id: str, fahrzeug_data: dict) -> Optional[Fahrzeug]:
        fahrzeug = self.get_by_id(fahrzeug_id)
        if fahrzeug:
            for key, value in fahrzeug_data.items():
                setattr(fahrzeug, key, value)
            self.db.commit()
            self.db.refresh(fahrzeug)
        return fahrzeug
    
    def delete(self, fahrzeug_id: str) -> bool:
        fahrzeug = self.get_by_id(fahrzeug_id)
        if fahrzeug:
            self.db.delete(fahrzeug)
            self.db.commit()
            return True
        return False


class FahrerRepository:
    """Repository for Fahrer operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Fahrer]:
        return self.db.query(Fahrer).offset(skip).limit(limit).all()
    
    def get_by_id(self, fahrer_id: str) -> Optional[Fahrer]:
        return self.db.query(Fahrer).filter(Fahrer.id == fahrer_id).first()
    
    def get_by_status(self, status: str) -> List[Fahrer]:
        return self.db.query(Fahrer).filter(Fahrer.status == status).all()
    
    def get_by_personalnummer(self, personalnummer: str) -> Optional[Fahrer]:
        return self.db.query(Fahrer).filter(Fahrer.personalnummer == personalnummer).first()
    
    def create(self, fahrer_data: dict) -> Fahrer:
        fahrer = Fahrer(
            id=f"DR-{str(__import__('uuid').uuid4())[:8].upper()}",
            **fahrer_data
        )
        self.db.add(fahrer)
        self.db.commit()
        self.db.refresh(fahrer)
        return fahrer
    
    def update(self, fahrer_id: str, fahrer_data: dict) -> Optional[Fahrer]:
        fahrer = self.get_by_id(fahrer_id)
        if fahrer:
            for key, value in fahrer_data.items():
                setattr(fahrer, key, value)
            self.db.commit()
            self.db.refresh(fahrer)
        return fahrer
    
    def delete(self, fahrer_id: str) -> bool:
        fahrer = self.get_by_id(fahrer_id)
        if fahrer:
            self.db.delete(fahrer)
            self.db.commit()
            return True
        return False


class FahrzeugTourRepository:
    """Repository for FahrzeugTour operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[FahrzeugTour]:
        return self.db.query(FahrzeugTour).offset(skip).limit(limit).all()
    
    def get_by_id(self, tour_id: str) -> Optional[FahrzeugTour]:
        return self.db.query(FahrzeugTour).filter(FahrzeugTour.id == tour_id).first()
    
    def get_by_fahrzeug(self, fahrzeug_id: str) -> List[FahrzeugTour]:
        return self.db.query(FahrzeugTour).filter(FahrzeugTour.fahrzeug_id == fahrzeug_id).all()
    
    def get_by_fahrer(self, fahrer_id: str) -> List[FahrzeugTour]:
        return self.db.query(FahrzeugTour).filter(FahrzeugTour.fahrer_id == fahrer_id).all()
    
    def create(self, tour_data: dict) -> FahrzeugTour:
        tour = FahrzeugTour(
            id=f"TOUR-{str(__import__('uuid').uuid4())[:8].upper()}",
            **tour_data
        )
        self.db.add(tour)
        self.db.commit()
        self.db.refresh(tour)
        return tour
    
    def update(self, tour_id: str, tour_data: dict) -> Optional[FahrzeugTour]:
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


# ── DOKUMENTE REPOSITORIES ──────────────────────────────────────────────

class DokumentRepository:
    """Repository for Dokument operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Dokument]:
        return self.db.query(Dokument).filter(Dokument.status != DokumentStatus.GELOESCHT.value).offset(skip).limit(limit).all()
    
    def get_by_id(self, dokument_id: str) -> Optional[Dokument]:
        return self.db.query(Dokument).filter(Dokument.id == dokument_id).first()
    
    def get_by_kategorie(self, kategorie: str) -> List[Dokument]:
        return self.db.query(Dokument).filter(Dokument.kategorie == kategorie, Dokument.status != DokumentStatus.GELOESCHT.value).all()
    
    def get_by_typ(self, typ: str) -> List[Dokument]:
        return self.db.query(Dokument).filter(Dokument.typ == typ, Dokument.status != DokumentStatus.GELOESCHT.value).all()
    
    def get_by_referenz(self, referenz_typ: str, referenz_id: str) -> List[Dokument]:
        return self.db.query(Dokument).filter(
            Dokument.referenz_typ == referenz_typ,
            Dokument.referenz_id == referenz_id,
            Dokument.status != DokumentStatus.GELOESCHT.value
        ).all()
    
    def search(self, query: str) -> List[Dokument]:
        return self.db.query(Dokument).filter(
            Dokument.name.contains(query),
            Dokument.status != DokumentStatus.GELOESCHT.value
        ).all()
    
    def create(self, dokument_data: dict) -> Dokument:
        dokument = Dokument(
            id=f"DOC-{str(__import__('uuid').uuid4())[:8].upper()}",
            **dokument_data
        )
        self.db.add(dokument)
        self.db.commit()
        self.db.refresh(dokument)
        return dokument
    
    def update(self, dokument_id: str, dokument_data: dict) -> Optional[Dokument]:
        dokument = self.get_by_id(dokument_id)
        if dokument:
            for key, value in dokument_data.items():
                setattr(dokument, key, value)
            self.db.commit()
            self.db.refresh(dokument)
        return dokument
    
    def soft_delete(self, dokument_id: str) -> bool:
        """Soft delete - mark as deleted instead of removing"""
        dokument = self.get_by_id(dokument_id)
        if dokument:
            from datetime import datetime
            dokument.status = DokumentStatus.GELOESCHT.value
            dokument.geloescht_am = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def delete(self, dokument_id: str) -> bool:
        """Hard delete - actually remove from database"""
        dokument = self.get_by_id(dokument_id)
        if dokument:
            self.db.delete(dokument)
            self.db.commit()
            return True
        return False
    
    def get_stats(self) -> dict:
        """Get document statistics"""
        total = self.db.query(Dokument).filter(Dokument.status != DokumentStatus.GELOESCHT.value).count()
        total_size = self.db.query(Dokument).filter(Dokument.status != DokumentStatus.GELOESCHT.value).with_entities(func.sum(Dokument.groesse)).scalar() or 0
        
        # Group by category
        kategorien = {}
        for d in self.db.query(Dokument).filter(Dokument.status != DokumentStatus.GELOESCHT.value).all():
            if d.kategorie not in kategorien:
                kategorien[d.kategorie] = 0
            kategorien[d.kategorie] += 1
        
        return {
            "total": total,
            "total_size_kb": total_size,
            "by_category": kategorien
        }


class DokumentVersionRepository:
    """Repository for DokumentVersion operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, dokument_id: str) -> List[DokumentVersion]:
        return self.db.query(DokumentVersion).filter(DokumentVersion.dokument_id == dokument_id).order_by(DokumentVersion.version.desc()).all()
    
    def get_by_id(self, version_id: str) -> Optional[DokumentVersion]:
        return self.db.query(DokumentVersion).filter(DokumentVersion.id == version_id).first()
    
    def get_latest(self, dokument_id: str) -> Optional[DokumentVersion]:
        return self.db.query(DokumentVersion).filter(DokumentVersion.dokument_id == dokument_id).order_by(DokumentVersion.version.desc()).first()
    
    def create(self, version_data: dict) -> DokumentVersion:
        version = DokumentVersion(
            id=f"VER-{str(__import__('uuid').uuid4())[:8].upper()}",
            **version_data
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def delete(self, version_id: str) -> bool:
        version = self.get_by_id(version_id)
        if version:
            self.db.delete(version)
            self.db.commit()
            return True
        return False


class ChargeRepository:
    """Repository for charge/lot operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        lagerort: Optional[str] = None,
    ) -> List[Charge]:
        query = self.db.query(Charge)
        if search:
            pattern = f"%{search}%"
            query = query.filter((Charge.chargen_id.ilike(pattern)) | (Charge.artikel.ilike(pattern)))
        if status:
            query = query.filter(Charge.status == status)
        if lagerort:
            query = query.filter(Charge.lagerort == lagerort)
        return query.order_by(desc(Charge.created_at)).offset(skip).limit(limit).all()

    def count(self, search: Optional[str] = None, status: Optional[str] = None, lagerort: Optional[str] = None) -> int:
        query = self.db.query(Charge)
        if search:
            pattern = f"%{search}%"
            query = query.filter((Charge.chargen_id.ilike(pattern)) | (Charge.artikel.ilike(pattern)))
        if status:
            query = query.filter(Charge.status == status)
        if lagerort:
            query = query.filter(Charge.lagerort == lagerort)
        return query.count()

    def get_by_id(self, charge_id: str) -> Optional[Charge]:
        return self.db.query(Charge).filter(Charge.id == charge_id).first()

    def get_by_chargen_id(self, chargen_id: str) -> Optional[Charge]:
        return self.db.query(Charge).filter(Charge.chargen_id == chargen_id).first()

    def create(self, charge_data: dict) -> Charge:
        payload = dict(charge_data)
        payload.setdefault("status", ChargeStatus.ERFASST.value)
        charge = Charge(
            id=f"CH-{uuid7()[:8].upper()}",
            **payload,
        )
        self.db.add(charge)
        self.db.commit()
        self.db.refresh(charge)
        return charge

    def update(self, charge_id: str, charge_data: dict) -> Optional[Charge]:
        charge = self.get_by_id(charge_id)
        if charge:
            for key, value in charge_data.items():
                setattr(charge, key, value)
            self.db.commit()
            self.db.refresh(charge)
        return charge

    def delete(self, charge_id: str) -> bool:
        charge = self.get_by_id(charge_id)
        if charge:
            self.db.delete(charge)
            self.db.commit()
            return True
        return False

    def get_stats(self) -> dict:
        total = self.db.query(Charge).count()
        in_pruefung = self.db.query(Charge).filter(Charge.status == ChargeStatus.IN_PRUEFUNG.value).count()
        freigegeben = self.db.query(Charge).filter(Charge.status == ChargeStatus.FREIGEGEBEN.value).count()
        gesperrt = self.db.query(Charge).filter(Charge.status == ChargeStatus.GESPERRT.value).count()
        total_menge = self.db.query(func.coalesce(func.sum(Charge.menge), 0)).scalar() or 0

        by_lagerort: dict[str, dict[str, float]] = {}
        rows = self.db.query(Charge.lagerort, func.count(Charge.id), func.coalesce(func.sum(Charge.menge), 0)).group_by(Charge.lagerort).all()
        for lagerort, cnt, menge in rows:
            by_lagerort[lagerort] = {"count": int(cnt), "menge": float(menge)}

        return {
            "total": total,
            "in_pruefung": in_pruefung,
            "freigegeben": freigegeben,
            "gesperrt": gesperrt,
            "total_menge": float(total_menge),
            "by_lagerort": by_lagerort,
        }


class BankKontoRepository:
    """Repository for operational bank account CRUD."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        kontoart: Optional[str] = None,
        ist_aktiv: Optional[bool] = None,
    ) -> List[BankKonto]:
        query = self.db.query(BankKonto)
        if kontoart:
            query = query.filter(BankKonto.kontoart == kontoart)
        if ist_aktiv is not None:
            query = query.filter(BankKonto.ist_aktiv == ist_aktiv)
        return query.order_by(BankKonto.bank.asc()).offset(skip).limit(limit).all()

    def count(self, kontoart: Optional[str] = None, ist_aktiv: Optional[bool] = None) -> int:
        query = self.db.query(BankKonto)
        if kontoart:
            query = query.filter(BankKonto.kontoart == kontoart)
        if ist_aktiv is not None:
            query = query.filter(BankKonto.ist_aktiv == ist_aktiv)
        return query.count()

    def get_by_id(self, konto_id: str) -> Optional[BankKonto]:
        return self.db.query(BankKonto).filter(BankKonto.id == konto_id).first()

    def get_by_iban(self, iban: str) -> Optional[BankKonto]:
        return self.db.query(BankKonto).filter(BankKonto.iban == iban).first()

    def create(self, konto_data: dict) -> BankKonto:
        konto = BankKonto(id=f"BK-{uuid7()[:8].upper()}", **konto_data)
        self.db.add(konto)
        self.db.commit()
        self.db.refresh(konto)
        return konto

    def update(self, konto_id: str, konto_data: dict) -> Optional[BankKonto]:
        konto = self.get_by_id(konto_id)
        if konto:
            for key, value in konto_data.items():
                setattr(konto, key, value)
            self.db.commit()
            self.db.refresh(konto)
        return konto

    def deactivate(self, konto_id: str) -> bool:
        konto = self.get_by_id(konto_id)
        if not konto:
            return False
        konto.ist_aktiv = False
        konto.status = "inaktiv"
        self.db.commit()
        return True

    def get_salden(self) -> dict:
        active = self.db.query(BankKonto).filter(BankKonto.ist_aktiv == True).all()  # noqa: E712
        gesamt_saldo = sum(float(k.saldo or 0) for k in active)
        nach_kontoart: dict[str, float] = {}
        for konto in active:
            art = konto.kontoart
            nach_kontoart.setdefault(art, 0.0)
            nach_kontoart[art] += float(konto.saldo or 0)
        return {
            "gesamt_saldo": gesamt_saldo,
            "waehrung": "EUR",
            "nach_kontoart": nach_kontoart,
            "anzahl_konten": len(active),
        }


class RahmenvertragRepository:
    """Repository for framework contracts."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, limit: int = 100, status: Optional[str] = None, typ: Optional[str] = None) -> List[Rahmenvertrag]:
        query = self.db.query(Rahmenvertrag)
        if status:
            query = query.filter(Rahmenvertrag.status == status)
        if typ:
            query = query.filter(Rahmenvertrag.typ == typ)
        return query.order_by(desc(Rahmenvertrag.laufzeit_bis)).limit(limit).all()

    def get_by_id(self, vertrag_id: str) -> Optional[Rahmenvertrag]:
        return self.db.query(Rahmenvertrag).filter(Rahmenvertrag.id == vertrag_id).first()

    def get_by_nummer(self, nummer: str) -> Optional[Rahmenvertrag]:
        return self.db.query(Rahmenvertrag).filter(Rahmenvertrag.nummer == nummer).first()

    def create(self, vertrag_data: dict) -> Rahmenvertrag:
        vertrag = Rahmenvertrag(id=f"RV-{uuid7()[:8].upper()}", **vertrag_data)
        self.db.add(vertrag)
        self.db.commit()
        self.db.refresh(vertrag)
        return vertrag

    def update(self, vertrag_id: str, vertrag_data: dict) -> Optional[Rahmenvertrag]:
        vertrag = self.get_by_id(vertrag_id)
        if vertrag:
            for key, value in vertrag_data.items():
                setattr(vertrag, key, value)
            self.db.commit()
            self.db.refresh(vertrag)
        return vertrag

    def delete(self, vertrag_id: str) -> bool:
        vertrag = self.get_by_id(vertrag_id)
        if vertrag:
            self.db.delete(vertrag)
            self.db.commit()
            return True
        return False
