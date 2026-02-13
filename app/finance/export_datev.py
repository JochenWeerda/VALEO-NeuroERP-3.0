"""
VALEO-NeuroERP - DATEV Export
Exportiert Buchungsdaten im DATEV-ASCII-Format
"""

import csv
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from io import StringIO


class DATEVExporter:
    """DATEV ASCII-Export Generator"""
    
    # DATEV-Format Version
    DATEV_VERSION = "700"
    
    def __init__(self, mandant_nr: str = "1000", berater_nr: str = "1000", wj_beginn: str = "0101"):
        self.mandant_nr = mandant_nr
        self.berater_nr = berater_nr
        self.wj_beginn = wj_beginn
    
    def export_buchungen(self, buchungen: List[Dict[str, Any]], von_datum: str, bis_datum: str) -> str:
        """
        Exportiert Buchungen im DATEV-Format
        
        Args:
            buchungen: Liste von Buchungsdaten (aus finance_buchungsjournal)
            von_datum: Start-Datum (DDMMYYYY)
            bis_datum: End-Datum (DDMMYYYY)
        
        Returns:
            DATEV-CSV als String
        """
        output = StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        
        # Header (Zeile 1)
        header_line1 = [
            "EXTF",                    # Formatname
            self.DATEV_VERSION,        # Versionsnummer
            "21",                      # Datenkategorie (21 = Buchungsstapel)
            "",                        # Formatname (leer)
            "",                        # Formatversion (leer)
            datetime.now().strftime("%Y%m%d%H%M%S"),  # Generiert am
            "",                        # Importiert (leer)
            "RE",                      # Herkunft (RE = Rechnungswesen)
            "",                        # Exportiert von (leer)
            "",                        # Importiert von (leer)
            self.berater_nr,           # Beraternummer
            self.mandant_nr,           # Mandantennummer
            self.wj_beginn,            # WJ-Beginn
            "4",                       # Sachkontenlänge
            von_datum,                 # Datum von
            bis_datum,                 # Datum bis
            "",                        # Bezeichnung
            "",                        # Diktatkürzel
            "1",                       # Buchungstyp (1 = Finanzbuchführung)
            "0",                       # Rechnungslegungszweck
            "",                        # Festschreibung
            "EUR"                      # Währungskennzeichen
        ]
        writer.writerow(header_line1)
        
        # Header (Zeile 2) - Spaltenbeschriftung
        header_line2 = [
            "Umsatz (ohne Soll/Haben-Kz)",
            "Soll/Haben-Kennzeichen",
            "WKZ Umsatz",
            "Kurs",
            "Basis-Umsatz",
            "WKZ Basis-Umsatz",
            "Konto",
            "Gegenkonto (ohne BU-Schlüssel)",
            "BU-Schlüssel",
            "Belegdatum",
            "Belegfeld 1",
            "Belegfeld 2",
            "Skonto",
            "Buchungstext",
            "Postensperre",
            "Diverse Adressnummer",
            "Geschäftspartnerbank",
            "Sachverhalt",
            "Zinssperre",
            "Beleglink",
            "Beleginfo - Art 1",
            "Beleginfo - Inhalt 1",
            "Beleginfo - Art 2",
            "Beleginfo - Inhalt 2",
            "Beleginfo - Art 3",
            "Beleginfo - Inhalt 3",
            "Beleginfo - Art 4",
            "Beleginfo - Inhalt 4",
            "Beleginfo - Art 5",
            "Beleginfo - Inhalt 5",
            "Beleginfo - Art 6",
            "Beleginfo - Inhalt 6",
            "Beleginfo - Art 7",
            "Beleginfo - Inhalt 7",
            "Beleginfo - Art 8",
            "Beleginfo - Inhalt 8",
            "KOST1 - Kostenstelle",
            "KOST2 - Kostenstelle",
            "Kost-Menge",
            "EU-Land u. UStID",
            "EU-Steuersatz",
            "Abw. Versteuerungsart",
            "Sachverhalt L+L",
            "Funktionsergänzung L+L",
            "BU 49 Hauptfunktionstyp",
            "BU 49 Hauptfunktionsnummer",
            "BU 49 Funktionsergänzung",
            "Zusatzinformation - Art 1",
            "Zusatzinformation - Inhalt 1",
            "Zusatzinformation - Art 2",
            "Zusatzinformation - Inhalt 2",
            "Zusatzinformation - Art 3",
            "Zusatzinformation - Inhalt 3",
            "Zusatzinformation - Art 4",
            "Zusatzinformation - Inhalt 4",
            "Zusatzinformation - Art 5",
            "Zusatzinformation - Inhalt 5",
            "Zusatzinformation - Art 6",
            "Zusatzinformation - Inhalt 6",
            "Zusatzinformation - Art 7",
            "Zusatzinformation - Inhalt 7",
            "Zusatzinformation - Art 8",
            "Zusatzinformation - Inhalt 8",
            "Zusatzinformation - Art 9",
            "Zusatzinformation - Inhalt 9",
            "Zusatzinformation - Art 10",
            "Zusatzinformation - Inhalt 10",
            "Zusatzinformation - Art 11",
            "Zusatzinformation - Inhalt 11",
            "Zusatzinformation - Art 12",
            "Zusatzinformation - Inhalt 12",
            "Zusatzinformation - Art 13",
            "Zusatzinformation - Inhalt 13",
            "Zusatzinformation - Art 14",
            "Zusatzinformation - Inhalt 14",
            "Zusatzinformation - Art 15",
            "Zusatzinformation - Inhalt 15",
            "Zusatzinformation - Art 16",
            "Zusatzinformation - Inhalt 16",
            "Zusatzinformation - Art 17",
            "Zusatzinformation - Inhalt 17",
            "Zusatzinformation - Art 18",
            "Zusatzinformation - Inhalt 18",
            "Zusatzinformation - Art 19",
            "Zusatzinformation - Inhalt 19",
            "Zusatzinformation - Art 20",
            "Zusatzinformation - Inhalt 20",
            "Stück",
            "Gewicht",
            "Zahlweise",
            "Forderungsart",
            "Veranlagungsjahr",
            "Zugeordnete Fälligkeit",
            "Skontotyp",
            "Auftragsnummer",
            "Buchungstyp",
            "USt-Schlüssel (Anzahlungen)",
            "EU-Land (Anzahlungen)",
            "Sachverhalt L+L (Anzahlungen)",
            "EU-Steuersatz (Anzahlungen)",
            "Erlöskonto (Anzahlungen)",
            "Herkunft-Kz",
            "Buchungs-GUID",
            "KOST-Datum",
            "SEPA-Mandatsreferenz",
            "Skontosperre",
            "Gesellschaftername",
            "Beteiligtennummer",
            "Identifikationsnummer",
            "Zeichnernummer",
            "Postensperre bis",
            "Bezeichnung SoBil-Sachverhalt",
            "Kennzeichen SoBil-Buchung",
            "Festschreibung",
            "Leistungsdatum",
            "Datum Zuord. Steuerperiode"
        ]
        writer.writerow(header_line2)
        
        # Buchungszeilen
        for buchung in buchungen:
            betrag = abs(Decimal(str(buchung.get('betrag', 0))))
            
            # Soll/Haben bestimmen
            # Bei DATEV: S = Soll, H = Haben
            soll_haben = "S"  # Default
            if betrag < 0:
                soll_haben = "H"
                betrag = abs(betrag)
            
            # Datum formatieren (DDMM)
            buchungsdatum = buchung.get('buchungsdatum', datetime.now())
            if isinstance(buchungsdatum, str):
                buchungsdatum = datetime.strptime(buchungsdatum, "%Y-%m-%d")
            datum_ddmm = buchungsdatum.strftime("%d%m")
            
            buchungszeile = [
                f"{betrag:.2f}".replace('.', ','),  # Umsatz
                soll_haben,                          # Soll/Haben
                "EUR",                               # Währung
                "",                                  # Kurs
                "",                                  # Basis-Umsatz
                "",                                  # Währung Basis
                buchung.get('soll_konto', ''),       # Konto
                buchung.get('haben_konto', ''),      # Gegenkonto
                buchung.get('steuerschluessel', ''), # BU-Schlüssel
                datum_ddmm,                          # Belegdatum
                buchung.get('belegnummer', '')[:36], # Belegfeld 1 (max 36 Zeichen)
                "",                                  # Belegfeld 2
                "",                                  # Skonto
                buchung.get('buchungstext', '')[:60], # Buchungstext (max 60 Zeichen)
                "",                                  # Postensperre
                "",                                  # Diverse Adressnummer
                "",                                  # Geschäftspartnerbank
                "",                                  # Sachverhalt
                "",                                  # Zinssperre
                "",                                  # Beleglink
            ]
            
            # Fülle restliche Felder mit leeren Werten auf (bis zu 116 Spalten)
            while len(buchungszeile) < 116:
                buchungszeile.append("")
            
            writer.writerow(buchungszeile)
        
        return output.getvalue()
    
    def save_to_file(self, csv_content: str, filename: str = None) -> str:
        """
        Speichert DATEV-Export in Datei
        
        Args:
            csv_content: DATEV-CSV Inhalt
            filename: Dateiname (optional)
        
        Returns:
            Pfad zur gespeicherten Datei
        """
        if filename is None:
            filename = f"DATEV_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', encoding='windows-1252', newline='') as f:
            f.write(csv_content)
        
        return filename


# Beispiel-Verwendung
if __name__ == "__main__":
    # Test-Buchungen
    test_buchungen = [
        {
            "betrag": 1190.00,
            "soll_konto": "8400",
            "haben_konto": "1200",
            "buchungsdatum": "2024-01-15",
            "belegnummer": "RE-2024-001",
            "buchungstext": "Warenverkauf Kunde Müller",
            "steuerschluessel": "9"
        },
        {
            "betrag": -500.50,
            "soll_konto": "1200",
            "haben_konto": "8400",
            "buchungsdatum": "2024-01-20",
            "belegnummer": "GS-2024-001",
            "buchungstext": "Gutschrift Retoure",
            "steuerschluessel": "9"
        }
    ]
    
    exporter = DATEVExporter(mandant_nr="1000", berater_nr="1000")
    csv_output = exporter.export_buchungen(test_buchungen, "01012024", "31012024")
    
    print("DATEV-Export generiert:")
    print(csv_output)
    
    # Datei speichern
    filename = exporter.save_to_file(csv_output)
    print(f"\n✅ Exportiert nach: {filename}")

