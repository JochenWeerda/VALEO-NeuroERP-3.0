"""GfE 2023 Bedarfsberechnung (ME + sidP, DLG 01|2023 Tabellen 8/11/12).

Code-SSOT der Bedarfsformeln — extrahiert 1:1 aus dem Optimierungs-Endpoint
(FEED-OPT-042); Drift-Freiheit ist golden-getestet
(tests/test_feeding_requirements_module.py). Der Endpoint-Monolith und
`feeding_requirements_service` importieren dieses Modul.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel


def normalize_feeding_type(raw: Optional[str]) -> str:
    """
    Normalisiert den Fuetterungsmodus:
      TMR          - klassische Totalmischration
      PMR          - partielle Mischration (Grund+Kraftfutter mit separatem Kraftfutter)
      PMR+Weide    - PMR mit nennenswerter Weideaufnahme (Fruehjahr/Sommer)
    """
    value = str(raw or "TMR").strip().upper().replace(" ", "").replace("_", "+")
    if value in {"PMRWEIDE", "PMR+WEIDE", "PASTURE", "WEIDE"}:
        return "PMR+Weide"
    if value == "PMR":
        return "PMR"
    return "TMR"


class CowRequirements(BaseModel):
    """Nährstoffbedarf Milchkuh nach GfE 2023 (ME-Basis, sidP-Protein)."""

    me_mj: float  # Umsetzbare Energie ME_FAN1 [MJ/d]
    sidp_g: float  # dünndarmverdauliches Protein sidP [g/d]  (GfE 2023)
    nel_mj: float  # NEL [MJ/d] – Referenz für Ausgabe
    nxp_g: float  # nXP [g/d]  – Referenz (≈ sidP, GfE 2001)
    dmi_min_kg: float  # Mindest-TM-Aufnahme [kg/d]
    dmi_max_kg: float  # Maximal-TM-Aufnahme [kg/d]
    ndf_min_g: float  # Mindest-aNDFom gesamt [g/d]
    ca_min_g: float  # Mindest-Calcium [g/d]
    p_min_g: float  # Mindest-Phosphor [g/d]
    na_min_g: float  # Mindest-Natrium [g/d]
    mg_min_g: float  # Mindest-Magnesium [g/d]
    k_max_g: float  # Maximum Kalium [g/d] – K/Mg-Antagonismus (GfE-Workshop 2023)
    dmi_target_kg: float  # Ziel-TM-Aufnahme (Mittelpunkt) für peNDF-Lookup


def gfe_requirements(profile: Dict[str, Any], fani: Optional[float] = None) -> CowRequirements:
    """
    GfE 2023 ME + sidP Bedarfsberechnung für Milchkühe.

    Energie (ME-Basis, dreistufiges Verfahren nach GfE 2023):
      ME_Erhaltung = (NEL_maint / k_m) = (0.308 × BW^0.75) / 0.73 = 0.422 × BW^0.75  [MJ/d]
      ME_Milch     = (NEL_milk  / k_l) = (0.38×XL%+ 0.21×XP%+ 0.95) / 0.62 × Milch  [MJ/d]
      Faktor 0.308 = 0.293 × 1.05 (inkl. ~5% Aktivitätszuschlag nach GfE 2001)

    Protein (sidP – dünndarmverdauliches Protein):
      sidP = nXP (GfE 2001 approximation, wird durch GfE 2023 Tab.A3 verfeinert)
      nXP_Erhaltung ≈ 3.47 × BW^0.75 [g/d]  (aus DLG Tab.8 abgeleitet)
      nXP_Milch     ≈ 85 g/kg Milch   [g/d]

    Mineralien (GfE 2001 vereinfacht):
      Ca = 0.031×BW^0.75 + 1.22×Milch;  P = 0.014×BW^0.75 + 0.90×Milch
      Na ≈ 1.5 g/kg TM × DMI;  Mg ≈ 1.5 g/kg TM × DMI

    DMI-Schätzung (Gruber 2004, Deutsche Holstein 675 kg):
      DMI = 0.025×BW + 0.15×Milch  (gilt ab ~60. Laktationstag)
      Optional: ``target_dmi_kg`` überschreibt den Planungsmittelpunkt;
      ``wizard_dmi_min_kg`` / ``wizard_dmi_max_kg`` setzen das TM-Band für den LP.
    """
    bw = float(profile.get("body_weight_kg") or 650)
    milk = float(profile.get("milk_kg_day") or 0)
    fat_pct = float(profile.get("milk_fat_pct") or 4.0)
    prot_pct = float(profile.get("milk_protein_pct") or 3.4)

    bw75 = bw**0.75

    # --- Weide-Aktivitaetszuschlag (DLG-Merkblatt 417 / GfE 2001) ---
    # Weidegang erhoeht den Erhaltungsbedarf durch Lauf-, Rupf- und
    # Thermoregulations-Aktivitaet um 10-25 %. Default: +15 % bei echtem
    # Weidegang (feeding_type == "PMR+Weide"). Das ist **zusaetzlich** zu
    # den bereits in 0.308 enthaltenen 5 % Grundaktivitaetszuschlag.
    feeding_type = normalize_feeding_type(profile.get("feeding_type"))
    pasture_factor = 1.15 if feeding_type == "PMR+Weide" else 1.00

    # --- NEL (für Referenzausgabe) ---
    nel_maint = 0.308 * bw75 * pasture_factor
    nel_milk = (0.38 * fat_pct + 0.21 * prot_pct + 0.95) * milk if milk > 0 else 0.0
    nel_total = nel_maint + nel_milk

    # --- ME (GfE 2023 dreistufig) ---
    me_maint = nel_maint / 0.73  # k_m = 0.73 für laktierende Kühe
    # k_l dichte-abhaengig (GfE 2001, §5): k_l = 0.463 + 0.24·q mit q = ME/GE.
    # Basis: k_l = 0.60 (konservativ, da ME-Dichte beim Planungsaufruf unbekannt).
    # Optional: FANi-Korrektur fuer den FAN-Iterationsloop:
    #   k_l += 0.01 * (FANi - 3.0), begrenzt auf [0.58, 0.64].
    # Bei hoeherem FANi (= mehr Futteraufnahme) steigt die ME-Dichte und damit k_l,
    # was den ME-Bedarf senkt – konsistent mit GfE 2023 Passageraten-Beziehung.
    k_l_planning = 0.60
    if fani is not None and fani > 0:
        k_l_planning = max(0.58, min(0.64, 0.60 + 0.01 * (float(fani) - 3.0)))
    me_milk = nel_milk / k_l_planning if milk > 0 else 0.0
    me_total = me_maint + me_milk

    # --- sidP ≈ nXP (GfE 2001, aus DLG Tab.8 validiert) ---
    # nXP_Milch: DLG Tab.8 (700 kg KM, Laktationstag 100) back-berechnet:
    #   35 kg Milch → 2341 g/d nXP, Erhaltung 468 g/d → 52,8 g/kg Milch für Leistungsanteil
    #   DLG empfiehlt 50-55 g/kg Milch je nach Milchinhaltsstoffen (GfE 2001 Annex).
    nxp_maint = 3.47 * bw75
    nxp_milk = 52.0 * milk  # g/kg Milch (aus DLG Tab.8; früher fälschlich 85 g/kg)
    nxp_total = nxp_maint + nxp_milk

    # sidP-Bedarf: GfE 2023 Tabelle A3 empfiehlt sidP etwas unter nXP (ca. 95%)
    sidp_total = nxp_total * 0.95

    # Physiologische Obergrenze nach DLG Information 01|25 Tabelle 14:
    _DMI_ABS_MAX_KG = 28.5  # DLG Tab. 14 – hartes physiologisches Limit

    # --- DMI (Gruber 2004 vereinfacht), optional durch Wizard-Ziel TM ueberschreibbar ---
    dmi_plan = 0.025 * bw + 0.15 * milk if milk > 0 else 0.025 * bw
    dmi_plan = max(dmi_plan, 8.0)
    td_raw = profile.get("target_dmi_kg")
    if td_raw is not None:
        try:
            td_f = float(td_raw)
            if td_f > 0:
                dmi_plan = max(8.0, min(td_f, _DMI_ABS_MAX_KG))
        except (TypeError, ValueError):
            pass

    dmi_min_kg = dmi_plan * 0.90
    dmi_max_kg = min(dmi_plan * 1.10, _DMI_ABS_MAX_KG)

    wm_raw = profile.get("wizard_dmi_min_kg")
    wx_raw = profile.get("wizard_dmi_max_kg")
    if wm_raw is not None:
        try:
            dmi_min_kg = float(wm_raw)
        except (TypeError, ValueError):
            pass
    if wx_raw is not None:
        try:
            dmi_max_kg = float(wx_raw)
        except (TypeError, ValueError):
            pass

    dmi_min_kg = max(5.0, min(dmi_min_kg, _DMI_ABS_MAX_KG))
    dmi_max_kg = max(dmi_min_kg, min(dmi_max_kg, _DMI_ABS_MAX_KG))
    dmi_target_kg = (dmi_min_kg + dmi_max_kg) / 2.0

    # --- aNDFom-Minimum: 300 g/kg TM × effektive TM-Aufnahme (Bandmittelpunkt) ---
    ndf_min = 300.0 * dmi_target_kg

    # --- Mengenelemente (GfE 2023 / GfE-Workshop 2023) ---
    ca_min = 0.031 * bw75 + 1.22 * milk
    p_min = 0.014 * bw75 + 0.90 * milk
    # GfE-Workshop 2023: Mg-Bedarf um 25–40% erhöht gegenüber GfE 2001
    # Erhaltung: 0.048 g/kg LM (hochrechnend aus DLG Tab.12 inkl. +30% Zuschlag)
    # Leistung: 0.10 g/kg Milch (GfE 2023 Workshop Präsentation)
    mg_min = (0.048 * bw + 0.10 * milk) if milk > 0 else 0.048 * bw
    na_min = 1.5 * dmi_target_kg  # ~1.5 g/kg TM
    # K/Mg-Antagonismus (GfE-Workshop 2023): max. K-Versorgung 28 g/kg TM
    k_max = 28.0 * dmi_target_kg

    return CowRequirements(
        me_mj=me_total,
        sidp_g=sidp_total,
        nel_mj=nel_total,
        nxp_g=nxp_total,
        dmi_min_kg=dmi_min_kg,
        dmi_max_kg=dmi_max_kg,
        dmi_target_kg=dmi_target_kg,
        ndf_min_g=ndf_min,
        ca_min_g=ca_min,
        p_min_g=p_min,
        na_min_g=na_min,
        mg_min_g=mg_min,
        k_max_g=k_max,
    )
