"""
Nährwert-Berechnungsservice nach DLG-Merkblatt 503 (10/2025) und DLG-Merkblatt 504 (10/2025).

Energie-Bewertung Wiederkäuer (DLG 503 / GfE 2023):
    OMD_FAN1 → ED → DE_FAN1 → UE → CH4E_FAN1 → ME_FAN1 → ME_FANi

Protein-Bewertung Milchkuh (DLG 504 / GfE 2023):
    CP → RDP/UDP → siDUDP → sidP (inkl. MCP-Anteil)

Jedes Ergebnis trägt ein Formel-Versionsfeld für vollständige Rückverfolgbarkeit
(Deklarations- vs. Beratungsmodus).

Referenzen:
    - DLG-Merkblatt 503, Oktober 2025: Leitfaden Energiekonzentration Wiederkäuer/Schwein
    - DLG-Merkblatt 504, Oktober 2025: Leitfaden Proteinversorgung Milchkuh nach GfE 2023
    - DLG-Futterwerttabellen Wiederkäuer 2025
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


FORMELWERK_ENERGIE = "DLG503_2025-10"
FORMELWERK_PROTEIN = "DLG504_2025-10"


class FutterTyp(str, Enum):
    GROBFUTTER = "grobfutter"          # Grassilage, Heu, Stroh
    KONZENTRAT = "konzentrat"           # Kraftfutter, Körner
    SAFTFUTTER = "saftfutter"           # Rüben, Trester
    MISCHFUTTER = "mischfutter"         # Mischfuttermittel


class QuelleTyp(str, Enum):
    LABOR = "labor"                     # Laborwert (mit Report-ID)
    TABELLE = "tabelle"                 # DLG-Tabellenwert
    USER = "user_override"              # Manueller Wert


@dataclass
class AnalytikInput:
    """
    Analytik-Eingangsmatrix für Nährwertberechnung (DLG 503 §3.1).

    Pflichtfelder je nach Bewertungsweg:
        ELOS-Weg: tm, ca, cp, cl, zucker, staerke, elos
        Gasbil.-Weg: tm, ca, cp, cl, zucker, staerke, gasbildung_200h
        Faser-Weg:  tm, ca, cp, cl, zucker, staerke, adfom
    """
    # Trockenmassegehalt (g/kg FM)
    tm: float = 880.0                   # Trockenmasse
    # Proximat-Analyse (g/kg TM)
    ca: float = 70.0                    # Rohasche (Crude Ash)
    cp: float = 180.0                   # Rohprotein (Crude Protein)
    cl: float = 30.0                    # Rohfett (Crude Lipid)
    zucker: float = 50.0                # Zucker
    staerke: float = 0.0                # Stärke
    # Faseranalytik (g/kg TM)
    adfom: Optional[float] = None       # ADFom (säureunlösliche NDF) g/kg TM
    andFom: Optional[float] = None      # aNDFom g/kg TM
    # In-vitro-Methoden (optional, für präzisere OMD-Schätzung)
    elos: Optional[float] = None        # ELOS (enzym-lösl. org. Substanz) g/kg TM
    gasbildung_200h: Optional[float] = None  # Gasbildung nach 200h (ml/200 mg TM)
    # Bruttoenergie (MJ/kg TM) — falls aus Bombe bekannt
    ge: Optional[float] = None
    # Protein-Analytik für DLG 504
    rdp_anteil: float = 0.70            # Anteil RDP am CP (Fraktion 0–1), typisch 0.65–0.75
    si_dudp: float = 0.80               # Scheinbare intestinale Verdaulichkeit des UDP (0–1)
    # Quellenherkunft für Audit
    quelle: QuelleTyp = QuelleTyp.LABOR
    quelle_id: Optional[str] = None     # Labor-Report-ID oder Tabellen-Referenz
    futtertyp: FutterTyp = FutterTyp.KONZENTRAT
    # Futteraufnahmeniveau (Vielfaches der Erhaltung; 1 = Erhaltung)
    fan: float = 2.5                    # typisch Milchkuh in Laktation: 2.0–3.0


@dataclass
class EnergieErgebnis:
    """Energie-Ergebnismatrix nach DLG 503 (FAN1 und FANi)."""
    # Berechnungsweg
    omd_methode: str = ""               # "elos" | "gasbildung" | "faser" | "mischfutter"
    # Verdaulichkeit
    omd_fan1: float = 0.0               # OM-Verdaulichkeit bei FAN1 (%)
    omd_fani: float = 0.0               # OM-Verdaulichkeit bei FANi (%)
    ed_fan1: float = 0.0                # Echte Verdaulichkeit bei FAN1 (%)
    # Energiegehalte MJ/kg OM
    ge_mj_kg_om: float = 0.0           # Bruttoenergie
    de_fan1: float = 0.0               # Verdauliche Energie FAN1
    ue: float = 0.0                    # Harnenergie
    ch4e_fan1: float = 0.0             # Methan-Energie FAN1
    ch4e_fani: float = 0.0             # Methan-Energie FANi
    me_fan1_mj_kg_om: float = 0.0      # ME bei FAN1 (MJ/kg OM)
    me_fani_mj_kg_om: float = 0.0      # ME bei FANi (MJ/kg OM)
    # Umgerechnet auf TM-Basis (MJ/kg TM)
    me_fan1_mj_kg_tm: float = 0.0
    me_fani_mj_kg_tm: float = 0.0
    # Audit
    formelwerk: str = FORMELWERK_ENERGIE
    fan_input: float = 1.0
    modus: str = "beratung"             # "deklaration" | "beratung"


@dataclass
class ProteinErgebnis:
    """Protein-Ergebnismatrix nach DLG 504 (sidP-System)."""
    # g/kg TM
    cp: float = 0.0
    rdp: float = 0.0                    # Ruminale abbaubare Protein-Fraktion
    udp: float = 0.0                    # Undegradable Dietary Protein
    sidp_udp: float = 0.0              # sidP aus UDP
    mcp: float = 0.0                    # Mikrobielle CP-Produktion
    sidp_mcp: float = 0.0              # sidP aus MCP
    sidp_gesamt: float = 0.0           # sidP gesamt
    dom: float = 0.0                    # verdauliche organische Substanz g/kg TM
    rmd: float = 0.0                    # Ruminale mikrobielle Differenz
    # Audit
    formelwerk: str = FORMELWERK_PROTEIN
    modus: str = "beratung"


@dataclass
class NaehrwertErgebnis:
    """Kombiniertes Ergebnis Energie + Protein mit Audit-Feldern."""
    energie: EnergieErgebnis = field(default_factory=EnergieErgebnis)
    protein: ProteinErgebnis = field(default_factory=ProteinErgebnis)
    # Roh-Nährstoffe (aus Input, für Report)
    rohprotein_g_kg_tm: float = 0.0
    rohfett_g_kg_tm: float = 0.0
    rohasche_g_kg_tm: float = 0.0
    # Konventionelle Kennzahlen (für Kompatibilität / Deklaration nach VO 767/2009)
    nel_mj_kg_tm: float = 0.0          # NEL für Milchkühe (vereinfacht aus ME)
    nxp_g_kg_tm: float = 0.0          # nXP (für Legacy-Systeme)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _calc_ge(inp: AnalytikInput) -> float:
    """
    Berechnung Bruttoenergie (GE) nach DLG 503 Formel (falls nicht aus Bombe bekannt).
    GE (MJ/kg TM) ≈ 0,0239·CP + 0,0398·CL + 0,0201·Zucker + 0,0175·Stärke
                   + 0,0198·(NDF - ADF) + 0,0215·ADF + 0,0131·CA [alle g/kg TM]
    """
    if inp.ge is not None:
        return inp.ge
    ndf = inp.andFom or 0.0
    adf = inp.adfom or 0.0
    ge = (
        0.0239 * inp.cp
        + 0.0398 * inp.cl
        + 0.0201 * inp.zucker
        + 0.0175 * inp.staerke
        + 0.0198 * max(ndf - adf, 0)
        + 0.0215 * adf
        + 0.0131 * inp.ca
    )
    return max(ge, 17.0)  # Minimalwert ca. 17 MJ/kg TM


def _calc_omd_elos(inp: AnalytikInput) -> tuple[float, str]:
    """
    OMD_FAN1 aus ELOS (DLG 503, Schätzgleichung ELOS-Weg).
    OMD_FAN1 (%) = (ELOS / (1000 - CA)) × 100 × 0.96 + Korrekturfaktor
    Vereinfacht nach DLG 503 §4.1 (ELOS-Methode Hohenheim-Darmstadt).
    """
    if inp.elos is None:
        return 0.0, "elos_nicht_verfügbar"
    om = 1000.0 - inp.ca  # g/kg TM
    if om <= 0:
        return 0.0, "elos"
    omd = (inp.elos / om) * 100.0 * 0.96
    return min(max(omd, 50.0), 95.0), "elos"


def _calc_omd_gasbildung(inp: AnalytikInput) -> tuple[float, str]:
    """
    OMD_FAN1 aus Gasbildung nach 200h (DLG 503, HFT-Methode).
    OMD_FAN1 (%) = 0.534 · GB200 + 0.00426 · CP + 0.00206 · CL - 0.00525 · CA + 30.6
    Formel nach Steingaß/Menke 1988 (aktuell in DLG 503 referenziert).
    """
    if inp.gasbildung_200h is None:
        return 0.0, "gasbildung_nicht_verfügbar"
    omd = (
        0.534 * inp.gasbildung_200h
        + 0.00426 * inp.cp
        + 0.00206 * inp.cl
        - 0.00525 * inp.ca
        + 30.6
    )
    return min(max(omd, 50.0), 95.0), "gasbildung"


def _calc_omd_faser(inp: AnalytikInput) -> tuple[float, str]:
    """
    OMD_FAN1 aus Faserfraktionen (DLG 503, Faser-Weg für Grobfutter/Mischfutter).
    OMD_FAN1 (%) = 88.9 - 0.779 × ADFom/OM × 100  [vereinfacht nach Van Soest]
    """
    if inp.adfom is None:
        return 75.0, "faser_schätzung"
    om = 1000.0 - inp.ca
    if om <= 0:
        return 75.0, "faser"
    adf_om_pct = (inp.adfom / om) * 100.0
    omd = 88.9 - 0.779 * adf_om_pct
    return min(max(omd, 50.0), 95.0), "faser"


def _calc_omd_mischfutter(inp: AnalytikInput) -> tuple[float, str]:
    """
    OMD_FAN1 nach der 'rechtsgültigen Mischfutter-Gleichung' (DLG 503 §5 / amtliche Kontrolle).
    Basiert auf OM-Verdaulichkeit aus Hauptnährstoffen (DE-Mischfutter-Gleichung).
    OMD ≈ (0.87·CP + 0.88·CL·2.25 + 0.79·ZU + 0.80·ST + VEM_NDF) / GE × 100
    Vereinfacht für ERP-Zwecke.
    """
    ndf = inp.andFom or 300.0
    ge = _calc_ge(inp)
    # Verdauliche Energie-Fraktionen (MJ/kg TM) nach Futterwert-Tabellen
    de_cp = 0.87 * inp.cp * 0.02340        # Rohprotein
    de_cl = 0.88 * inp.cl * 0.03890 * 2.25  # Rohfett (Faktor 2.25 für Energiedichte)
    de_zu = 0.79 * inp.zucker * 0.01680    # Zucker
    de_st = 0.80 * inp.staerke * 0.01760   # Stärke
    de_ndf = max(0.55 * ndf * 0.01850, 0)  # NDF (annahme 55 % verd.)
    de_sum = de_cp + de_cl + de_zu + de_st + de_ndf
    omd = (de_sum / max(ge, 1.0)) * 100.0
    return min(max(omd, 55.0), 92.0), "mischfutter"


def _select_omd_method(inp: AnalytikInput) -> tuple[float, str]:
    """Wählt die beste verfügbare OMD-Schätzmethode (Priorität: ELOS > GB > Faser > Mischfutter)."""
    if inp.elos is not None:
        val, meth = _calc_omd_elos(inp)
        if val > 0:
            return val, meth
    if inp.gasbildung_200h is not None:
        val, meth = _calc_omd_gasbildung(inp)
        if val > 0:
            return val, meth
    if inp.adfom is not None:
        return _calc_omd_faser(inp)
    return _calc_omd_mischfutter(inp)


def _omd_fani(omd_fan1: float, fan: float) -> float:
    """
    FAN-Anpassung der OMD (DLG 503 §4.4):
    OMD_FANi = OMD_FAN1 - ((1.5 + 0.05·(OMD_FAN1 - 65)) · (FANi - 1))
    """
    if fan <= 1.0:
        return omd_fan1
    delta = (1.5 + 0.05 * (omd_fan1 - 65.0)) * (fan - 1.0)
    return max(omd_fan1 - delta, 50.0)


def _ch4e_fani(ch4e_fan1: float, fan: float) -> float:
    """
    FAN-Anpassung CH4E (DLG 503 §4.4):
    CH4E_FANi = (CH4E_FAN1 + 0.9·(FANi - 1)) / FANi
    """
    if fan <= 0:
        return ch4e_fan1
    return (ch4e_fan1 + 0.9 * (fan - 1.0)) / fan


def berechne_energie(inp: AnalytikInput, modus: str = "beratung") -> EnergieErgebnis:
    """
    Energie-Bewertung nach DLG 503 (10/2025) / GfE 2023.
    Gibt ME_FAN1 und ME_FANi (MJ/kg TM) zurück.
    """
    res = EnergieErgebnis(modus=modus, fan_input=inp.fan)

    # 1) GE
    ge_tm = _calc_ge(inp)
    # Umrechnung auf OM-Basis: GE_OM = GE_TM / (1 - CA/1000)
    om_anteil = max(1.0 - inp.ca / 1000.0, 0.1)
    ge_om = ge_tm / om_anteil
    res.ge_mj_kg_om = round(ge_om, 3)

    # 2) OMD_FAN1 — Methodenwahl
    omd_fan1, methode = _select_omd_method(inp)
    res.omd_fan1 = round(omd_fan1, 2)
    res.omd_methode = methode

    # 3) ED_FAN1 (DLG 503): ED = OMD - 3.3
    ed_fan1 = omd_fan1 - 3.3
    res.ed_fan1 = round(ed_fan1, 2)

    # 4) DE_FAN1 (MJ/kg OM)
    de_fan1 = ge_om * (ed_fan1 / 100.0)
    res.de_fan1 = round(de_fan1, 3)

    # 5) Harnenergie UE (MJ/kg OM): UE = 0.0037 · CP [g/kg OM]
    cp_om = inp.cp / om_anteil
    ue = 0.0037 * cp_om
    res.ue = round(ue, 3)

    # 6) Methan-Energie CH4E_FAN1 (MJ/kg OM): CH4E = 0.7 + 0.014 · OMD_FAN1
    ch4e_fan1 = 0.7 + 0.014 * omd_fan1
    res.ch4e_fan1 = round(ch4e_fan1, 3)

    # 7) ME_FAN1 (MJ/kg OM) = DE - UE - CH4E
    me_fan1_om = de_fan1 - ue - ch4e_fan1
    res.me_fan1_mj_kg_om = round(me_fan1_om, 3)

    # 8) ME_FAN1 auf TM-Basis: ME_TM = ME_OM · (1 - CA/1000)
    me_fan1_tm = me_fan1_om * om_anteil
    res.me_fan1_mj_kg_tm = round(me_fan1_tm, 3)

    # 9) FAN-Anpassung für FANi
    omd_fani = _omd_fani(omd_fan1, inp.fan)
    res.omd_fani = round(omd_fani, 2)
    ch4e_fani = _ch4e_fani(ch4e_fan1, inp.fan)
    res.ch4e_fani = round(ch4e_fani, 3)

    ed_fani = omd_fani - 3.3
    de_fani = ge_om * (ed_fani / 100.0)
    me_fani_om = de_fani - ue - ch4e_fani
    me_fani_tm = me_fani_om * om_anteil
    res.me_fani_mj_kg_om = round(me_fani_om, 3)
    res.me_fani_mj_kg_tm = round(me_fani_tm, 3)

    return res


def _calc_dom(inp: AnalytikInput, omd: float) -> float:
    """
    Verdauliche organische Substanz (DOM) in g/kg TM.
    DOM = OM × OMD/100
    """
    om = 1000.0 - inp.ca
    return om * omd / 100.0


def _calc_mcp(dom: float) -> float:
    """
    MCP aus DOM (DLG 504 §3.2 nach GfE 2023).
    MCP [g/kg TM] = DOM × 0.149, max. 180 g MCP / kg DOM
    """
    mcp = dom * 0.149
    mcp_max = dom * 180.0 / 1000.0  # max 180 g/kg DOM
    return min(mcp, mcp_max)


def berechne_protein(inp: AnalytikInput, omd_fan1: float, modus: str = "beratung") -> ProteinErgebnis:
    """
    Protein-Bewertung nach DLG 504 (10/2025) / GfE 2023 (sidP-System).
    """
    res = ProteinErgebnis(modus=modus)
    res.cp = inp.cp

    # RDP / UDP
    rdp = inp.cp * inp.rdp_anteil
    udp = inp.cp - rdp
    res.rdp = round(rdp, 2)
    res.udp = round(udp, 2)

    # sidP aus UDP
    sidp_udp = udp * inp.si_dudp
    res.sidp_udp = round(sidp_udp, 2)

    # DOM und MCP
    dom = _calc_dom(inp, omd_fan1)
    res.dom = round(dom, 2)
    mcp = _calc_mcp(dom)
    res.mcp = round(mcp, 2)

    # sidP aus MCP (annahme: siD von MCP ≈ 0.80 nach GfE 2023)
    sidp_mcp = mcp * 0.80
    res.sidp_mcp = round(sidp_mcp, 2)

    # sidP gesamt
    res.sidp_gesamt = round(sidp_udp + sidp_mcp, 2)

    # RMD (ruminale mikrobielle Differenz) = MCP - RDP·MCP_per_RDP_faktor
    # RMD > 0: ausreichend N für MCP-Synthese; RMD < 0: N-Mangel
    rmd = mcp - rdp * 0.80
    res.rmd = round(rmd, 2)

    return res


def berechne_naehrwerte(inp: AnalytikInput, modus: str = "beratung") -> NaehrwertErgebnis:
    """
    Vollständige Nährwertberechnung nach DLG 503 + DLG 504.

    Args:
        inp: Analytik-Eingangsmatrix (Laborwerte oder Tabellenwerte)
        modus: 'beratung' (beste Schätzung) oder 'deklaration' (amtliche Gleichung)

    Returns:
        NaehrwertErgebnis mit Energie- und Protein-Kennzahlen + Audit-Feldern
    """
    if modus == "deklaration":
        # Für die amtliche Kontrolle: immer Mischfutter-Gleichung
        inp_dekl = inp.__class__(**{k: v for k, v in inp.__dict__.items()})
        inp_dekl.elos = None
        inp_dekl.gasbildung_200h = None
        inp_dekl.adfom = None
        energie = berechne_energie(inp_dekl, modus)
    else:
        energie = berechne_energie(inp, modus)

    protein = berechne_protein(inp, energie.omd_fan1, modus)

    # Konventionelle Kennzahlen für Legacy-Kompatibilität (Deklaration nach VO 767/2009)
    # NEL ≈ ME_FAN1 × 0.6 (vereinfachter Faktor für Milchkuhration)
    nel = energie.me_fan1_mj_kg_tm * 0.60
    # nXP ≈ sidP × 1.05 (Näherung, da nXP = MCP + UDP (verd.))
    nxp = protein.sidp_gesamt * 1.05

    return NaehrwertErgebnis(
        energie=energie,
        protein=protein,
        rohprotein_g_kg_tm=round(inp.cp, 2),
        rohfett_g_kg_tm=round(inp.cl, 2),
        rohasche_g_kg_tm=round(inp.ca, 2),
        nel_mj_kg_tm=round(nel, 3),
        nxp_g_kg_tm=round(nxp, 2),
    )
