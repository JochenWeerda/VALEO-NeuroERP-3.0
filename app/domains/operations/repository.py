"""
Repository Pattern for Operations Domain
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timezone
from app.core.uuid7 import prefixed_id

from app.domains.operations.models import (
    Waage, WaageStatus,
    Wiegung,
    Fahrzeug, FahrzeugStatus,
    Fahrer, FahrerStatus,
    FahrzeugTour,
    FuhrparkTerminart,
    FuhrparkRechnung,
    FuhrparkAusgehendesDokument,
    SpeditionFrachttarif,
    Dokument, DokumentStatus,
    DokumentVersion,
    Charge,
    ChargeStatus,
    BankKonto,
    Rahmenvertrag,
    KonContract,
    KonContractLine,
    KonContractMovement,
    KonAuditLog,
    KonNumberRange,
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


class FuhrparkTerminartRepository:
    """Repository for FuhrparkTerminart operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[FuhrparkTerminart]:
        return self.db.query(FuhrparkTerminart).order_by(FuhrparkTerminart.terminart.asc()).all()

    def get_by_id(self, item_id: str) -> Optional[FuhrparkTerminart]:
        return self.db.query(FuhrparkTerminart).filter(FuhrparkTerminart.id == item_id).first()

    def get_by_name(self, terminart: str) -> Optional[FuhrparkTerminart]:
        return self.db.query(FuhrparkTerminart).filter(FuhrparkTerminart.terminart == terminart).first()

    def create(self, payload: dict) -> FuhrparkTerminart:
        row = FuhrparkTerminart(id=f"FTA-{str(__import__('uuid').uuid4())[:8].upper()}", **payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update(self, item_id: str, payload: dict) -> Optional[FuhrparkTerminart]:
        row = self.get_by_id(item_id)
        if row:
            for key, value in payload.items():
                setattr(row, key, value)
            self.db.commit()
            self.db.refresh(row)
        return row

    def delete(self, item_id: str) -> bool:
        row = self.get_by_id(item_id)
        if row:
            self.db.delete(row)
            self.db.commit()
            return True
        return False


class FuhrparkRechnungRepository:
    """Repository for FuhrparkRechnung operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 200) -> List[FuhrparkRechnung]:
        return (
            self.db.query(FuhrparkRechnung)
            .order_by(FuhrparkRechnung.datum.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, item_id: str) -> Optional[FuhrparkRechnung]:
        return self.db.query(FuhrparkRechnung).filter(FuhrparkRechnung.id == item_id).first()

    def get_by_rechnungs_nr(self, rechnungs_nr: str) -> Optional[FuhrparkRechnung]:
        return self.db.query(FuhrparkRechnung).filter(FuhrparkRechnung.rechnungs_nr == rechnungs_nr).first()

    def create(self, payload: dict) -> FuhrparkRechnung:
        row = FuhrparkRechnung(id=f"FR-{str(__import__('uuid').uuid4())[:8].upper()}", **payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update(self, item_id: str, payload: dict) -> Optional[FuhrparkRechnung]:
        row = self.get_by_id(item_id)
        if row:
            for key, value in payload.items():
                setattr(row, key, value)
            self.db.commit()
            self.db.refresh(row)
        return row

    def delete(self, item_id: str) -> bool:
        row = self.get_by_id(item_id)
        if row:
            self.db.delete(row)
            self.db.commit()
            return True
        return False


class FuhrparkAusgehendesDokumentRepository:
    """Repository for FuhrparkAusgehendesDokument operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 200) -> List[FuhrparkAusgehendesDokument]:
        return (
            self.db.query(FuhrparkAusgehendesDokument)
            .order_by(FuhrparkAusgehendesDokument.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, item_id: str) -> Optional[FuhrparkAusgehendesDokument]:
        return self.db.query(FuhrparkAusgehendesDokument).filter(FuhrparkAusgehendesDokument.id == item_id).first()

    def create(self, payload: dict) -> FuhrparkAusgehendesDokument:
        row = FuhrparkAusgehendesDokument(id=f"FAD-{str(__import__('uuid').uuid4())[:8].upper()}", **payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update(self, item_id: str, payload: dict) -> Optional[FuhrparkAusgehendesDokument]:
        row = self.get_by_id(item_id)
        if row:
            for key, value in payload.items():
                setattr(row, key, value)
            self.db.commit()
            self.db.refresh(row)
        return row

    def delete(self, item_id: str) -> bool:
        row = self.get_by_id(item_id)
        if row:
            self.db.delete(row)
            self.db.commit()
            return True
        return False


class SpeditionFrachttarifRepository:
    """Repository for SpeditionFrachttarif (PLZ-based freight prices)."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 500, aktiv_only: bool = False) -> List[SpeditionFrachttarif]:
        q = self.db.query(SpeditionFrachttarif)
        if aktiv_only:
            q = q.filter(SpeditionFrachttarif.aktiv.is_(True))
        return q.order_by(SpeditionFrachttarif.spediteur.asc(), SpeditionFrachttarif.plz_von.asc()).offset(skip).limit(limit).all()

    def get_by_id(self, item_id: str) -> Optional[SpeditionFrachttarif]:
        return self.db.query(SpeditionFrachttarif).filter(SpeditionFrachttarif.id == item_id).first()

    def create(self, payload: dict) -> SpeditionFrachttarif:
        row = SpeditionFrachttarif(id=f"SFT-{str(__import__('uuid').uuid4())[:8].upper()}", **payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update(self, item_id: str, payload: dict) -> Optional[SpeditionFrachttarif]:
        row = self.get_by_id(item_id)
        if row:
            for key, value in payload.items():
                setattr(row, key, value)
            self.db.commit()
            self.db.refresh(row)
        return row

    def delete(self, item_id: str) -> bool:
        row = self.get_by_id(item_id)
        if row:
            self.db.delete(row)
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
            id=prefixed_id("CH"),
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
        konto = BankKonto(id=prefixed_id("BK"), **konto_data)
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
        vertrag = Rahmenvertrag(id=prefixed_id("RV"), **vertrag_data)
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


class KontraktRepository:
    """Repository for valeo Kontrakte."""

    def __init__(self, db: Session):
        self.db = db

    def list_contracts(
        self,
        tenant_id: str,
        *,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        contract_type: Optional[str] = None,
        party_id: Optional[str] = None,
        article_id: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        query: Optional[str] = None,
        include_done: bool = True,
    ) -> tuple[list[KonContract], int]:
        q = self.db.query(KonContract).filter(KonContract.tenant_id == tenant_id)
        if status:
            q = q.filter(KonContract.status == status)
        if contract_type:
            q = q.filter(KonContract.contract_type == contract_type)
        if party_id:
            q = q.filter(KonContract.party_id == party_id)
        if article_id:
            q = q.join(KonContractLine, KonContractLine.contract_id == KonContract.contract_id).filter(
                KonContractLine.article_id == article_id
            )
        if valid_from:
            q = q.filter(KonContract.valid_to >= valid_from)
        if valid_to:
            q = q.filter(KonContract.valid_from <= valid_to)
        if not include_done:
            q = q.filter(KonContract.status != "ERLEDIGT")
        if query:
            like = f"%{query.strip()}%"
            q = q.filter(
                (KonContract.contract_no.ilike(like))
                | (KonContract.party_id.ilike(like))
            )
        total = q.count()
        items = q.order_by(desc(KonContract.updated_at), desc(KonContract.created_at)).offset(skip).limit(limit).all()
        return items, total

    def get_contract(self, tenant_id: str, contract_id: str) -> Optional[KonContract]:
        return (
            self.db.query(KonContract)
            .filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id)
            .first()
        )

    def get_by_no(self, tenant_id: str, contract_no: str) -> Optional[KonContract]:
        return (
            self.db.query(KonContract)
            .filter(KonContract.tenant_id == tenant_id, KonContract.contract_no == contract_no)
            .first()
        )

    def get_lines(self, tenant_id: str, contract_id: str) -> list[KonContractLine]:
        return (
            self.db.query(KonContractLine)
            .filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id)
            .order_by(KonContractLine.position_no.asc())
            .all()
        )

    def get_movements(
        self,
        tenant_id: str,
        contract_id: str,
        *,
        include_archived: bool = False,
        only_invoiced: Optional[bool] = None,
        article_id: Optional[str] = None,
    ) -> list[KonContractMovement]:
        q = (
            self.db.query(KonContractMovement)
            .outerjoin(KonContractLine, KonContractMovement.line_id == KonContractLine.line_id)
            .filter(KonContractMovement.tenant_id == tenant_id, KonContractMovement.contract_id == contract_id)
        )
        if not include_archived:
            q = q.filter(KonContractMovement.is_archived.is_(False))
        if only_invoiced is not None:
            q = q.filter(KonContractMovement.is_invoiced.is_(only_invoiced))
        if article_id:
            q = q.filter(KonContractLine.article_id == article_id)
        return q.order_by(desc(KonContractMovement.movement_date)).all()

    def get_audit_logs(self, tenant_id: str, entity_id: str) -> list[KonAuditLog]:
        return (
            self.db.query(KonAuditLog)
            .filter(KonAuditLog.tenant_id == tenant_id, KonAuditLog.entity_id == entity_id)
            .order_by(desc(KonAuditLog.changed_at))
            .all()
        )

    def get_number_range(self, tenant_id: str, contract_type: str, branch_id: Optional[str]) -> Optional[KonNumberRange]:
        return (
            self.db.query(KonNumberRange)
            .filter(
                KonNumberRange.tenant_id == tenant_id,
                KonNumberRange.contract_type == contract_type,
                KonNumberRange.branch_id.is_(branch_id) if branch_id is None else KonNumberRange.branch_id == branch_id,
            )
            .first()
        )
