"""
Finance Repositories
Database operations for finance entities
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from decimal import Decimal
import uuid
from datetime import datetime

from .models import OffenerPosten, Buchung, Konto, Anlage


class OffenerPostenRepository:
    """Repository for Offene Posten (Debitoren/Kreditoren)"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, op_data: dict, tenant_id: str) -> OffenerPosten:
        """Create new Offener Posten"""
        op = OffenerPosten(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **op_data
        )
        self.db.add(op)
        self.db.commit()
        self.db.refresh(op)
        return op

    def get_by_id(self, op_id: str, tenant_id: str) -> Optional[OffenerPosten]:
        """Get Offener Posten by ID"""
        return self.db.get(OffenerPosten, op_id)

    def get_debitoren(self, tenant_id: str, ueberfaellig: Optional[bool] = None,
                     mahn_stufe: Optional[int] = None) -> List[OffenerPosten]:
        """Get Debitoren (receivables)"""
        query = select(OffenerPosten).where(
            and_(OffenerPosten.tenant_id == tenant_id,
                 OffenerPosten.kunde_id.isnot(None))
        )

        if ueberfaellig is not None:
            heute = date.today()
            if ueberfaellig:
                query = query.where(OffenerPosten.faelligkeit < heute)
            else:
                query = query.where(OffenerPosten.faelligkeit >= heute)

        if mahn_stufe is not None:
            query = query.where(OffenerPosten.mahn_stufe == mahn_stufe)

        return list(self.db.execute(query).scalars().all())

    def get_kreditoren(self, tenant_id: str, zahlbar: Optional[bool] = None) -> List[OffenerPosten]:
        """Get Kreditoren (payables)"""
        query = select(OffenerPosten).where(
            and_(OffenerPosten.tenant_id == tenant_id,
                 OffenerPosten.lieferant_id.isnot(None))
        )

        if zahlbar is not None:
            query = query.where(OffenerPosten.zahlbar == zahlbar)

        return list(self.db.execute(query).scalars().all())

    def update_mahn_stufe(self, op_id: str, tenant_id: str, new_stufe: int) -> bool:
        """Update Mahnstufen"""
        op = self.get_by_id(op_id, tenant_id)
        if op:
            op.mahn_stufe = new_stufe
            op.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def update_zahlung(self, op_id: str, tenant_id: str, betrag: Decimal) -> bool:
        """Update payment amount"""
        op = self.get_by_id(op_id, tenant_id)
        if op:
            op.offen -= betrag
            if op.offen <= 0:
                op.offen = Decimal("0.00")
            op.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False


class BuchungRepository:
    """Repository for Buchungen (Journal Entries)"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, buchung_data: dict, tenant_id: str) -> Buchung:
        """Create new Buchung"""
        buchung = Buchung(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **buchung_data
        )
        self.db.add(buchung)
        self.db.commit()
        self.db.refresh(buchung)
        return buchung

    def get_by_filters(self, tenant_id: str, datum_von: Optional[date] = None,
                      datum_bis: Optional[date] = None, belegart: Optional[str] = None) -> List[Buchung]:
        """Get Buchungen with filters"""
        query = select(Buchung).where(Buchung.tenant_id == tenant_id)

        if datum_von:
            query = query.where(Buchung.datum >= datum_von)
        if datum_bis:
            query = query.where(Buchung.datum <= datum_bis)
        if belegart:
            query = query.where(Buchung.belegart == belegart)

        return list(self.db.execute(query.order_by(Buchung.datum.desc())).scalars().all())

    def update_konten_saldi(self, tenant_id: str, soll_konto: str, haben_konto: str, betrag: Decimal):
        """Update account balances after booking"""
        # Update Soll-Konto (increase)
        soll = self.db.execute(
            select(Konto).where(and_(Konto.tenant_id == tenant_id, Konto.kontonummer == soll_konto))
        ).scalar_one_or_none()
        if soll:
            soll.saldo += betrag

        # Update Haben-Konto (decrease)
        haben = self.db.execute(
            select(Konto).where(and_(Konto.tenant_id == tenant_id, Konto.kontonummer == haben_konto))
        ).scalar_one_or_none()
        if haben:
            haben.saldo -= betrag

        self.db.commit()


class KontoRepository:
    """Repository for Konten (Accounts)"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, konto_data: dict, tenant_id: str) -> Konto:
        """Create new Konto"""
        konto = Konto(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **konto_data
        )
        self.db.add(konto)
        self.db.commit()
        self.db.refresh(konto)
        return konto

    def get_all(self, tenant_id: str, typ: Optional[str] = None) -> List[Konto]:
        """Get all Konten, optionally filtered by type"""
        query = select(Konto).where(Konto.tenant_id == tenant_id)
        if typ:
            query = query.where(Konto.typ == typ)
        return list(self.db.execute(query).scalars().all())

    def get_by_nummer(self, kontonummer: str, tenant_id: str) -> Optional[Konto]:
        """Get Konto by number"""
        return self.db.execute(
            select(Konto).where(and_(Konto.tenant_id == tenant_id, Konto.kontonummer == kontonummer))
        ).scalar_one_or_none()


class AnlageRepository:
    """Repository for Anlagen (Fixed Assets)"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, anlage_data: dict, tenant_id: str) -> Anlage:
        """Create new Anlage"""
        anlage = Anlage(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **anlage_data
        )
        self.db.add(anlage)
        self.db.commit()
        self.db.refresh(anlage)
        return anlage

    def get_all(self, tenant_id: str) -> List[Anlage]:
        """Get all Anlagen"""
        return list(self.db.execute(
            select(Anlage).where(Anlage.tenant_id == tenant_id)
        ).scalars().all())

    def get_by_id(self, anlage_id: str, tenant_id: str) -> Optional[Anlage]:
        """Get Anlage by ID"""
        return self.db.execute(
            select(Anlage).where(and_(Anlage.tenant_id == tenant_id, Anlage.id == anlage_id))
        ).scalar_one_or_none()

    def berechne_afa(self, anlage_id: str, tenant_id: str, jahr: int) -> Optional[dict]:
        """Calculate depreciation for an asset"""
        anlage = self.get_by_id(anlage_id, tenant_id)
        if not anlage:
            return None

        jahres_afa = anlage.anschaffungswert * (anlage.afa_satz / Decimal("100"))

        return {
            "anlage_id": anlage_id,
            "jahr": jahr,
            "afa_satz": anlage.afa_satz,
            "jahres_afa": jahres_afa,
            "kumulierte_afa": anlage.kumulierte_afa,
            "buchwert": anlage.buchwert,
        }