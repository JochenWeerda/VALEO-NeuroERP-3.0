from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid

class AusnahmeKategorie(str, Enum):
    PREIS_AUSNAHME = "preis_ausnahme"
    MENGEN_AUSNAHME = "mengen_ausnahme"
    QUALITAETS_AUSNAHME = "qualitaets_ausnahme"
    SICHERHEITS_AUSNAHME = "sicherheits_ausnahme"
    KOMPETENZ_AUSNAHME = "kompetenz_ausnahme"

class AusnahmeStatus(str, Enum):
    BEANTRAGT = "beantragt"
    GENEHMIGT = "genehmigt"
    ABGELEHNT = "abgelehnt"

class AusnahmeAntrag(BaseModel):
    antrag_id: str
    workflow_instance_id: str
    kategorie: AusnahmeKategorie
    begruendung: str
    beantragende_rolle: str
    schwellenwert_ueberschritten: bool
    betrag_eur: Optional[float] = None          # bei Preis-/Mengenausnahme
    genehmigt_von: Optional[str] = None
    genehmigt_am: Optional[datetime] = None
    status: AusnahmeStatus = AusnahmeStatus.BEANTRAGT
    schema_version: int = 1

    def genehmigen(self, genehmiger: str) -> "AusnahmeAntrag":
        self.genehmigt_von = genehmiger
        self.genehmigt_am = datetime.utcnow()
        self.status = AusnahmeStatus.GENEHMIGT
        return self

    def ablehnen(self) -> "AusnahmeAntrag":
        self.status = AusnahmeStatus.ABGELEHNT
        return self

class AusnahmeGenehmigungsregel(BaseModel):
    """Regelt ab welchem Schwellenwert eine Ausnahme 4-Augen-Genehmigung braucht."""
    kategorie: AusnahmeKategorie
    schwellenwert_eur: float          # ab diesem Betrag Genehmigung erforderlich
    erforderliche_rolle: str          # z.B. "head_of_trading"
    schema_version: int = 1

    def ist_genehmigung_noetig(self, betrag_eur: float) -> bool:
        return betrag_eur > self.schwellenwert_eur

# Default-Regeln fuer den Agrarhandel
DEFAULT_AUSNAHME_REGELN: list[AusnahmeGenehmigungsregel] = [
    AusnahmeGenehmigungsregel(
        kategorie=AusnahmeKategorie.PREIS_AUSNAHME,
        schwellenwert_eur=5000.0,
        erforderliche_rolle="head_of_trading",
    ),
    AusnahmeGenehmigungsregel(
        kategorie=AusnahmeKategorie.MENGEN_AUSNAHME,
        schwellenwert_eur=10000.0,
        erforderliche_rolle="head_of_trading",
    ),
    AusnahmeGenehmigungsregel(
        kategorie=AusnahmeKategorie.SICHERHEITS_AUSNAHME,
        schwellenwert_eur=0.0,          # immer Genehmigung noetig
        erforderliche_rolle="compliance_officer",
    ),
]

def pruefe_ausnahme_notwendig(
    kategorie: AusnahmeKategorie,
    betrag_eur: float,
    workflow_instance_id: str,
    beantragende_rolle: str,
    begruendung: str = "",
    regeln: list[AusnahmeGenehmigungsregel] = DEFAULT_AUSNAHME_REGELN,
) -> Optional[AusnahmeAntrag]:
    """Prueft ob fuer den Command ein AusnahmeAntrag noetig ist. None = keine Ausnahme."""
    for regel in regeln:
        if regel.kategorie == kategorie and regel.ist_genehmigung_noetig(betrag_eur):
            return AusnahmeAntrag(
                antrag_id=str(uuid.uuid4()),
                workflow_instance_id=workflow_instance_id,
                kategorie=kategorie,
                begruendung=begruendung,
                beantragende_rolle=beantragende_rolle,
                schwellenwert_ueberschritten=True,
                betrag_eur=betrag_eur,
            )
    return None
