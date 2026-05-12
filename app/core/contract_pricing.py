from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date
import uuid

class PreisTyp(str, Enum):
    FEST = "fest"
    BASIS = "basis"
    FORMEL = "formel"
    MARKT = "markt"

class PriceMatrixEintrag(BaseModel):
    sorte: str
    qualitaet: str               # z.B. "A", "B", "C"
    preis_eur_t: float
    gueltig_von: date
    gueltig_bis: date
    preis_typ: PreisTyp = PreisTyp.FEST
    schema_version: int = 1

class PriceMatrix(BaseModel):
    matrix_id: str
    tenant_id: str
    wirtschaftsjahr: int
    eintraege: list[PriceMatrixEintrag]
    schema_version: int = 1

    def get_preis(self, sorte: str, qualitaet: str, stichtag: date) -> Optional[float]:
        """Gibt den gültigen Preis für Sorte/Qualität an einem Stichtag zurück."""
        for e in self.eintraege:
            if (e.sorte == sorte
                    and e.qualitaet == qualitaet
                    and e.gueltig_von <= stichtag <= e.gueltig_bis):
                return e.preis_eur_t
        return None

    def alle_preise_am_stichtag(self, stichtag: date) -> list[PriceMatrixEintrag]:
        """Alle gültigen Einträge an einem Stichtag."""
        return [e for e in self.eintraege if e.gueltig_von <= stichtag <= e.gueltig_bis]

class KonContractLot(BaseModel):
    """Einzelpartie / Los innerhalb eines Kontrakts."""
    lot_id: str
    tenant_id: str
    kontrakt_id: str
    lieferant_id: str
    menge_t: float
    sorte: str
    qualitaet: str
    vereinbarter_preis_eur_t: float
    preis_typ: PreisTyp
    lieferdatum_soll: date
    lieferdatum_ist: Optional[date] = None
    abgerechnet: bool = False
    schema_version: int = 1

    @property
    def wert_eur(self) -> float:
        return self.menge_t * self.vereinbarter_preis_eur_t

    @property
    def ist_geliefert(self) -> bool:
        return self.lieferdatum_ist is not None

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.ist_geliefert and self.abgerechnet

class KonContractLotStore(BaseModel):
    """In-Memory Store für Lots (Wave-6, kein DB-Zugriff)."""
    lots: dict[str, KonContractLot] = {}
    schema_version: int = 1

    def add(self, lot: KonContractLot) -> KonContractLot:
        self.lots[lot.lot_id] = lot
        return lot

    def get(self, lot_id: str) -> Optional[KonContractLot]:
        return self.lots.get(lot_id)

    def by_kontrakt(self, kontrakt_id: str) -> list[KonContractLot]:
        return [line_item for line_item in self.lots.values() if line_item.kontrakt_id == kontrakt_id]

    def offene_lots(self, tenant_id: str) -> list[KonContractLot]:
        return [line_item for line_item in self.lots.values() if line_item.tenant_id == tenant_id and not line_item.ist_abgeschlossen]
