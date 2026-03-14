from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date, datetime
import uuid

class ReklamationsTyp(str, Enum):
    QUALITAET = "qualitaet"
    MENGE = "menge"
    PREIS = "preis"
    LIEFERTERMIN = "liefertermin"
    SONSTIGE = "sonstige"

class ReklamationsStatus(str, Enum):
    OFFEN = "offen"
    IN_PRUEFUNG = "in_pruefung"
    TEILWEISE_ANERKANNT = "teilweise_anerkannt"
    ANERKANNT = "anerkannt"
    ABGELEHNT = "abgelehnt"
    GESCHLOSSEN = "geschlossen"

# Erlaubte Statusübergänge
_GUELTIGE_UEBERGAENGE: dict[ReklamationsStatus, list[ReklamationsStatus]] = {
    ReklamationsStatus.OFFEN: [ReklamationsStatus.IN_PRUEFUNG, ReklamationsStatus.ABGELEHNT],
    ReklamationsStatus.IN_PRUEFUNG: [
        ReklamationsStatus.ANERKANNT,
        ReklamationsStatus.TEILWEISE_ANERKANNT,
        ReklamationsStatus.ABGELEHNT,
    ],
    ReklamationsStatus.TEILWEISE_ANERKANNT: [ReklamationsStatus.GESCHLOSSEN],
    ReklamationsStatus.ANERKANNT: [ReklamationsStatus.GESCHLOSSEN],
    ReklamationsStatus.ABGELEHNT: [ReklamationsStatus.GESCHLOSSEN],
    ReklamationsStatus.GESCHLOSSEN: [],
}

class ReklamationsPosition(BaseModel):
    artikel_id: str
    charge_id: Optional[str] = None
    beanstandete_menge: float
    anerkannte_menge: float = 0.0
    beanstandeter_wert_eur: float
    begruendung: str
    schema_version: int = 1

class Reklamation(BaseModel):
    reklamation_id: str
    tenant_id: str
    kontrakt_id: Optional[str] = None
    lieferant_id: str
    typ: ReklamationsTyp
    status: ReklamationsStatus = ReklamationsStatus.OFFEN
    positionen: list[ReklamationsPosition]
    zustaendiger: str
    frist_datum: date
    erstellt_am: datetime
    gobd_beleg_id: Optional[str] = None
    schema_version: int = 1

    @property
    def gesamtwert_beanstandet_eur(self) -> float:
        return sum(p.beanstandeter_wert_eur for p in self.positionen)

    @property
    def gesamtwert_anerkannt_eur(self) -> float:
        return sum(p.anerkannte_menge * (p.beanstandeter_wert_eur / p.beanstandete_menge)
                   for p in self.positionen if p.beanstandete_menge > 0)

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status == ReklamationsStatus.GESCHLOSSEN

class ReklamationZustandsmaschine:
    @staticmethod
    def transition(reklamation: Reklamation, neuer_status: ReklamationsStatus) -> Reklamation:
        erlaubt = _GUELTIGE_UEBERGAENGE.get(reklamation.status, [])
        if neuer_status not in erlaubt:
            raise ValueError(
                f"Ungültiger Übergang: {reklamation.status} → {neuer_status}. "
                f"Erlaubt: {[s.value for s in erlaubt]}"
            )
        reklamation.status = neuer_status
        return reklamation

class ReklamationStore(BaseModel):
    reklamationen: dict[str, Reklamation] = {}
    schema_version: int = 1

    def add(self, r: Reklamation) -> Reklamation:
        self.reklamationen[r.reklamation_id] = r
        return r

    def get(self, reklamation_id: str) -> Optional[Reklamation]:
        return self.reklamationen.get(reklamation_id)

    def by_lieferant(self, lieferant_id: str) -> list[Reklamation]:
        return [r for r in self.reklamationen.values() if r.lieferant_id == lieferant_id]

    def offene(self, tenant_id: str) -> list[Reklamation]:
        return [r for r in self.reklamationen.values()
                if r.tenant_id == tenant_id and not r.ist_abgeschlossen]
