"""
GfE (2023) – öffentlich referenzierte Näherungsformeln für Milchkühe

Quellen (Stand Recherche 2026):
- GfE: „Empfehlungen zur Energie- und Nährstoffversorgung von Milchkühe“ (Sept. 2023),
  DLG-Verlag / Ausschuss für Bedarfsnormen der GfE (AfBN).
- Proteinmarkt.de / LKV (2024): Umstellung NEL → ME; Erhaltung 0,64 MJ ME/kg LM^0,75;
  Milchbildung: Energiegehalt ECM 3,15 MJ/kg, Teilwirkungsgrad ME → Milch 0,66
  → ME_Milch ≈ ECM × (3,15 / 0,66) MJ pro Tag.
- LKV Sachsen Blog: ME-Futtermittelbewertung, FAN-Bezug (50 g TM/kg LM^0,75 = FAN 1).

Hinweis: Vollständige Tabellen (sidAA, FAN-Korrekturen, Mineralien exakt) stehen nur
in der GfE-Publikation. Dieses Modul implementiert die in Fachartikeln konsistent
wiedergegebenen ME- und ECM-Kernelemente sowie pragmatische Näherungen für sidP,
Faseranteil und Minerale. Für Zertifizierung/Legalität die Originalpublikation nutzen.

**NEL und ME sind verschiedene energetische Bewertungsgrößen und dürfen nicht
gleichgesetzt oder ohne anerkannte Umrechnung substituiert werden.**
"""

from __future__ import annotations

from typing import Tuple

# --- Energie (GfE 2023, laktierende Milchkuh) ---

ME_MAINTENANCE_MJ_PER_KG_METABOLIC_BW = 0.64

ECM_ENERGY_CONTENT_MJ_PER_KG = 3.15
ME_TO_MILK_EFFICIENCY = 0.66
ME_PER_KG_ECM = ECM_ENERGY_CONTENT_MJ_PER_KG / ME_TO_MILK_EFFICIENCY  # ≈ 4,77 MJ/kg ECM

FAN1_G_TM_PER_KG075 = 50.0

SIDP_MAINTENANCE_G_PER_KG075 = 2.85
SIDP_PER_KG_MILK_PROTEIN = 68.0

NDF_MIN_FRACTION_OF_DMI = 0.30
NDF_MAX_FRACTION_OF_DMI = 0.48
STARCH_MAX_FRACTION_OF_DMI = 0.15
SUGAR_MAX_FRACTION_OF_DMI = 0.05
FAT_MAX_FRACTION_OF_DMI = 0.08

FORAGE_SHARE_MIN_LACTATING = 0.40
FORAGE_SHARE_MIN_DRY = 0.60


def metabolic_body_weight_kg(live_weight_kg: float) -> float:
    """Metabolische Körpermasse LM^0,75 (kg^0,75)."""
    if live_weight_kg <= 0:
        raise ValueError("Lebendmasse muss positiv sein")
    return live_weight_kg ** 0.75


def energy_maintenance_me_mj(live_weight_kg: float) -> float:
    """
    Erhaltungsbedarf an umsetzbarer Energie (ME) für laktierende Milchkuh nach GfE (2023).

    ME_Erhalt = 0,64 × LM^0,75  [MJ/Tag]
    """
    return ME_MAINTENANCE_MJ_PER_KG_METABOLIC_BW * metabolic_body_weight_kg(live_weight_kg)


# ECM-Referenz-Laktosegehalt [%] (DLG 01|2025: ECM mit 4,8 % Laktose).
ECM_REFERENCE_LACTOSE_PCT = 4.8


def energy_corrected_milk_kg(
    milk_kg_day: float,
    fat_percent: float,
    protein_percent: float,
    lactose_percent: float = ECM_REFERENCE_LACTOSE_PCT,
) -> float:
    """
    Energiekorrigierte Milch ECM [kg/Tag] nach DLG Information 01|2025 (Kap. 10).

    ECM [kg] = kg Milch × (38,5 × Fett% + 24,2 × Protein% + 16,5 × Laktose%) ÷ 3,15 ÷ 100

    mit Fett%, Protein% und Laktose% als Prozentangaben (z. B. 4,0 / 3,4 / 4,8) und
    dem Milch-Energiegehalt 3,15 MJ/kg. Bei Referenzzusammensetzung (4,0/3,4/4,8) ergibt
    sich ECM ≈ Milch. Laktose default 4,8 % (DLG-ECM-Referenz), falls nicht analysiert.
    """
    if milk_kg_day < 0:
        raise ValueError("Milchmenge darf nicht negativ sein")
    f = max(fat_percent, 0.0)
    p = max(protein_percent, 0.0)
    la = max(lactose_percent, 0.0)
    factor = (38.5 * f + 24.2 * p + 16.5 * la) / 3.15 / 100.0
    return milk_kg_day * factor


def energy_lactation_me_mj(ecm_kg_day: float) -> float:
    """
    ME-Bedarf für Milchbildung nach GfE (2023), aus ECM abgeleitet.

    ME_Milch = ECM × (3,15 / 0,66)  [MJ/Tag]
    """
    if ecm_kg_day < 0:
        raise ValueError("ECM darf nicht negativ sein")
    return ME_PER_KG_ECM * ecm_kg_day


def total_me_requirement_mj(
    live_weight_kg: float,
    milk_kg_day: float,
    fat_percent: float,
    protein_percent: float,
    lactose_percent: float = ECM_REFERENCE_LACTOSE_PCT,
) -> Tuple[float, float, float]:
    """
    Gesamt-ME-Bedarf [MJ/Tag] = Erhaltung + Milch (über ECM nach DLG 01|2025).

    Returns:
        (me_total, me_maintenance, me_lactation)
    """
    me_m = energy_maintenance_me_mj(live_weight_kg)
    ecm = energy_corrected_milk_kg(milk_kg_day, fat_percent, protein_percent, lactose_percent)
    me_l = energy_lactation_me_mj(ecm)
    return me_m + me_l, me_m, me_l


def fan1_reference_dmi_kg(live_weight_kg: float) -> float:
    """Theoretisches TM-Aufnahmeniveau FAN 1 [kg TM/Tag] = 0,050 × LM^0,75 (Referenz GfE 2023)."""
    return (FAN1_G_TM_PER_KG075 / 1000.0) * metabolic_body_weight_kg(live_weight_kg)


def lactation_stage_dmi_factor(days_in_lactation: int) -> float:
    """Skalierung der geschätzten Aufnahme nach Laktationstag (heuristisch)."""
    if days_in_lactation <= 0:
        return 0.85
    if days_in_lactation <= 100:
        return 0.82 + (days_in_lactation / 100.0) * 0.18
    if days_in_lactation <= 200:
        return 1.0
    if days_in_lactation <= 305:
        return 1.0 - ((days_in_lactation - 200) / 105.0) * 0.08
    return 0.88


def estimate_dmi_lactating_kg(
    live_weight_kg: float,
    milk_kg_day: float,
    days_in_lactation: int,
) -> float:
    """
    Geschätzte Trockenmasseaufnahme laktierende Kuh [kg/Tag].

    Heuristik (ohne FAN-Tabellen): TM ≈ (0,018 × LM + 0,40 × Milch) × Laktationsfaktor.
    Koeffizienten so gewählt, dass die sich aus GfE-2023-ME (Erhaltung + ECM-Milch) ergebende
    mittlere Energiekonzentration mit typischem Raufutter/Kraftfutter-Mix (ca. 9,5–11 MJ/kg TM)
    im LP üblicherweise erreichbar ist. Liegt ``target_dmi_kg`` im Kuhprofil vor, wird diese
    Schätzung im RequirementService nicht verwendet.

    Vollständige GfE-Aufnahmemodelle → FAN und Rationszusammensetzung (Handbuch).
    """
    base = 0.018 * live_weight_kg + 0.40 * max(milk_kg_day, 0.0)
    return base * lactation_stage_dmi_factor(days_in_lactation)


def sidp_requirement_g(
    live_weight_kg: float,
    milk_kg_day: float,
    milk_protein_percent: float,
) -> Tuple[float, float, float]:
    """
    Geschätzter sidP-Bedarf [g/Tag] = Erhaltung + Milch (Näherung, kein Ersatz für sidAA-Tabellen).

    Returns:
        (sidp_total, sidp_maint, sidp_milk)
    """
    bw75 = metabolic_body_weight_kg(live_weight_kg)
    maint = SIDP_MAINTENANCE_G_PER_KG075 * bw75
    milk_prot_kg = milk_kg_day * (milk_protein_percent / 100.0)
    lact = SIDP_PER_KG_MILK_PROTEIN * milk_prot_kg
    return maint + lact, maint, lact


def fiber_and_concentrate_bounds_g(dmi_kg: float) -> dict:
    """aNDFom- und Stärke/Zucker/Fett-Grenzen aus DMI und typischen DM-Anteilen [g/Tag]."""
    return {
        "andfom_min_g": dmi_kg * NDF_MIN_FRACTION_OF_DMI * 1000.0,
        "andfom_max_g": dmi_kg * NDF_MAX_FRACTION_OF_DMI * 1000.0,
        "starch_max_g": dmi_kg * STARCH_MAX_FRACTION_OF_DMI * 1000.0,
        "sugar_max_g": dmi_kg * SUGAR_MAX_FRACTION_OF_DMI * 1000.0,
        "fat_max_g": dmi_kg * FAT_MAX_FRACTION_OF_DMI * 1000.0,
    }


def fiber_bounds_dry_cow_g(dmi_kg: float) -> dict:
    """aNDFom und Konzentrat-Obergrenzen Trockensteher (konservativer als laktierend)."""
    return {
        "andfom_min_g": dmi_kg * NDF_MIN_FRACTION_OF_DMI * 1000.0,
        "andfom_max_g": dmi_kg * min(NDF_MAX_FRACTION_OF_DMI, 0.42) * 1000.0,
        "starch_max_g": dmi_kg * 0.10 * 1000.0,
        "sugar_max_g": dmi_kg * 0.03 * 1000.0,
        "fat_max_g": dmi_kg * 0.04 * 1000.0,
    }


def minerals_ca_p_na_g(live_weight_kg: float, milk_kg_day: float) -> Tuple[float, float, float]:
    """
    Ca-, P-, Na-Bedarf [g/Tag] – pragmatische Näherung (Erhaltung + Milchleistung).

    Exakte Werte GfE 2023 → Handbuch „Empfehlungen zur Energie- und Nährstoffversorgung von Milchkühe“.
    """
    ca = 0.05 * live_weight_kg + 2.4 * milk_kg_day
    p = 0.032 * live_weight_kg + 1.65 * milk_kg_day
    na = 0.005 * live_weight_kg + 0.15 * milk_kg_day
    return ca, p, na
