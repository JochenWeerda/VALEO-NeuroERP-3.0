"""Lohnabrechnung-Kalkulations-Engine (§ 38 EStG, SGB IV 2025).

Berechnet Brutto-Netto für Steuerklassen I–VI mit korrekten
SV-Beitragsätzen 2025 und LSt-Tabellenwerten (Näherungsformel).

Keine externen Abhängigkeiten — reine Python-Mathematik.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


# ── SV-Beitragssätze 2025 (Arbeitnehmeranteil) ───────────────────────────────
_SV_2025 = {
    "kv":   Decimal("0.0730"),   # 7,30 % gesetzliche KV AN-Anteil (+ Zusatzbeitrag ø 1,7 % → 8,65 % gesamt)
    "kv_zusatz": Decimal("0.0085"),  # halber Zusatzbeitrag ø 1,7 %
    "rv":   Decimal("0.093"),    # 9,3 % RV
    "alv":  Decimal("0.013"),    # 1,3 % ALV
    "pv":   Decimal("0.01525"),  # 1,525 % PflV (ohne Kinder; +0,6 % Kinderloser ≥23)
    "pv_kinderlos_zuschlag": Decimal("0.006"),
}

# ── Beitragsbemessungsgrenzen 2025 (monatlich, West) ─────────────────────────
_BBG_KV = Decimal("5512.50")   # KV/PV
_BBG_RV = Decimal("8050.00")   # RV/ALV (West)

# ── Grundfreibetrag 2025 (§ 32a EStG) ────────────────────────────────────────
_GRUNDFREIBETRAG_MONAT = Decimal("12096") / 12  # 1.008,00 €/Monat

# ── Steuerklassen-Parameter (vereinfacht LSt-Tabelle 2025) ───────────────────
# Steuerklasse → (Freibetrag-Faktor, Entlastungsbetrag-Jahres)
_SK_CONFIG = {
    1: {"freibetrag_extra": Decimal("0"),       "faktor": Decimal("1.0")},
    2: {"freibetrag_extra": Decimal("162"),      "faktor": Decimal("1.0")},  # Alleinerz. 1.908/12
    3: {"freibetrag_extra": Decimal("1008"),     "faktor": Decimal("2.0")},  # doppelter Grundfreibetrag
    4: {"freibetrag_extra": Decimal("0"),        "faktor": Decimal("1.0")},
    5: {"freibetrag_extra": Decimal("-1008"),    "faktor": Decimal("0.0")},  # kein Grundfreibetrag
    6: {"freibetrag_extra": Decimal("-1008"),    "faktor": Decimal("0.0")},  # kein Grundfreibetrag, kein Arbeitnehmerpauschbetrag
}

_ARBEITNEHMER_PAUSCHBETRAG_MONAT = Decimal("1230") / 12  # § 9a Nr. 1 EStG


def _lohnsteuer_monat(zvE_monat: Decimal) -> Decimal:
    """
    Grundtarif § 32a EStG auf monatliches zvE hochgerechnet (Jahresbetrag → /12).
    Näherungsformel — für exakte Werte Finanzverwaltungs-LSt-Tabelle verwenden.
    """
    if zvE_monat <= Decimal("0"):
        return Decimal("0")

    zvE_jahr = zvE_monat * 12

    if zvE_jahr <= Decimal("11604"):       # unterhalb Grundfreibetrag (Altjahr 2024; 2025: 12096)
        lst_jahr = Decimal("0")
    elif zvE_jahr <= Decimal("17005"):
        y = (zvE_jahr - Decimal("11604")) / Decimal("10000")
        lst_jahr = (Decimal("979.18") * y + Decimal("1400")) * y
    elif zvE_jahr <= Decimal("66760"):
        z = (zvE_jahr - Decimal("17005")) / Decimal("10000")
        lst_jahr = (Decimal("192.59") * z + Decimal("2397")) * z + Decimal("966.53")
    elif zvE_jahr <= Decimal("277825"):
        lst_jahr = Decimal("0.42") * zvE_jahr - Decimal("9972.98")
    else:
        lst_jahr = Decimal("0.45") * zvE_jahr - Decimal("18307.73")

    return (lst_jahr / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _solidaritaetszuschlag(lst: Decimal) -> Decimal:
    """5,5 % SolZ auf LSt, Freigrenze § 3 SolZG 1995 beachten."""
    if lst <= Decimal("18.33"):
        return Decimal("0")
    zuschlag = lst * Decimal("0.055")
    gleitzone_grenze = lst * Decimal("0.119")
    return min(zuschlag, gleitzone_grenze).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class LohnAbrechnungErgebnis:
    brutto: Decimal
    steuerklasse: int
    kinder_freibetraege: Decimal

    # SV
    kv_beitrag: Decimal
    rv_beitrag: Decimal
    alv_beitrag: Decimal
    pv_beitrag: Decimal
    sv_gesamt: Decimal

    # Steuern
    zvE_monat: Decimal
    lohnsteuer: Decimal
    solidaritaetszuschlag: Decimal
    kirchensteuer: Decimal

    # Netto
    netto: Decimal

    def as_dict(self) -> dict:
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in self.__dict__.items()}


def berechne_netto(
    brutto: float,
    steuerklasse: int,
    *,
    hat_kinder: bool = False,
    kinder_freibetraege: float = 0.0,
    kirchensteuersatz: float = 0.09,  # Bayern/BaWü: 0,08
    zusatzbeitrag_kv: float = 0.017,  # individueller Kassenzsatz ø 2025
) -> LohnAbrechnungErgebnis:
    """
    Brutto-Netto-Kalkulation für einen Monat.

    Args:
        brutto: Monatliches Bruttogehalt in EUR
        steuerklasse: 1–6
        hat_kinder: Kinderlosenzuschlag PV entfällt
        kinder_freibetraege: Anzahl Kinderfreibeträge (0,5-Schritte)
        kirchensteuersatz: 8 % oder 9 % je nach Bundesland
        zusatzbeitrag_kv: Kassenindividueller Zusatzbeitrag (ø 2025: 1,7 %)
    """
    if steuerklasse not in range(1, 7):
        raise ValueError(f"Ungültige Steuerklasse: {steuerklasse}")

    B = Decimal(str(brutto))
    cfg = _SK_CONFIG[steuerklasse]

    # ── SV-Beiträge ───────────────────────────────────────────────────────────
    kv_basis = min(B, _BBG_KV)
    kv_satz = _SV_2025["kv"] + Decimal(str(zusatzbeitrag_kv)) / 2  # halber Zusatzbeitrag
    kv = (kv_basis * kv_satz).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    rv_basis = min(B, _BBG_RV)
    rv = (rv_basis * _SV_2025["rv"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    alv = (rv_basis * _SV_2025["alv"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    pv_satz = _SV_2025["pv"]
    if not hat_kinder:
        pv_satz += _SV_2025["pv_kinderlos_zuschlag"]
    pv = (kv_basis * pv_satz).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    sv = kv + rv + alv + pv

    # ── zvE (zu versteuerndes Einkommen, monatlich) ───────────────────────────
    grundfreibetrag = _GRUNDFREIBETRAG_MONAT * cfg["faktor"] + cfg["freibetrag_extra"]
    kf_abzug = Decimal(str(kinder_freibetraege)) * Decimal("306.17")  # halber Kinder-FB monatlich
    arbeitnehmer_pausch = _ARBEITNEHMER_PAUSCHBETRAG_MONAT

    zvE = B - sv - grundfreibetrag - arbeitnehmer_pausch - kf_abzug
    zvE = max(Decimal("0"), zvE)

    # ── Lohnsteuer & Soli ─────────────────────────────────────────────────────
    lst = _lohnsteuer_monat(zvE)
    soli = _solidaritaetszuschlag(lst)
    kist = (lst * Decimal(str(kirchensteuersatz))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if kirchensteuersatz > 0 else Decimal("0")

    netto = B - sv - lst - soli - kist

    return LohnAbrechnungErgebnis(
        brutto=B,
        steuerklasse=steuerklasse,
        kinder_freibetraege=Decimal(str(kinder_freibetraege)),
        kv_beitrag=kv,
        rv_beitrag=rv,
        alv_beitrag=alv,
        pv_beitrag=pv,
        sv_gesamt=sv,
        zvE_monat=zvE,
        lohnsteuer=lst,
        solidaritaetszuschlag=soli,
        kirchensteuer=kist,
        netto=netto,
    )
