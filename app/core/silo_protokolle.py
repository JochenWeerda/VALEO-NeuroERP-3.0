from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date, datetime

class ReinigungsArt(str, Enum):
    BESEN = "besen"
    SAUG = "saug"
    HOCHDRUCK = "hochdruck"
    CHEMISCH = "chemisch"

class SiloReinigungsprotokoll(BaseModel):
    """GoBD-konformes Reinigungsprotokoll bei Warenwechsel im Silo."""
    protokoll_id: str
    silo_id: str
    tenant_id: str
    datum: date
    vorige_ware: str
    naechste_ware: str
    reinigungsart: ReinigungsArt
    durchgefuehrt_von: str          # Name oder Mitarbeiter-ID
    kontrolliert_von: Optional[str] = None
    gobd_beleg_id: Optional[str] = None
    bemerkung: Optional[str] = None
    schema_version: int = 1

    def ist_gobd_vollstaendig(self) -> bool:
        """Prueft ob alle GoBD-Pflichtfelder fuer das Reinigungsprotokoll vorhanden sind."""
        return bool(
            self.silo_id
            and self.datum
            and self.vorige_ware
            and self.naechste_ware
            and self.durchgefuehrt_von
            and self.reinigungsart
        )

class TrocknungsProtokoll(BaseModel):
    """Trocknungsprotokoll mit IoT-Messkette (Ein-/Ausgangswerte)."""
    lauf_id: str
    silo_id: str
    tenant_id: str
    charge_id: str
    sorte: str
    eingang_feuchte_pct: float
    ausgang_feuchte_pct: float
    eingang_temp_c: float
    ausgang_temp_c: float
    energie_kwh: float
    dauer_h: float
    getrocknet_t: float
    start_zeitpunkt: datetime
    ende_zeitpunkt: Optional[datetime] = None
    iot_device_id: Optional[str] = None       # Referenz auf IoT-Geraet (Wave 3 AP3)
    schema_version: int = 1

    @property
    def trocknungseffekt_pct(self) -> float:
        """Feuchtigkeitsreduktion in Prozentpunkten."""
        return self.eingang_feuchte_pct - self.ausgang_feuchte_pct

    @property
    def energie_je_t_kwh(self) -> float:
        """Energieverbrauch pro Tonne getrockneter Ware."""
        if self.getrocknet_t <= 0:
            return 0.0
        return self.energie_kwh / self.getrocknet_t

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.ende_zeitpunkt is not None

    def ist_wirtschaftlich(self, max_kwh_je_t: float = 100.0) -> bool:
        """Prueft ob der Trocknungslauf wirtschaftlich im Normbereich liegt."""
        return self.energie_je_t_kwh <= max_kwh_je_t

class SiloProtokolleStore(BaseModel):
    reinigungen: dict[str, SiloReinigungsprotokoll] = {}
    trocknungen: dict[str, TrocknungsProtokoll] = {}
    schema_version: int = 1

    def add_reinigung(self, p: SiloReinigungsprotokoll) -> SiloReinigungsprotokoll:
        self.reinigungen[p.protokoll_id] = p
        return p

    def add_trocknung(self, p: TrocknungsProtokoll) -> TrocknungsProtokoll:
        self.trocknungen[p.lauf_id] = p
        return p

    def reinigungen_fuer_silo(self, silo_id: str) -> list[SiloReinigungsprotokoll]:
        return [p for p in self.reinigungen.values() if p.silo_id == silo_id]

    def trocknungen_fuer_silo(self, silo_id: str) -> list[TrocknungsProtokoll]:
        return [p for p in self.trocknungen.values() if p.silo_id == silo_id]
