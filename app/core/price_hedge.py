from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date
import uuid

class TerminmarktProdukt(str, Enum):
    WEIZEN_MATIF = "weizen_matif"
    MAIS_MATIF = "mais_matif"
    RAPS_MATIF = "raps_matif"
    SOJASCHROT_CBOT = "sojaschrot_cbot"
    FUTTERGERSTE_MATIF = "futtergerste_matif"

class HedgeTyp(str, Enum):
    LONG = "long"
    SHORT = "short"
    OPTION_CALL = "option_call"
    OPTION_PUT = "option_put"

class HedgeStatus(str, Enum):
    OFFEN = "offen"
    GESCHLOSSEN = "geschlossen"
    VERFALLEN = "verfallen"

class HedgeReference(BaseModel):
    hedge_id: str
    tenant_id: str
    kontrakt_id: Optional[str] = None
    produkt: TerminmarktProdukt
    typ: HedgeTyp
    menge_t: float
    basis_preis_eur_t: float
    verfall_datum: date
    status: HedgeStatus = HedgeStatus.OFFEN
    broker_referenz: Optional[str] = None
    schema_version: int = 1

    @property
    def wert_eur(self) -> float:
        return self.menge_t * self.basis_preis_eur_t

    @property
    def ist_aktiv(self) -> bool:
        return self.status == HedgeStatus.OFFEN

class KontraktHedgeBindung(BaseModel):
    """Verknuepft einen KonContractLot mit einer oder mehreren HedgeReferences."""
    bindung_id: str
    tenant_id: str
    lot_id: str             # KonContractLot.lot_id aus Wave 6
    kontrakt_id: str
    hedge_ids: list[str]    # HedgeReference.hedge_id(s)
    lot_menge_t: float
    gesicherte_menge_t: float
    schema_version: int = 1

    @property
    def hedge_quote_pct(self) -> float:
        """Absicherungsquote 0-100%."""
        if self.lot_menge_t <= 0:
            return 0.0
        return min(100.0, (self.gesicherte_menge_t / self.lot_menge_t) * 100)

    @property
    def ist_vollstaendig_gesichert(self) -> bool:
        return self.hedge_quote_pct >= 100.0

def berechne_hedge_quote(kontrakt_menge_t: float, hedge_menge_t: float) -> float:
    """Berechnet Absicherungsquote in Prozent (0-100)."""
    if kontrakt_menge_t <= 0:
        return 0.0
    return min(100.0, (hedge_menge_t / kontrakt_menge_t) * 100)

class HedgeStore(BaseModel):
    hedges: dict[str, HedgeReference] = {}
    bindungen: dict[str, KontraktHedgeBindung] = {}
    schema_version: int = 1

    def add_hedge(self, hedge: HedgeReference) -> HedgeReference:
        self.hedges[hedge.hedge_id] = hedge
        return hedge

    def add_bindung(self, bindung: KontraktHedgeBindung) -> KontraktHedgeBindung:
        self.bindungen[bindung.bindung_id] = bindung
        return bindung

    def get_hedge(self, hedge_id: str) -> Optional[HedgeReference]:
        return self.hedges.get(hedge_id)

    def aktive_hedges(self, tenant_id: str) -> list[HedgeReference]:
        return [h for h in self.hedges.values()
                if h.tenant_id == tenant_id and h.ist_aktiv]

    def bindung_fuer_lot(self, lot_id: str) -> Optional[KontraktHedgeBindung]:
        return next((b for b in self.bindungen.values() if b.lot_id == lot_id), None)
