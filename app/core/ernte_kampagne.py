from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class ErnteArt(str, Enum):
    GETREIDE = "getreide"
    RAPS = "raps"
    MAIS = "mais"
    ZUCKERRUEBEN = "zuckerrueben"
    KARTOFFELN = "kartoffeln"

class KampagnenStatus(str, Enum):
    PLANUNG = "planung"
    AKTIV = "aktiv"
    ABGESCHLOSSEN = "abgeschlossen"
    ARCHIVIERT = "archiviert"

_GUELTIGE_UEBERGAENGE: dict[KampagnenStatus, list[KampagnenStatus]] = {
    KampagnenStatus.PLANUNG: [KampagnenStatus.AKTIV],
    KampagnenStatus.AKTIV: [KampagnenStatus.ABGESCHLOSSEN],
    KampagnenStatus.ABGESCHLOSSEN: [KampagnenStatus.ARCHIVIERT],
    KampagnenStatus.ARCHIVIERT: [],
}

class SchlagErnteziel(BaseModel):
    schlag_id: str
    sorte: str
    flaeche_ha: float
    ziel_ertrag_t_ha: float     # Planzahl kg/ha
    schema_version: int = 1

    @property
    def erwartet_gesamt_t(self) -> float:
        return self.flaeche_ha * self.ziel_ertrag_t_ha

class ErnteKampagne(BaseModel):
    kampagne_id: str
    tenant_id: str
    wirtschaftsjahr: int
    ernte_art: ErnteArt
    bezeichnung: str
    schlag_ziele: list[SchlagErnteziel]
    status: KampagnenStatus = KampagnenStatus.PLANUNG
    gestartet_am: Optional[datetime] = None
    abgeschlossen_am: Optional[datetime] = None
    schema_version: int = 1

    @property
    def geplante_gesamtmenge_t(self) -> float:
        return sum(z.erwartet_gesamt_t for z in self.schlag_ziele)

    @property
    def geplante_gesamtflaeche_ha(self) -> float:
        return sum(z.flaeche_ha for z in self.schlag_ziele)

    def fortschritt_pct(self, gelieferte_t: float) -> float:
        """Fortschritt in Prozent: geliefert / geplant * 100."""
        if self.geplante_gesamtmenge_t <= 0:
            return 0.0
        return min(100.0, (gelieferte_t / self.geplante_gesamtmenge_t) * 100)

    def kampagne_starten(self) -> "ErnteKampagne":
        erlaubt = _GUELTIGE_UEBERGAENGE.get(self.status, [])
        if KampagnenStatus.AKTIV not in erlaubt:
            raise ValueError(f"Kampagne kann nicht aus Status {self.status} gestartet werden")
        self.status = KampagnenStatus.AKTIV
        self.gestartet_am = datetime.utcnow()
        return self

    def kampagne_abschliessen(self) -> "ErnteKampagne":
        erlaubt = _GUELTIGE_UEBERGAENGE.get(self.status, [])
        if KampagnenStatus.ABGESCHLOSSEN not in erlaubt:
            raise ValueError(f"Kampagne kann nicht aus Status {self.status} abgeschlossen werden")
        self.status = KampagnenStatus.ABGESCHLOSSEN
        self.abgeschlossen_am = datetime.utcnow()
        return self

    def archivieren(self) -> "ErnteKampagne":
        erlaubt = _GUELTIGE_UEBERGAENGE.get(self.status, [])
        if KampagnenStatus.ARCHIVIERT not in erlaubt:
            raise ValueError(f"Kampagne kann nicht aus Status {self.status} archiviert werden")
        self.status = KampagnenStatus.ARCHIVIERT
        return self

class ErnteKampagneStore(BaseModel):
    kampagnen: dict[str, ErnteKampagne] = {}
    schema_version: int = 1

    def add(self, k: ErnteKampagne) -> ErnteKampagne:
        self.kampagnen[k.kampagne_id] = k
        return k

    def get(self, kampagne_id: str) -> Optional[ErnteKampagne]:
        return self.kampagnen.get(kampagne_id)

    def aktive(self, tenant_id: str) -> list[ErnteKampagne]:
        return [k for k in self.kampagnen.values()
                if k.tenant_id == tenant_id and k.status == KampagnenStatus.AKTIV]

    def by_wirtschaftsjahr(self, tenant_id: str, wirtschaftsjahr: int) -> list[ErnteKampagne]:
        return [k for k in self.kampagnen.values()
                if k.tenant_id == tenant_id and k.wirtschaftsjahr == wirtschaftsjahr]
