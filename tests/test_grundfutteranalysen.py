"""
Tests für Grundfutter-Analysen: LUFA-Parser + API-Endpoints + DB-Modell.

Referenz: LUFA Nord-West Prüfbericht 26FG003920 (Kleegras 2025, Grassilage)
"""

import io
import pytest
from unittest.mock import MagicMock, patch

from app.api.v1.endpoints.grundfutter_analysen import (
    parse_lufa_pdf_text,
    parse_lufa_csv,
    _de_float,
    _parse_date_de,
)


# ---------------------------------------------------------------------------
# Fixtures: realer Prüfbericht-Text (aus LUFA Nord-West 26FG003920)
# ---------------------------------------------------------------------------

LUFA_SAMPLE_TEXT = """
Institut für Futtermittel
LUFA Nord-West

Prüfbericht
Oldenburg, 24.03.2026
Berichts-Version: 1
Kundennummer: 50200509     Eingangsdatum: 20.03.2026
Auftragsnummer: 5074595    Untersuchungsbeginn: 20.03.2026
Probe-Nr.: 26FG003920      Untersuchungsende: 24.03.2026
Probenart: Grassilage
Erntetermin: 20.08.2025
Bezeichnung:
(nach Angabe des Einsenders)
Kleegras 2025
Probenahme: Weerda (#6)

Parameter      Ergebnis OS    Berechnet auf TS    Zielwert    Einheit

Aussehen       auffällig/ Produktuntypisch
Geruch         Normal/Produkttypisch
pH-Wert        5,9
Trockensubstanz 81,9                              30,0 bis 40,0 %
Rohprotein     9,1            11,1                < 17,0 %
Rohfaser       24,2           29,5                22,0 bis 25,0 %
ADFom          31,3           38,2                25,0 bis 30,0 %
aNDFom         44,1           53,9                40,0 bis 48,0 %
ADL            5,4            6,6                 < 3,0 %
Hemicellulose  12,8           15,6                %
Gasbildung                    41,7                > 52,0 ml/200mg
Gesamtzucker   5,2            6,3                 2,0 bis 10,0 %
NFC (Nicht-Faser-Kohlenhydrate) 22,0             26,8                %
Rohfett        1,1            1,4                 %
Rohasche       5,6            6,9                 < 10,0 %
Strukturwert                  3,49                2,60 bis 2,90
ME-Rind        6,9            8,4                 > 10,4 MJ/kg
NEL            3,9            4,8                 > 6,2 MJ/kg
Nutzbares Rohprotein (nXP)    91    112           > 135 g/kg
Nutzbares Rohprotein (nXP)
(UDP aus XP-Fraktionierung)   102   124           > 135 g/kg
Ruminale N-Bilanz (RNB)       -0,1  -0,1          < 6,0 g/kg
Ruminale N-Bilanz (RNB)
(UDP aus XP-Fraktionierung)   -1,7  -2,1          g/kg
Reineiweiß n. Barnstein       7,2   8,8            %
Anteil Reineiweiß a. Rohprotein     79,4           > 50,0 %
A (NPN)        1,6            2,0                 %
B1 (Pufferlösl. Reinprotein)  0,4   0,4            %
B2 (Pufferunlösl. Reinprotein) 3,8  4,6            %
B3 (Zellwandgeb. lösl.
Reinprotein)   2,3            2,8                 %
C (Zellwandgeb. unlösl.
Reinprotein)   1,1            1,3                 %
UDP 2                         295                 g/kg XP
UDP 5                         417                 > 150 g/kg XP
UDP 8                         493                 g/kg XP
Verdaulichkeit der org. Masse
(OMD)                         63,6                > 76,0 %
Bruttoenergie (GE)            14,93  18,23         MJ/kg
Umsetzbare Energie (ME)       7,5    9,1           > 11,2 MJ/kg
sidP (dünndarmverdauliches
Protein WK)                   60,5                g/kg
sidLys (dünndarmverdauliches
Lys Wiederkäuer)              5,97                g/kg
sidMet (dünndarmverdauliches
Met Wiederkäuer)              1,85                g/kg
RMD (Ruminale Mikrobielle
Differenz)                    1,2                 g N/kg
a (rasch abbaubare Fraktion des 57,0 %
b (potentiell abbaubare Fraktion 35,0 %
c (Abbaurate der Fraktion b; 12,0 %h
lag (Verzögerungszeit des
ruminalen CP-Abbaus;
Wiederkäuer GfE 2023)         0,0                 h

Durchschnittswerte Grassilage Ernte 2025: TS 37,8 %; bezogen auf 100 % TS:
Calcium 0,55 %; Phosphor 0,35 %; Natrium 0,26 %; Magnesium 0,22 %; Kalium 2,82 %;
"""

LUFA_CSV_SAMPLE = """Probe-Nr;Bezeichnung;Probenart;Trockensubstanz;Rohprotein;Rohfaser;aNDFom;ADFom;NEL;ME-Rind;nXP;RNB
26FG003920;Kleegras 2025;Grassilage;81,9;11,1;29,5;53,9;38,2;4,8;8,4;112;-0,1
"""


# ---------------------------------------------------------------------------
# Unit: _de_float
# ---------------------------------------------------------------------------

class TestDeFloat:
    def test_komma_zu_punkt(self):
        assert _de_float("3,49") == pytest.approx(3.49)

    def test_negativ(self):
        assert _de_float("-0,1") == pytest.approx(-0.1)

    def test_kleiner_zeichen(self):
        assert _de_float("< 1,0") is None

    def test_strich(self):
        assert _de_float("-") is None

    def test_leer(self):
        assert _de_float("") is None

    def test_none(self):
        assert _de_float(None) is None

    def test_integer(self):
        assert _de_float("112") == pytest.approx(112.0)


# ---------------------------------------------------------------------------
# Unit: _parse_date_de
# ---------------------------------------------------------------------------

class TestParseDateDe:
    def test_de_format(self):
        from datetime import date
        assert _parse_date_de("20.08.2025") == date(2025, 8, 20)

    def test_iso_format(self):
        from datetime import date
        assert _parse_date_de("2026-03-24") == date(2026, 3, 24)

    def test_none(self):
        assert _parse_date_de(None) is None

    def test_leer(self):
        assert _parse_date_de("") is None


# ---------------------------------------------------------------------------
# Integration: LUFA PDF-Parser (Text-Modus)
# ---------------------------------------------------------------------------

class TestLufaPdfParser:
    """Testet den Regex-Parser gegen den echten LUFA Nord-West Berichtstext."""

    def setup_method(self):
        self.result = parse_lufa_pdf_text(LUFA_SAMPLE_TEXT, "Prüfbericht 26FG003920.pdf")
        self.p = self.result.parsed

    def test_labor_erkannt(self):
        assert self.p.labor is not None
        assert "LUFA" in self.p.labor

    def test_probe_nr(self):
        assert self.p.probe_nr == "26FG003920"

    def test_auftragsnummer(self):
        assert self.p.auftragsnummer == "5074595"

    def test_probenart_grassilage(self):
        assert self.p.probenart == "Grassilage"

    def test_bezeichnung(self):
        assert "Kleegras" in (self.p.bezeichnung or "")

    def test_erntetermin(self):
        from datetime import date
        assert self.p.erntetermin == date(2025, 8, 20)

    def test_trockensubstanz(self):
        assert self.p.trockensubstanz_os == pytest.approx(81.9)

    def test_ph_wert(self):
        assert self.p.ph_wert == pytest.approx(5.9)

    def test_rohprotein(self):
        assert self.p.rohprotein_ts == pytest.approx(11.1)

    def test_rohfaser(self):
        assert self.p.rohfaser_ts == pytest.approx(29.5)

    def test_adfom(self):
        assert self.p.adfom_ts == pytest.approx(38.2)

    def test_andfom(self):
        assert self.p.andfom_ts == pytest.approx(53.9)

    def test_adl(self):
        assert self.p.adl_ts == pytest.approx(6.6)

    def test_nel(self):
        assert self.p.nel_ts == pytest.approx(4.8)

    def test_me_rind(self):
        assert self.p.me_rind_gfe2008_ts == pytest.approx(8.4)

    def test_strukturwert(self):
        assert self.p.strukturwert_ts == pytest.approx(3.49)

    def test_rnb(self):
        assert self.p.rnb_ts == pytest.approx(-0.1)

    def test_gesamtzucker(self):
        assert self.p.gesamtzucker_ts == pytest.approx(6.3)

    def test_udp5(self):
        assert self.p.udp5_ts == pytest.approx(417.0)

    def test_udp8(self):
        assert self.p.udp8_ts == pytest.approx(493.0)

    def test_omd(self):
        assert self.p.omd_ts == pytest.approx(63.6)

    def test_cp_abbau_a(self):
        assert self.p.cp_abbau_a_ts == pytest.approx(57.0)

    def test_cp_abbau_b(self):
        assert self.p.cp_abbau_b_ts == pytest.approx(35.0)

    def test_cp_abbau_c(self):
        assert self.p.cp_abbau_c_ts == pytest.approx(12.0)

    def test_calcium(self):
        assert self.p.calcium_ts == pytest.approx(0.55)

    def test_phosphor(self):
        assert self.p.phosphor_ts == pytest.approx(0.35)

    def test_natrium(self):
        assert self.p.natrium_ts == pytest.approx(0.26)

    def test_magnesium(self):
        assert self.p.magnesium_ts == pytest.approx(0.22)

    def test_kalium(self):
        assert self.p.kalium_ts == pytest.approx(2.82)

    def test_quelle_datei(self):
        assert self.p.quelle_datei == "Prüfbericht 26FG003920.pdf"

    def test_confidence_trotz_warnung(self):
        # Das Sample hat keine Energie-Zielwerte direkt → Parser warnt ggf.
        assert self.result.confidence in ("high", "medium", "low")

    def test_keine_parse_exception(self):
        # Robustheit: kein uncaught Exception bei leerem Text
        r = parse_lufa_pdf_text("", "leer.pdf")
        assert r.parsed.bezeichnung is not None


# ---------------------------------------------------------------------------
# Integration: CSV-Parser
# ---------------------------------------------------------------------------

class TestLufaCsvParser:
    def setup_method(self):
        self.parsed = parse_lufa_csv(LUFA_CSV_SAMPLE, "export.csv")

    def test_bezeichnung(self):
        assert "Kleegras" in self.parsed.bezeichnung

    def test_trockensubstanz(self):
        assert self.parsed.trockensubstanz_os == pytest.approx(81.9)

    def test_rohprotein(self):
        assert self.parsed.rohprotein_ts == pytest.approx(11.1)

    def test_nel(self):
        assert self.parsed.nel_ts == pytest.approx(4.8)

    def test_andfom(self):
        assert self.parsed.andfom_ts == pytest.approx(53.9)

    def test_rnb_negativ(self):
        assert self.parsed.rnb_ts == pytest.approx(-0.1)

    def test_leeres_csv_fehler(self):
        with pytest.raises(ValueError):
            parse_lufa_csv("", "leer.csv")


# ---------------------------------------------------------------------------
# Zielwert-Prüfung: Qualitätsbeurteilung Kleegras 2025
# ---------------------------------------------------------------------------

class TestKleegrasQualitaetsbeurteilung:
    """
    Prüft, ob die geparsten Werte korrekt außerhalb der LUFA-Zielwerte liegen.
    Kleegras 2025 war erkennbar qualitativ unterdurchschnittlich.
    """

    def setup_method(self):
        r = parse_lufa_pdf_text(LUFA_SAMPLE_TEXT)
        self.p = r.parsed

    def test_ts_zu_hoch(self):
        # Zielwert 30–40%, Ist: 81,9% → zu trocken
        assert self.p.trockensubstanz_os > 40

    def test_nel_unter_zielwert(self):
        # Zielwert >6,2 MJ/kg, Ist: 4,8 MJ/kg → Energiemangel
        assert self.p.nel_ts < 6.2

    def test_andfom_ueber_zielwert(self):
        # Zielwert 40–48%, Ist: 53,9% → zu faserreich
        assert self.p.andfom_ts > 48.0

    def test_adl_ueber_zielwert(self):
        # Zielwert <3%, Ist: 6,6% → zu verholzt
        assert self.p.adl_ts > 3.0

    def test_gasbildung_unter_zielwert(self):
        # Zielwert >52 ml/200mg, Ist: 41,7 → schlechte Verdaulichkeit
        assert self.p.gasbildung_ts < 52.0

    def test_strukturwert_ueber_zielwert(self):
        # Zielwert 2,6–2,9, Ist: 3,49 → zu strukturreich
        assert self.p.strukturwert_ts > 2.9
