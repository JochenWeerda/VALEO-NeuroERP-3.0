"""
Grundfutter-Analysen API

Verwaltung und Import von Laborprüfberichten (LUFA / VDLUFA-Standard).

Endpunkte:
  GET    /grundfutter-analysen            — Liste aller Analysen (Tenant)
  GET    /grundfutter-analysen/{id}       — Einzelanalyse
  POST   /grundfutter-analysen            — Manuelle Anlage
  PATCH  /grundfutter-analysen/{id}       — Korrektur / Verifizierung
  DELETE /grundfutter-analysen/{id}       — Löschen
  POST   /grundfutter-analysen/upload-pdf — PDF-Import (LUFA-Prüfbericht)
  POST   /grundfutter-analysen/upload-csv — CSV-Import (Labor-Export)
  POST   /grundfutter-analysen/{id}/as-feed — In Futtermittel-DB übernehmen
"""

from __future__ import annotations

import csv
import io
import logging
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import Response, APIRouter, Depends, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.uuid7 import uuid7
from app.infrastructure.models.futtermittel_models import GrundfutterAnalyse, RationsZugang

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.grundfutter_analysen_schemas import GrundfutterAnalysenOut


router = APIRouter(tags=["agrar", "futtermittel", "grundfutter-analysen"])


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class GrundfutterAnalyseIn(BaseModel):
    bezeichnung: str
    probenart: Optional[str] = None
    labor: Optional[str] = None
    probe_nr: Optional[str] = None
    auftragsnummer: Optional[str] = None
    kundennummer: Optional[str] = None
    erntetermin: Optional[date] = None
    eingangsdatum: Optional[date] = None
    analyse_datum: Optional[date] = None
    probenahme_ort: Optional[str] = None
    schnitt: Optional[int] = None
    quelle_datei: Optional[str] = None
    # Sensorik
    aussehen: Optional[str] = None
    geruch: Optional[str] = None
    ph_wert: Optional[float] = None
    # Grundnährstoffe
    trockensubstanz_os: Optional[float] = None
    rohprotein_ts: Optional[float] = None
    rohfaser_ts: Optional[float] = None
    rohfett_ts: Optional[float] = None
    rohasche_ts: Optional[float] = None
    gesamtzucker_ts: Optional[float] = None
    sand_ts: Optional[float] = None
    nfc_ts: Optional[float] = None
    # Faser
    adfom_ts: Optional[float] = None
    andfom_ts: Optional[float] = None
    adl_ts: Optional[float] = None
    hemicellulose_ts: Optional[float] = None
    # Gasbildung / OMD
    gasbildung_ts: Optional[float] = None
    omd_ts: Optional[float] = None
    # Energie
    me_rind_gfe2008_ts: Optional[float] = None
    nel_ts: Optional[float] = None
    me_gfe2023_ts: Optional[float] = None
    bruttoenergie_ts: Optional[float] = None
    strukturwert_ts: Optional[float] = None
    # Protein
    nxp_ts: Optional[float] = None
    nxp_udp_ts: Optional[float] = None
    rnb_ts: Optional[float] = None
    rnb_udp_ts: Optional[float] = None
    reineiweis_ts: Optional[float] = None
    anteil_reineiweis_ts: Optional[float] = None
    # XP-Fraktionierung
    xp_fraktion_a_ts: Optional[float] = None
    xp_fraktion_b1_ts: Optional[float] = None
    xp_fraktion_b2_ts: Optional[float] = None
    xp_fraktion_b3_ts: Optional[float] = None
    xp_fraktion_c_ts: Optional[float] = None
    udp2_ts: Optional[float] = None
    udp5_ts: Optional[float] = None
    udp8_ts: Optional[float] = None
    # GfE 2023
    sidp_ts: Optional[float] = None
    sidlys_ts: Optional[float] = None
    sidmet_ts: Optional[float] = None
    rmd_ts: Optional[float] = None
    # CP-Kinetik
    cp_abbau_a_ts: Optional[float] = None
    cp_abbau_b_ts: Optional[float] = None
    cp_abbau_c_ts: Optional[float] = None
    cp_abbau_lag_ts: Optional[float] = None
    # Mineralstoffe
    calcium_ts: Optional[float] = None
    phosphor_ts: Optional[float] = None
    natrium_ts: Optional[float] = None
    magnesium_ts: Optional[float] = None
    kalium_ts: Optional[float] = None
    notizen: Optional[str] = None


class GrundfutterAnalysePatch(BaseModel):
    verifiziert: Optional[bool] = None
    notizen: Optional[str] = None
    bezeichnung: Optional[str] = None
    # alle Messwerte optional überschreibbar
    rohprotein_ts: Optional[float] = None
    nel_ts: Optional[float] = None
    me_gfe2023_ts: Optional[float] = None
    nxp_ts: Optional[float] = None
    rnb_ts: Optional[float] = None
    andfom_ts: Optional[float] = None
    adfom_ts: Optional[float] = None
    trockensubstanz_os: Optional[float] = None


class ParseResult(BaseModel):
    parsed: GrundfutterAnalyseIn
    confidence: str = "high"
    warnings: List[str] = Field(default_factory=list)
    raw_text_preview: Optional[str] = None


# ---------------------------------------------------------------------------
# LUFA PDF-Parser
# ---------------------------------------------------------------------------

def _de_float(s: Optional[str]) -> Optional[float]:
    """Deutschen Dezimaltrennzeichen → float. Gibt None bei '<' oder Leerzeichen."""
    if not s:
        return None
    s = s.strip()
    if s.startswith("<") or s == "-" or s == "":
        return None
    s = s.replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date_de(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _extract_value(text: str, label: str) -> Optional[str]:  # noqa: F811
    """Sucht nach 'Label <zahl>' mit optionalem Trennzeichen."""
    pattern = rf"{re.escape(label)}\s+([<\d,\.\-]+)"
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m else None


def parse_lufa_pdf_text(full_text: str, filename: str = "") -> ParseResult:
    """
    Parst den Textinhalt eines LUFA-Prüfberichts (Nord-West-Format).
    Unterstützt das Prüfbericht-Layout mit Spalten:
      Parameter | Ergebnis OS | Berechnet auf TS | Zielwert | Einheit

    Struktur des LUFA-Textes (alle Werte durch pdfplumber extrahiert):
    - Kopfzeile: Probe-Nr., Auftragsnummer, Probenart, Erntetermin, Bezeichnung
    - Parameterzeilen: Parametername, OS-Wert, TS-Wert (fett), optional Zielwert
    """
    t = full_text
    warnings: List[str] = []

    def find(label: str, ts_col: bool = True) -> Optional[float]:
        """Sucht Wert nach Label — bevorzugt TS-Spalte (zweiter numerischer Block)."""
        pattern = rf"{re.escape(label)}\s+([\d,\.\-<]+)(?:\s+([\d,\.\-<]+))?"
        m = re.search(pattern, t, re.IGNORECASE)
        if not m:
            return None
        if ts_col and m.group(2):
            return _de_float(m.group(2))
        return _de_float(m.group(1))

    def find_os(label: str) -> Optional[float]:
        return find(label, ts_col=False)

    def find_meta(label: str) -> Optional[str]:
        m = re.search(rf"{re.escape(label)}[:\s.]+([^\n]+)", t, re.IGNORECASE)
        if not m:
            return None
        # Schneide alles nach dem ersten Whitespace-Block ab (zweite Spalte / Label)
        val = m.group(1).strip()
        # Wenn mehrere Tokens: nur erstes nehmen (Auftragsnummer hat Tab-getrennte Nachbarspalte)
        first = val.split()[0] if val else val
        return first

    # --- Metadaten ---
    probe_nr_m = re.search(r"Probe-Nr\.?[:\s]+(\w+)", t, re.IGNORECASE)
    probe_nr = probe_nr_m.group(1).strip() if probe_nr_m else None
    auftragsnummer = find_meta("Auftragsnummer")
    kundennummer = find_meta("Kundennummer")
    erntetermin = _parse_date_de(find_meta("Erntetermin"))
    eingangsdatum = _parse_date_de(find_meta("Eingangsdatum"))
    analyse_datum = _parse_date_de(find_meta("Untersuchungsende"))

    # Labor aus Kopfzeile
    labor = "LUFA Nord-West" if "lufa nord-west" in t.lower() else None
    if not labor and "lufa" in t.lower():
        labor = "LUFA"

    # Probenart
    probenart = None
    for art in ["Grassilage", "Maissilage", "Heu", "Anwelksilage", "Stroh", "Kleegrassilage", "Grünmais"]:
        if art.lower() in t.lower():
            probenart = art
            break

    # Bezeichnung — zwei Formate: "Bezeichnung: Kleegras 2025" oder mehrzeilig nach "(nach Angabe...)"
    bezeichnung_m = re.search(r"Bezeichnung[:\s]*\(nach Angabe des Einsenders\)\s*([^\n]+)", t, re.IGNORECASE)
    if not bezeichnung_m:
        bezeichnung_m = re.search(r"Bezeichnung:\s*([^\n]+)", t, re.IGNORECASE)
    bezeichnung = bezeichnung_m.group(1).strip() if bezeichnung_m else (probenart or "Unbekannte Probe")

    # Schnitt
    schnitt_m = re.search(r"(\d+)\.\s*Schnitt", t, re.IGNORECASE)
    schnitt = int(schnitt_m.group(1)) if schnitt_m else None

    # Probenahme-Ort
    probenahme_m = re.search(r"Probenahme[:\s]+([^\n]+)", t, re.IGNORECASE)
    probenahme_ort = probenahme_m.group(1).strip() if probenahme_m else None

    # --- Sensorik ---
    aussehen_m = re.search(r"Aussehen\s+([^\n]+)", t, re.IGNORECASE)
    aussehen = aussehen_m.group(1).strip() if aussehen_m else None
    geruch_m = re.search(r"Geruch\s+([^\n]+)", t, re.IGNORECASE)
    geruch = geruch_m.group(1).strip() if geruch_m else None
    ph_wert = find_os("pH-Wert")

    # --- Grundnährstoffe ---
    # TS: Format "Trockensubstanz 81,9 30,0 bis 40,0 %" → nur erste Zahl = OS-Wert
    ts_m = re.search(r"^Trockensubstanz\s+([\d,\.]+)", t, re.IGNORECASE | re.MULTILINE)
    ts_os = _de_float(ts_m.group(1)) if ts_m else find_os("Trockensubstanz")
    rohprotein = find("Rohprotein")
    rohfaser = find("Rohfaser")
    rohfett = find("Rohfett")
    rohasche = find("Rohasche")
    gesamtzucker = find("Gesamtzucker")
    # NFC: "NFC (Nicht-Faser-Kohlenhydrate) 22,0 26,8 %" → zweite Zahl = TS
    nfc_m = re.search(r"NFC[^\n]+([\d,\.]+)\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    nfc = _de_float(nfc_m.group(2)) if nfc_m else find("NFC")
    sand_m = re.search(r"Sand\s+[-<\d,\.]+\s+([\d,\.]+)", t, re.IGNORECASE)
    sand = _de_float(sand_m.group(1)) if sand_m else None

    # --- Faser ---
    adfom = find("ADFom")
    andfom = find("aNDFom")
    adl = find("ADL")
    hemi = find("Hemicellulose")

    # --- Gasbildung / OMD ---
    gasbildung_m = re.search(r"Gasbildung\s+([\d,\.]+)", t, re.IGNORECASE)
    gasbildung = _de_float(gasbildung_m.group(1)) if gasbildung_m else None
    omd_m = re.search(r"Verdaulichkeit der org\. Masse.*?([\d,\.]+)", t, re.IGNORECASE | re.DOTALL)
    omd = _de_float(omd_m.group(1)) if omd_m else None

    # --- Energie ---
    me_rind = find("ME-Rind")
    # NEL: "NEL (Netto-Energie-Lakt.) 3,9  4,8  > 6,2 MJ/kg" → 3 Zahlen: OS, TS, Zielwert
    # Expliziter Regex: greift OS + TS und nimmt TS (zweite Zahl)
    nel_m = re.search(r"NEL[^\n]*?([\d,\.]+)\s+([\d,\.]+)\s+[>< ]", t, re.IGNORECASE)
    nel = _de_float(nel_m.group(2)) if nel_m else find("NEL")
    # GfE 2023 ME (Seite 3 — "Umsetzbare Energie (ME)")
    me23_m = re.search(r"Umsetzbare Energie \(ME\)\s+([\d,\.]+)\s+([\d,\.]+)", t, re.IGNORECASE)
    me_gfe2023 = _de_float(me23_m.group(2)) if me23_m else None
    ge_m = re.search(r"Bruttoenergie \(GE\)\s+([\d,\.]+)\s+([\d,\.]+)", t, re.IGNORECASE)
    bruttoenergie = _de_float(ge_m.group(2)) if ge_m else None
    # Strukturwert: nur TS-Wert (einzige Zahl vor dem Zielwert-Bereich "2,60 bis ...")
    sv_m = re.search(r"Strukturwert\s+([\d,\.]+)\s+[\d,]+ bis", t, re.IGNORECASE)
    if sv_m:
        strukturwert = _de_float(sv_m.group(1))
    else:
        sv_m2 = re.search(r"Strukturwert\s+([\d,\.]+)", t, re.IGNORECASE)
        strukturwert = _de_float(sv_m2.group(1)) if sv_m2 else None

    # --- Protein ---
    nxp_m = re.search(r"Nutzbares Rohprotein \(nXP\)\s+([\d,\.]+)\s+([\d,\.]+)", t, re.IGNORECASE)
    nxp = _de_float(nxp_m.group(2)) if nxp_m else None
    nxp_udp_m = re.search(r"Nutzbares Rohprotein \(nXP\)\s*\(UDP.*?\)\s+([\d,\.]+)\s+([\d,\.]+)", t, re.IGNORECASE | re.DOTALL)
    nxp_udp = _de_float(nxp_udp_m.group(2)) if nxp_udp_m else None
    rnb_m = re.search(r"Ruminale N-Bilanz \(RNB\)\s+([-\d,\.]+)\s+([-\d,\.]+)", t, re.IGNORECASE)
    rnb = _de_float(rnb_m.group(2)) if rnb_m else None
    rnb_udp_m = re.search(r"Ruminale N-Bilanz \(RNB\)\s*\(UDP.*?\)\s+([-\d,\.]+)\s+([-\d,\.]+)", t, re.IGNORECASE | re.DOTALL)
    rnb_udp = _de_float(rnb_udp_m.group(2)) if rnb_udp_m else None
    reineiweis = find("Reineiweiß n. Barnstein")
    anteil_rei = find("Anteil Reineiweiß")

    # --- XP-Fraktionierung ---
    # Format: "A (NPN) 1,6 2,0 %" → OS=1,6 TS=2,0 oder einzeilig "A (NPN) 2,0 %"
    xp_a = find("A (NPN)")
    xp_b1_m = re.search(r"B1[^\n]+([\d,\.]+)\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    xp_b1 = _de_float(xp_b1_m.group(2)) if xp_b1_m else find("B1")
    xp_b2_m = re.search(r"B2[^\n]+([\d,\.]+)\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    xp_b2 = _de_float(xp_b2_m.group(2)) if xp_b2_m else find("B2")
    xp_b3_m = re.search(r"B3[^\n]*\n?[^\n]*([\d,\.]+)\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    xp_b3 = _de_float(xp_b3_m.group(2)) if xp_b3_m else None
    xp_c_m = re.search(r"^C \(Zellwandgeb[^\n]+([\d,\.]+)\s+([\d,\.]+)\s*%", t, re.IGNORECASE | re.MULTILINE)
    if not xp_c_m:
        xp_c_m = re.search(r"Reinprotein\)\s+([\d,\.]+)\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    xp_c = _de_float(xp_c_m.group(2)) if xp_c_m else None
    udp2_m = re.search(r"UDP 2\s+([\d,\.]+)", t, re.IGNORECASE)
    udp2 = _de_float(udp2_m.group(1)) if udp2_m else None
    udp5_m = re.search(r"UDP 5\s+([\d,\.]+)", t, re.IGNORECASE)
    udp5 = _de_float(udp5_m.group(1)) if udp5_m else None
    udp8_m = re.search(r"UDP 8\s+([\d,\.]+)", t, re.IGNORECASE)
    udp8 = _de_float(udp8_m.group(1)) if udp8_m else None

    # --- GfE 2023 sidAA ---
    # sidP: "sidP (d?nndarmverdauliches" — Umlaut-robust mit .? für ü/u
    sidp_m = re.search(r"sidP\s+\([^\)]*Protein[^\)]*\)\s+([\d,\.]+)", t, re.IGNORECASE)
    if not sidp_m:
        sidp_m = re.search(r"^sidP[^\n]*\s+([\d,\.]+)", t, re.IGNORECASE | re.MULTILINE)
    sidp = _de_float(sidp_m.group(1)) if sidp_m else None
    sidlys_m = re.search(r"sidLys[^\n]*\s+([\d,\.]+)\s*g/kg", t, re.IGNORECASE)
    sidlys = _de_float(sidlys_m.group(1)) if sidlys_m else None
    sidmet_m = re.search(r"sidMet[^\n]*\s+([\d,\.]+)\s*g/kg", t, re.IGNORECASE)
    sidmet = _de_float(sidmet_m.group(1)) if sidmet_m else None
    rmd_m = re.search(r"RMD[^\n]+?([\d,\.]+)\s*g N/kg", t, re.IGNORECASE)
    rmd = _de_float(rmd_m.group(1)) if rmd_m else None

    # --- CP-Kinetik ---
    # CP-Kinetik: "a (rasch abbaubare Fraktion des 57,0 %" → Zahl am Zeilenende vor %
    cp_a_m = re.search(r"^a \(rasch abbaubare Fraktion.*?\s([\d,\.]+)\s*%", t, re.IGNORECASE | re.MULTILINE)
    cp_a = _de_float(cp_a_m.group(1)) if cp_a_m else None
    cp_b_m = re.search(r"^b \(potentiell abbaubare Fraktion.*?\s([\d,\.]+)\s*%", t, re.IGNORECASE | re.MULTILINE)
    cp_b = _de_float(cp_b_m.group(1)) if cp_b_m else None
    cp_c_m = re.search(r"^c \(Abbaurate der Fraktion.*?\s([\d,\.]+)\s*%", t, re.IGNORECASE | re.MULTILINE)
    cp_c = _de_float(cp_c_m.group(1)) if cp_c_m else None
    lag_m = re.search(r"^lag \(.*?\s([\d,\.]+)\s*h$", t, re.IGNORECASE | re.MULTILINE)
    lag = _de_float(lag_m.group(1)) if lag_m else None

    # --- Mineralstoffe (aus Seite-4-Durchschnittswerten oder eigener Tabelle) ---
    ca_m = re.search(r"Calcium\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    ca = _de_float(ca_m.group(1)) if ca_m else None
    p_m = re.search(r"Phosphor\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    p = _de_float(p_m.group(1)) if p_m else None
    na_m = re.search(r"Natrium\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    na = _de_float(na_m.group(1)) if na_m else None
    mg_m = re.search(r"Magnesium\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    mg = _de_float(mg_m.group(1)) if mg_m else None
    k_m = re.search(r"Kalium\s+([\d,\.]+)\s*%", t, re.IGNORECASE)
    k = _de_float(k_m.group(1)) if k_m else None

    if not probe_nr:
        warnings.append("Probe-Nr. nicht erkannt")
    if ts_os is None:
        warnings.append("Trockensubstanz nicht erkannt")
    if nel is None and me_gfe2023 is None:
        warnings.append("Kein Energiewert erkannt — manuelle Eingabe erforderlich")

    parsed = GrundfutterAnalyseIn(
        bezeichnung=bezeichnung,
        probenart=probenart,
        labor=labor,
        probe_nr=probe_nr,
        auftragsnummer=auftragsnummer,
        kundennummer=kundennummer,
        erntetermin=erntetermin,
        eingangsdatum=eingangsdatum,
        analyse_datum=analyse_datum,
        probenahme_ort=probenahme_ort,
        schnitt=schnitt,
        quelle_datei=filename,
        aussehen=aussehen,
        geruch=geruch,
        ph_wert=ph_wert,
        trockensubstanz_os=ts_os,
        rohprotein_ts=rohprotein,
        rohfaser_ts=rohfaser,
        rohfett_ts=rohfett,
        rohasche_ts=rohasche,
        gesamtzucker_ts=gesamtzucker,
        sand_ts=sand,
        nfc_ts=nfc,
        adfom_ts=adfom,
        andfom_ts=andfom,
        adl_ts=adl,
        hemicellulose_ts=hemi,
        gasbildung_ts=gasbildung,
        omd_ts=omd,
        me_rind_gfe2008_ts=me_rind,
        nel_ts=nel,
        me_gfe2023_ts=me_gfe2023,
        bruttoenergie_ts=bruttoenergie,
        strukturwert_ts=strukturwert,
        nxp_ts=nxp,
        nxp_udp_ts=nxp_udp,
        rnb_ts=rnb,
        rnb_udp_ts=rnb_udp,
        reineiweis_ts=reineiweis,
        anteil_reineiweis_ts=anteil_rei,
        xp_fraktion_a_ts=xp_a,
        xp_fraktion_b1_ts=xp_b1,
        xp_fraktion_b2_ts=xp_b2,
        xp_fraktion_b3_ts=xp_b3,
        xp_fraktion_c_ts=xp_c,
        udp2_ts=udp2,
        udp5_ts=udp5,
        udp8_ts=udp8,
        sidp_ts=sidp,
        sidlys_ts=sidlys,
        sidmet_ts=sidmet,
        rmd_ts=rmd,
        cp_abbau_a_ts=cp_a,
        cp_abbau_b_ts=cp_b,
        cp_abbau_c_ts=cp_c,
        cp_abbau_lag_ts=lag,
        calcium_ts=ca,
        phosphor_ts=p,
        natrium_ts=na,
        magnesium_ts=mg,
        kalium_ts=k,
    )
    confidence = "high" if len(warnings) == 0 else ("medium" if len(warnings) <= 2 else "low")
    return ParseResult(
        parsed=parsed,
        confidence=confidence,
        warnings=warnings,
        raw_text_preview=full_text[:500],
    )


def parse_lufa_csv(content: str, filename: str = "") -> GrundfutterAnalyseIn:
    """Parst einen LUFA-CSV-Export (Semikolon-getrennt, deutsche Dezimaltrennzeichen)."""
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    rows = list(reader)
    if not rows:
        raise ValueError("CSV leer oder kein gültiges Format")

    row = rows[0]

    def g(key: str) -> Optional[float]:
        for k, v in row.items():
            if k and key.lower() in k.lower():
                return _de_float(v)
        return None

    bezeichnung = row.get("Bezeichnung") or row.get("Probe") or row.get("Probenbezeichnung") or "CSV-Import"
    return GrundfutterAnalyseIn(
        bezeichnung=bezeichnung,
        probenart=row.get("Probenart"),
        probe_nr=row.get("Probe-Nr") or row.get("ProbeNr"),
        auftragsnummer=row.get("Auftragsnummer"),
        quelle_datei=filename,
        trockensubstanz_os=g("Trockensubstanz"),
        rohprotein_ts=g("Rohprotein"),
        rohfaser_ts=g("Rohfaser"),
        rohfett_ts=g("Rohfett"),
        rohasche_ts=g("Rohasche"),
        gesamtzucker_ts=g("Zucker"),
        adfom_ts=g("ADFom"),
        andfom_ts=g("aNDFom"),
        adl_ts=g("ADL"),
        nel_ts=g("NEL"),
        me_rind_gfe2008_ts=g("ME-Rind"),
        me_gfe2023_ts=g("ME Wiederkäuer") or g("ME GfE"),
        nxp_ts=g("nXP"),
        rnb_ts=g("RNB"),
        sidp_ts=g("sidP"),
        strukturwert_ts=g("Strukturwert"),
        omd_ts=g("OMD") or g("Verdaulichkeit"),
        calcium_ts=g("Calcium") or g(" Ca "),
        phosphor_ts=g("Phosphor") or g(" P "),
        natrium_ts=g("Natrium") or g(" Na "),
        magnesium_ts=g("Magnesium") or g(" Mg "),
        kalium_ts=g("Kalium") or g(" K "),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_tenant(x_tenant_id: Optional[str] = Header(default=None)) -> str:
    return x_tenant_id or "default"


def _is_portal_request(x_share_token: Optional[str], x_user_email: Optional[str]) -> bool:
    """
    Heuristik: Ein Request gilt als Portal-Request (extern, DSGVO-pflichtig) wenn
    ein Share-Token vorliegt. Interne ERP-Nutzer senden keinen Share-Token und
    sind bereits durch die OIDC-Middleware authentifiziert.
    """
    return bool(x_share_token)


def _check_rations_read(
    tenant_id: str,
    db: Session,
    x_user_email: Optional[str] = None,
    x_share_token: Optional[str] = None,
) -> None:
    """
    DSGVO-Lesezugang: nur für Share-Token-basierte Portal-Zugriffe erzwungen.
    Interne ERP-Nutzer (OIDC-authentifiziert, kein Share-Token) haben immer Zugang
    zu den Daten ihres Mandanten.
    """
    if not _is_portal_request(x_share_token, x_user_email):
        return  # interner ERP-Request — OIDC-Auth reicht

    from datetime import timezone
    now = datetime.now(timezone.utc)

    def _has_access(q_filter) -> bool:
        row = db.query(RationsZugang).filter(
            RationsZugang.tenant_id == tenant_id,
            RationsZugang.ist_aktiv.is_(True),
            RationsZugang.darf_lesen.is_(True),
            *q_filter,
        ).first()
        if row is None:
            return False
        return row.gueltig_bis is None or row.gueltig_bis > now

    if x_share_token and _has_access([RationsZugang.share_token == x_share_token]):
        return
    if x_user_email and _has_access([RationsZugang.empfaenger_email == x_user_email]):
        return

    raise HTTPException(
        status_code=403,
        detail="Kein Lesezugang auf betriebseigene Grundfutterdaten dieses Mandanten.",
    )


def _check_rations_write(
    tenant_id: str,
    db: Session,
    x_user_email: Optional[str] = None,
    x_share_token: Optional[str] = None,
) -> None:
    """
    DSGVO-Schreibzugang: nur für Share-Token-basierte Portal-Zugriffe geprüft.
    Interne ERP-Nutzer schreiben immer (OIDC-authentifiziert).
    """
    if not _is_portal_request(x_share_token, x_user_email):
        return  # interner ERP-Request

    from datetime import timezone
    now = datetime.now(timezone.utc)
    if not x_user_email:
        raise HTTPException(status_code=403, detail="Authentifizierung erforderlich.")
    row = db.query(RationsZugang).filter(
        RationsZugang.tenant_id == tenant_id,
        RationsZugang.empfaenger_email == x_user_email,
        RationsZugang.ist_aktiv.is_(True),
        RationsZugang.darf_grundfutter_anlegen.is_(True),
    ).first()
    if not row or (row.gueltig_bis and row.gueltig_bis < now):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung zum Anlegen/Bearbeiten von Grundfutter-Analysen.",
        )


def _analyse_to_dict(a: GrundfutterAnalyse) -> Dict[str, Any]:
    return {c.name: getattr(a, c.name) for c in a.__table__.columns}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/grundfutter-analysen", summary="Analysen auflisten",
    response_model=GrundfutterAnalysenOut
)
def list_analysen(
    probenart: Optional[str] = Query(default=None),
    verifiziert: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
    x_user_email: Optional[str] = Header(default=None),
    x_share_token: Optional[str] = Header(default=None),
):
    _check_rations_read(tenant_id, db, x_user_email, x_share_token)
    q = db.query(GrundfutterAnalyse).filter(GrundfutterAnalyse.tenant_id == tenant_id)
    if probenart:
        q = q.filter(GrundfutterAnalyse.probenart == probenart)
    if verifiziert is not None:
        q = q.filter(GrundfutterAnalyse.verifiziert == verifiziert)
    total = q.count()
    items = q.order_by(GrundfutterAnalyse.created_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": [_analyse_to_dict(a) for a in items]}


@router.get("/grundfutter-analysen/{analyse_id}", summary="Analyse abrufen",
    response_model=GrundfutterAnalysenOut
)
def get_analyse(
    analyse_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
    x_user_email: Optional[str] = Header(default=None),
    x_share_token: Optional[str] = Header(default=None),
):
    _check_rations_read(tenant_id, db, x_user_email, x_share_token)
    a = db.query(GrundfutterAnalyse).filter(
        GrundfutterAnalyse.id == analyse_id,
        GrundfutterAnalyse.tenant_id == tenant_id,
    ).first()
    if not a:
        raise HTTPException(404, "Analyse nicht gefunden")
    return _analyse_to_dict(a)


@router.post("/grundfutter-analysen", status_code=201, summary="Analyse anlegen",
    response_model=GrundfutterAnalysenOut
)
def create_analyse(
    data: GrundfutterAnalyseIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
    x_user_email: Optional[str] = Header(default=None),
):
    _check_rations_write(tenant_id, db, x_user_email, None)

    # Dublettenprüfung: gleiche Bezeichnung + Probe-Nr. im gleichen Mandanten?
    dupe_q = db.query(GrundfutterAnalyse).filter(
        GrundfutterAnalyse.tenant_id == tenant_id,
        GrundfutterAnalyse.bezeichnung == data.bezeichnung,
    )
    if data.probe_nr:
        dupe_q = dupe_q.filter(GrundfutterAnalyse.probe_nr == data.probe_nr)
    existing = dupe_q.first()
    if existing:
        hint = f" (Probe-Nr. {existing.probe_nr})" if existing.probe_nr else ""
        raise HTTPException(
            409,
            f"Eine Analyse mit der Bezeichnung '{data.bezeichnung}'{hint} wurde bereits gespeichert "
            f"(angelegt am {existing.created_at.strftime('%d.%m.%Y') if existing.created_at else '–'}). "
            f"Bitte Bezeichnung oder Probe-Nr. anpassen, falls es sich um eine neue Probe handelt."
        )

    a = GrundfutterAnalyse(id=uuid7(), tenant_id=tenant_id, **data.model_dump(exclude_none=True))
    db.add(a)
    db.commit()
    db.refresh(a)
    return _analyse_to_dict(a)


@router.patch("/grundfutter-analysen/{analyse_id}", summary="Analyse aktualisieren",
    response_model=None
)
def patch_analyse(
    analyse_id: str,
    data: GrundfutterAnalysePatch,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
    x_user_email: Optional[str] = Header(default=None),
):
    _check_rations_write(tenant_id, db, x_user_email, None)
    a = db.query(GrundfutterAnalyse).filter(
        GrundfutterAnalyse.id == analyse_id,
        GrundfutterAnalyse.tenant_id == tenant_id,
    ).first()
    if not a:
        raise HTTPException(404, "Analyse nicht gefunden")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return _analyse_to_dict(a)


@router.delete("/grundfutter-analysen/{analyse_id}", status_code=204, response_class=Response, response_model=None, summary="Analyse löschen")
def delete_analyse(
    analyse_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
    x_user_email: Optional[str] = Header(default=None),
):
    _check_rations_write(tenant_id, db, x_user_email, None)
    a = db.query(GrundfutterAnalyse).filter(
        GrundfutterAnalyse.id == analyse_id,
        GrundfutterAnalyse.tenant_id == tenant_id,
    ).first()
    if not a:
        raise HTTPException(404, "Analyse nicht gefunden")
    db.delete(a)
    db.commit()
    from fastapi.responses import Response
    return Response(status_code=204)


@router.post("/grundfutter-analysen/upload-pdf", summary="Pdf hochladen",
    response_model=None
)
async def upload_pdf(
    file: UploadFile = File(...),
    save: bool = Query(default=False, description="Direkt in DB speichern"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
):
    """
    LUFA-PDF hochladen und automatisch parsen.

    Strategie:
    1. pdfplumber für Textextraktion (native Text-PDFs)
    2. Falls kein Text erkannt → Hinweis auf Claude Vision (erfordert ANTHROPIC_API_KEY)
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Nur PDF-Dateien erlaubt")

    content = await file.read()

    # Textextraktion via pdfplumber
    full_text = ""
    try:
        import pdfplumber
        import io as _io
        with pdfplumber.open(_io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                pt = page.extract_text() or ""
                full_text += pt + "\n"
    except ImportError:
        raise HTTPException(503, "pdfplumber nicht installiert (pip install pdfplumber)")
    except Exception as e:
        raise HTTPException(422, f"PDF konnte nicht geöffnet werden: {e}")

    if not full_text.strip():
        # Gescanntes PDF → kein Textlayer
        return JSONResponse(
            status_code=422,
            content={
                "error": "scan_pdf",
                "message": (
                    "Das PDF enthält keinen Textlayer (Bildscan). "
                    "Bitte als Foto-Upload verwenden oder Daten manuell eingeben."
                ),
                "hint": "claude_vision_required",
            },
        )

    result = parse_lufa_pdf_text(full_text, filename=file.filename)

    if save:
        a = GrundfutterAnalyse(
            id=uuid7(),
            tenant_id=tenant_id,
            **result.parsed.model_dump(exclude_none=True),
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        return {
            "saved": True,
            "analyse_id": a.id,
            "confidence": result.confidence,
            "warnings": result.warnings,
            "data": _analyse_to_dict(a),
        }

    return {
        "saved": False,
        "confidence": result.confidence,
        "warnings": result.warnings,
        "parsed": result.parsed.model_dump(),
        "raw_text_preview": result.raw_text_preview,
    }


@router.post("/grundfutter-analysen/upload-csv", summary="Csv hochladen",
    response_model=GrundfutterAnalysenOut
)
async def upload_csv(
    file: UploadFile = File(...),
    save: bool = Query(default=False),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
):
    """LUFA-CSV-Export hochladen und parsen."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Nur CSV-Dateien erlaubt")

    raw = await file.read()
    try:
        content = raw.decode("utf-8-sig")  # BOM-safe
    except UnicodeDecodeError:
        content = raw.decode("latin-1")

    try:
        parsed = parse_lufa_csv(content, filename=file.filename)
    except Exception as e:
        raise HTTPException(422, f"CSV-Parsing fehlgeschlagen: {e}")

    if save:
        a = GrundfutterAnalyse(id=uuid7(), tenant_id=tenant_id, **parsed.model_dump(exclude_none=True))
        db.add(a)
        db.commit()
        db.refresh(a)
        return {"saved": True, "analyse_id": a.id, "data": _analyse_to_dict(a)}

    return {"saved": False, "parsed": parsed.model_dump()}


@router.post("/grundfutter-analysen/{analyse_id}/as-feed", summary="As feed promote",
    response_model=GrundfutterAnalysenOut
)
def promote_as_feed(
    analyse_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_get_tenant),
):
    """Übernimmt eine verifizierte Analyse als Einzelfuttermittel in die Futtermittel-DB."""
    from app.infrastructure.models.futtermittel_models import Einzelfuttermittel

    a = db.query(GrundfutterAnalyse).filter(
        GrundfutterAnalyse.id == analyse_id,
        GrundfutterAnalyse.tenant_id == tenant_id,
    ).first()
    if not a:
        raise HTTPException(404, "Analyse nicht gefunden")
    if not a.verifiziert:
        raise HTTPException(409, "Analyse muss zuerst verifiziert werden (PATCH verifiziert=true)")

    # Dublettenprüfung: gleicher Name + Tenant bereits vorhanden?
    existing = db.query(Einzelfuttermittel).filter(
        Einzelfuttermittel.tenant_id == tenant_id,
        Einzelfuttermittel.name == a.bezeichnung,
    ).first()
    if existing:
        raise HTTPException(
            409,
            f"Futtermittel '{a.bezeichnung}' ist bereits in der Datenbank vorhanden "
            f"(Artikel-Nr. {existing.artikel_nummer}). Bitte zuerst das bestehende prüfen oder "
            f"die Bezeichnung der Analyse ändern."
        )

    ef = Einzelfuttermittel(
        id=uuid7(),
        tenant_id=tenant_id,
        artikel_nummer=f"GF-{a.probe_nr or uuid7()[:8]}",
        name=a.bezeichnung,
        art=a.probenart or "Grundfutter",
        herkunft=a.probenahme_ort,
        protein=a.rohprotein_ts,
        energie=float(a.me_gfe2023_ts or a.me_rind_gfe2008_ts or 0),
        faser=a.rohfaser_ts,
        fett=a.rohfett_ts,
        asche=a.rohasche_ts,
        trockensubstanz=a.trockensubstanz_os,
        verfuegbar_t=0,
    )
    db.add(ef)
    db.commit()
    db.refresh(ef)
    return {
        "einzelfuttermittel_id": ef.id,
        "artikel_nummer": ef.artikel_nummer,
        "name": ef.name,
    }
