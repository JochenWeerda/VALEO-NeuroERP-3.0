from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid

class SiloStatus(str, Enum):
    LEER = "leer"
    TEILBELEGT = "teilbelegt"
    VOLL = "voll"
    GESPERRT = "gesperrt"

class IoTMeasurement(BaseModel):
    """IoT-Telemetriemessung für Silozelle."""
    measurement_id: str
    silo_id: str
    timestamp: datetime
    temperatur_celsius: float
    feuchte_pct: float
    fuellstand_pct: float       # 0–100
    schema_version: int = 1

class SiloCell(BaseModel):
    """Einzelne Silozelle / Silo-Kammer."""
    silo_id: str
    tenant_id: str
    bezeichnung: str
    kapazitaet_t: float
    aktuell_eingelagert_t: float = 0.0
    sorte: Optional[str] = None
    status: SiloStatus = SiloStatus.LEER
    letzte_messung: Optional[IoTMeasurement] = None
    schema_version: int = 1

    @property
    def fuellstand_pct(self) -> float:
        if self.kapazitaet_t <= 0:
            return 0.0
        return min(100.0, (self.aktuell_eingelagert_t / self.kapazitaet_t) * 100)

    @property
    def freie_kapazitaet_t(self) -> float:
        return max(0.0, self.kapazitaet_t - self.aktuell_eingelagert_t)

    def aktualisiere_status(self) -> "SiloCell":
        if self.status == SiloStatus.GESPERRT:
            return self
        if self.aktuell_eingelagert_t <= 0:
            self.status = SiloStatus.LEER
        elif self.fuellstand_pct >= 95:
            self.status = SiloStatus.VOLL
        else:
            self.status = SiloStatus.TEILBELEGT
        return self

class TransferTyp(str, Enum):
    EINLAGERUNG = "einlagerung"
    AUSLAGERUNG = "auslagerung"
    UMLAGERUNG = "umlagerung"

class SiloTransfer(BaseModel):
    transfer_id: str
    tenant_id: str
    silo_id: str
    transfer_typ: TransferTyp
    menge_t: float
    sorte: str
    zeitpunkt: datetime
    beleg_nr: Optional[str] = None    # Referenz auf Annahmebeleg / Lieferschein
    schema_version: int = 1

class SiloCellStore(BaseModel):
    """In-Memory Store für Silozellen (Wave-6, kein DB-Zugriff)."""
    zellen: dict[str, SiloCell] = {}
    transfers: list[SiloTransfer] = []
    schema_version: int = 1

    def add_zelle(self, zelle: SiloCell) -> SiloCell:
        self.zellen[zelle.silo_id] = zelle
        return zelle

    def get_zelle(self, silo_id: str) -> Optional[SiloCell]:
        return self.zellen.get(silo_id)

    def einlagern(self, silo_id: str, menge_t: float, sorte: str, beleg_nr: Optional[str] = None) -> SiloTransfer:
        zelle = self.zellen.get(silo_id)
        if zelle is None:
            raise ValueError(f"Silozelle {silo_id} nicht gefunden")
        if zelle.status == SiloStatus.GESPERRT:
            raise ValueError(f"Silozelle {silo_id} ist gesperrt")
        if menge_t > zelle.freie_kapazitaet_t:
            raise ValueError(f"Kapazität überschritten: {menge_t}t > {zelle.freie_kapazitaet_t}t frei")
        zelle.aktuell_eingelagert_t += menge_t
        if zelle.sorte is None:
            zelle.sorte = sorte
        zelle.aktualisiere_status()
        transfer = SiloTransfer(
            transfer_id=str(uuid.uuid4()),
            tenant_id=zelle.tenant_id,
            silo_id=silo_id,
            transfer_typ=TransferTyp.EINLAGERUNG,
            menge_t=menge_t,
            sorte=sorte,
            zeitpunkt=datetime.utcnow(),
            beleg_nr=beleg_nr,
        )
        self.transfers.append(transfer)
        return transfer

    def auslagern(self, silo_id: str, menge_t: float, beleg_nr: Optional[str] = None) -> SiloTransfer:
        zelle = self.zellen.get(silo_id)
        if zelle is None:
            raise ValueError(f"Silozelle {silo_id} nicht gefunden")
        if menge_t > zelle.aktuell_eingelagert_t:
            raise ValueError(f"Nicht genug eingelagert: {menge_t}t > {zelle.aktuell_eingelagert_t}t")
        sorte = zelle.sorte or "unbekannt"
        zelle.aktuell_eingelagert_t -= menge_t
        if zelle.aktuell_eingelagert_t <= 0:
            zelle.sorte = None
        zelle.aktualisiere_status()
        transfer = SiloTransfer(
            transfer_id=str(uuid.uuid4()),
            tenant_id=zelle.tenant_id,
            silo_id=silo_id,
            transfer_typ=TransferTyp.AUSLAGERUNG,
            menge_t=menge_t,
            sorte=sorte,
            zeitpunkt=datetime.utcnow(),
            beleg_nr=beleg_nr,
        )
        self.transfers.append(transfer)
        return transfer

    def transfers_fuer_silo(self, silo_id: str) -> list[SiloTransfer]:
        return [t for t in self.transfers if t.silo_id == silo_id]

    def gesamtbestand_t(self, tenant_id: str) -> float:
        return sum(z.aktuell_eingelagert_t for z in self.zellen.values() if z.tenant_id == tenant_id)
