from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date
import uuid

class ZertifikatTyp(str, Enum):
    QS_GAP = "qs_gap"
    ISO_22000 = "iso_22000"
    BIO_EU = "bio_eu"
    GLOBALG_AP = "globalg_ap"
    IFS_FOOD = "ifs_food"
    BRC_FOOD = "brc_food"

class ZertifikatStatus(str, Enum):
    GUELTIG = "gueltig"
    ABGELAUFEN = "abgelaufen"
    IN_PRUEFUNG = "in_pruefung"
    WIDERRUFEN = "widerrufen"
    BEANTRAGT = "beantragt"

class Zertifikat(BaseModel):
    zertifikat_id: str
    tenant_id: str
    typ: ZertifikatTyp
    zertifizierungsstelle: str
    zertifikatsnummer: Optional[str] = None
    gueltig_von: date
    gueltig_bis: date
    status: ZertifikatStatus = ZertifikatStatus.GUELTIG
    schema_version: int = 1

    def ist_gueltig(self, datum: Optional[date] = None) -> bool:
        datum = datum or date.today()
        return (
            self.status == ZertifikatStatus.GUELTIG
            and self.gueltig_von <= datum <= self.gueltig_bis
        )

    def tage_bis_ablauf(self, datum: Optional[date] = None) -> int:
        """Positive Werte = noch gueltig, negative = bereits abgelaufen."""
        datum = datum or date.today()
        return (self.gueltig_bis - datum).days

    def aktualisiere_status(self, datum: Optional[date] = None) -> "Zertifikat":
        """Setzt Status auf ABGELAUFEN wenn Datum ueberschritten."""
        datum = datum or date.today()
        if self.status == ZertifikatStatus.GUELTIG and datum > self.gueltig_bis:
            self.status = ZertifikatStatus.ABGELAUFEN
        return self

class ZertifikatStore(BaseModel):
    zertifikate: dict[str, Zertifikat] = {}
    schema_version: int = 1

    def add(self, z: Zertifikat) -> Zertifikat:
        self.zertifikate[z.zertifikat_id] = z
        return z

    def get(self, zertifikat_id: str) -> Optional[Zertifikat]:
        return self.zertifikate.get(zertifikat_id)

    def by_tenant(self, tenant_id: str) -> list[Zertifikat]:
        return [z for z in self.zertifikate.values() if z.tenant_id == tenant_id]

    def gueltige(self, tenant_id: str, datum: Optional[date] = None) -> list[Zertifikat]:
        return [z for z in self.by_tenant(tenant_id) if z.ist_gueltig(datum)]

    def ablaufende_zertifikate(self, tage_vorwarnung: int = 30, datum: Optional[date] = None) -> list[Zertifikat]:
        """Gibt Zertifikate zurueck die innerhalb von tage_vorwarnung ablaufen."""
        datum = datum or date.today()
        return [
            z for z in self.zertifikate.values()
            if z.status == ZertifikatStatus.GUELTIG
            and 0 <= z.tage_bis_ablauf(datum) <= tage_vorwarnung
        ]

    def bereits_abgelaufene(self, datum: Optional[date] = None) -> list[Zertifikat]:
        datum = datum or date.today()
        return [z for z in self.zertifikate.values() if z.tage_bis_ablauf(datum) < 0]
