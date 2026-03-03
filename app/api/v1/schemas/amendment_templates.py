"""
Pydantic-Schemas für Vertragsnachträge (EHB/EB-Nachtrag).
Strukturierte Daten für Abschnitte B.1–B.8 und C, gespeichert in ContractAmendment.changes.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


# --- B.1 Liefermodell / Lieferweg ---
class SectionB1(BaseModel):
    lieferart: Optional[str] = None
    abholpunkt: Optional[str] = None
    lagerhaus_standort: Optional[str] = None
    empfaenger_ort: Optional[str] = None
    uebergabe_annahmestelle: Optional[str] = None
    avisierung_stunden: Optional[str] = None
    lieferfenster_von: Optional[str] = None
    lieferfenster_bis: Optional[str] = None
    teillieferungen: Optional[str] = None
    mindestpartie_t: Optional[str] = None


# --- B.2 Transport / Fracht / Wartezeit ---
class SectionB2(BaseModel):
    disposition_durch: Optional[str] = None
    spediteur: Optional[str] = None
    frachtregel: Optional[str] = None
    fracht_pauschal: Optional[str] = None
    wartezeit_frei_h: Optional[str] = None
    standgeld_eur_h: Optional[str] = None


# --- B.3 Verwiegung / Probenahme / Analyse ---
class SectionB3(BaseModel):
    massgebliche_verwiegung: Optional[str] = None
    verwiegung_ort: Optional[str] = None
    probenahme: Optional[str] = None
    analyse_labor: Optional[str] = None
    analyse_extern: Optional[str] = None
    charge_lagerschein: Optional[str] = None


# --- B.4 Qualität / Basis / Abzüge ---
class SectionB4(BaseModel):
    feuchte_basis: Optional[str] = None
    feuchte_max: Optional[str] = None
    protein_basis: Optional[str] = None
    hl_gewicht_basis: Optional[str] = None
    besatz_basis: Optional[str] = None
    besatz_max: Optional[str] = None
    sonstiges_qualitaet: Optional[str] = None
    abrechnung_abweichung: Optional[str] = None
    zurueckweisung_nur_bei: Optional[str] = None


# --- B.5 Menge / Umwidmung ---
class SectionB5(BaseModel):
    mengenaenderung: Optional[str] = None
    ersetzt_menge_t: Optional[str] = None
    umwidmung_datum: Optional[str] = None
    umwidmung_partie: Optional[str] = None
    eigentumsuebergang: Optional[str] = None
    lagergeld_traegt: Optional[str] = None
    lagergeld_satz: Optional[str] = None


# --- B.6 Preis / Preisfixierung / Prämien ---
class SectionB6(BaseModel):
    fixpreis_neu: Optional[str] = None
    fixpreis_fuer_t: Optional[str] = None
    preisfixierung_bis: Optional[str] = None
    fixierung_via: Optional[str] = None
    praemie_abschlag: Optional[str] = None
    vergleich_buyout: Optional[str] = None


# --- B.7 Abrechnung / Zahlung ---
class SectionB7(BaseModel):
    abrechnung_werktage: Optional[str] = None
    abrechnung_nach: Optional[str] = None
    zahlung_tage: Optional[str] = None
    zahlung_ab: Optional[str] = None
    skonto: Optional[str] = None
    gutschrift_selbstfakturierung: Optional[str] = None


# --- B.8 Dokumente ---
class SectionB8(BaseModel):
    dokumente: Optional[list[str]] = None
    dokumente_sonstiges: Optional[str] = None


# --- C. Schluss ---
class SectionC(BaseModel):
    ort_datum: Optional[str] = None
    eintritt_ab: Optional[str] = None
    verkaeufer_name_funktion: Optional[str] = None
    kaeufer_name_funktion: Optional[str] = None


class EHBEBNachtragChanges(BaseModel):
    """Struktur für ContractAmendment.changes bei type=EHBEB_NACHTRAG."""
    b1: Optional[SectionB1] = Field(None, description="Liefermodell / Lieferweg")
    b2: Optional[SectionB2] = Field(None, description="Transport / Fracht / Wartezeit")
    b3: Optional[SectionB3] = Field(None, description="Verwiegung / Probenahme / Analyse")
    b4: Optional[SectionB4] = Field(None, description="Qualität / Basis / Abzüge")
    b5: Optional[SectionB5] = Field(None, description="Menge / Umwidmung")
    b6: Optional[SectionB6] = Field(None, description="Preis / Preisfixierung / Prämien")
    b7: Optional[SectionB7] = Field(None, description="Abrechnung / Zahlung")
    b8: Optional[SectionB8] = Field(None, description="Dokumente")
    c: Optional[SectionC] = Field(None, description="Schluss")

    class Config:
        extra = "allow"


def validate_ehbeb_changes(data: dict[str, Any]) -> dict[str, Any]:
    """Validiert und bereinigt changes für EHBEB_NACHTRAG."""
    try:
        model = EHBEBNachtragChanges.model_validate(data)
        return model.model_dump(exclude_none=True)
    except Exception:
        return data
