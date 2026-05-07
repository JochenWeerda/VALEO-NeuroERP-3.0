"""ORM: Streckengeschaefte (M-11 Strecke / Drop-Ship Pass-Through)."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Date, DateTime, Numeric, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class Streckengeschaeft(Base):
    __tablename__ = "streckengeschaefte"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    strecke_nr = Column(String(64), nullable=False, index=True)

    datum = Column(Date, nullable=False)
    niederlassung = Column(String(255), nullable=False, default="")
    partie_nr = Column(String(128), nullable=False, default="")
    kostenstelle = Column(String(128), nullable=False, default="")
    lagerhalle = Column(String(128), nullable=False, default="")
    nls_nr = Column(String(64), nullable=False, default="")
    erledigt = Column(Boolean, nullable=False, default=False)

    lieferant_name = Column(String(255), nullable=False, default="")
    lieferant_nr = Column(String(64), nullable=False, default="")
    kontrakt_nr = Column(String(64), nullable=False, default="")
    artikel = Column(String(512), nullable=False, default="")

    netto = Column(Numeric(16, 2), nullable=False, default=0)
    mwst = Column(Numeric(16, 2), nullable=False, default=0)
    brutto = Column(Numeric(16, 2), nullable=False, default=0)

    rechnungsnr = Column(String(128), nullable=False, default="")
    bediener = Column(String(128), nullable=False, default="")
    notiz = Column(Text, nullable=False, default="")

    erstellt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "strecke_nr", name="uq_streckengeschaefte_tenant_strecke_nr"),
    )
