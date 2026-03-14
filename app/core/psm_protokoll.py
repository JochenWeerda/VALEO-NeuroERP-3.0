from __future__ import annotations
from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid

class PsmAnwendungProtokoll(BaseModel):
    """GoBD-konformes PSM-Anwendungsprotokoll nach § 11 PflSchG."""
    protokoll_id: str
    tenant_id: str
    schlag_id: str
    anwendungsdatum: date
    praeparat_name: str
    wirkstoff: str
    aufwandmenge_l_ha: float
    sachkunde_nr: str            # Pflicht: Sachkundeausweis des Anwenders
    wasser_schutzgebiet: bool = False
    wartezeit_tage: int | None = None
    flaeche_ha: float
    zulassungsnummer: str | None = None
    schema_version: int = 1

    def ist_gobd_vollstaendig(self) -> bool:
        """Prüft ob alle GoBD-Pflichtfelder für PSM-Tagebuch vorhanden sind."""
        return bool(
            self.sachkunde_nr
            and self.praeparat_name
            and self.wirkstoff
            and self.aufwandmenge_l_ha > 0
            and self.flaeche_ha > 0
        )
