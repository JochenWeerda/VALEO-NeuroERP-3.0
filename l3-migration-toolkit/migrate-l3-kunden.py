#!/usr/bin/env python3
"""
Migration-Script für L3 → VALEO Kundenstamm-Daten
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class L3ToValeoMigrator:
    """Migriert L3-Daten zu VALEO-NeuroERP"""
    
    def __init__(self, mappings_dir: str = "schemas/mappings"):
        self.mappings_dir = Path(mappings_dir)
        self.main_mapping = self.load_mapping("l3-to-valeo-kundenstamm-extended.json")
        self.subtable_mappings = self.load_mapping("subtable-mappings.json")
        
    def load_mapping(self, filename: str) -> Dict:
        """Lädt Mapping-Datei"""
        mapping_file = self.mappings_dir / filename
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def transform_value(self, value: Any, mapping: Dict) -> Any:
        """Transformiert einen Wert gemäß Mapping"""
        
        if value is None or value == '':
            return mapping.get('default', None)
        
        transformation = mapping.get('transformation', '')
        
        if transformation == 'uppercase':
            return str(value).upper()
        elif transformation == 'lowercase':
            return str(value).lower()
        elif transformation == 'trim':
            return str(value).strip()
        elif transformation == 'phone_format':
            # Entferne Leerzeichen und normalisiere
            return str(value).replace(' ', '').replace('-', '').replace('/', '')
        
        return value
    
    def validate_value(self, value: Any, mapping: Dict) -> bool:
        """Validiert einen Wert"""
        
        field_type = mapping.get('type', 'string')
        
        if field_type == 'email':
            return '@' in str(value)
        elif field_type == 'iban':
            # Einfache IBAN-Validierung
            return len(str(value)) >= 15 and len(str(value)) <= 34
        
        return True
    
    def migrate_main_table(self, l3_data: List[Dict]) -> List[Dict]:
        """Migriert Haupttabelle"""
        
        valeo_data = []
        
        for l3_record in l3_data:
            valeo_record = {}
            
            for field_mapping in self.main_mapping['masks'][0]['fields']:
                l3_field = field_mapping['l3_field']
                valeo_field = field_mapping['valeo_field']
                
                # Hole Wert aus L3-Daten
                value = l3_record.get(l3_field)
                
                # Transformiere Wert
                transformed_value = self.transform_value(value, field_mapping)
                
                # Validiere Wert
                if transformed_value is not None and not self.validate_value(transformed_value, field_mapping):
                    print(f"⚠️  Validierungsfehler: {l3_field} = {value}")
                    continue
                
                valeo_record[valeo_field] = transformed_value
            
            valeo_data.append(valeo_record)
        
        return valeo_data
    
    def migrate_subtable(self, subtable_name: str, l3_data: List[Dict]) -> List[Dict]:
        """Migriert Untertabelle"""
        
        if subtable_name not in self.subtable_mappings:
            return []
        
        subtable_mapping = self.subtable_mappings[subtable_name]
        valeo_data = []
        
        for l3_record in l3_data:
            valeo_record = {}
            
            for field_mapping in subtable_mapping['fields']:
                l3_field = field_mapping['l3_field']
                valeo_field = field_mapping['valeo_field']
                
                value = l3_record.get(l3_field)
                transformed_value = self.transform_value(value, field_mapping)
                
                if transformed_value is not None:
                    valeo_record[valeo_field] = transformed_value
            
            if valeo_record:
                valeo_data.append(valeo_record)
        
        return valeo_data
    
    def export_to_csv(self, data: List[Dict], output_file: str):
        """Exportiert Daten zu CSV"""
        
        if not data:
            print(f"⚠️  Keine Daten für {output_file}")
            return
        
        fieldnames = data[0].keys()
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ CSV exportiert: {output_file} ({len(data)} Zeilen)")
    
    def export_to_sql(self, data: List[Dict], table_name: str, output_file: str):
        """Exportiert Daten zu SQL INSERT-Statements"""
        
        if not data:
            print(f"⚠️  Keine Daten für {table_name}")
            return
        
        sql_statements = []
        
        for record in data:
            columns = ', '.join(record.keys())
            values = ', '.join([
                f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" if isinstance(v, str) 
                else ('NULL' if v is None else str(v))
                for v in record.values()
            ])
            
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            sql_statements.append(sql)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Migration: {table_name}\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Records: {len(sql_statements)}\n\n")
            f.write('\n'.join(sql_statements))
        
        print(f"✅ SQL exportiert: {output_file} ({len(sql_statements)} Statements)")

def main():
    """Hauptfunktion"""
    
    print("=" * 80)
    print("L3 → VALEO MIGRATION-SCRIPT")
    print("=" * 80)
    
    migrator = L3ToValeoMigrator()
    
    # Beispiel: Lade L3-Daten (CSV)
    l3_csv_file = "l3-export/kunden.csv"
    
    if not Path(l3_csv_file).exists():
        print(f"\n⚠️  L3-Daten nicht gefunden: {l3_csv_file}")
        print("📝 Erstelle Beispiel-CSV für Tests...")
        
        # Erstelle Beispiel-CSV
        Path("l3-export").mkdir(exist_ok=True)
        example_data = [
            {
                "Kunden-Nr.": "K001",
                "Name 1:": "Musterfirma GmbH",
                "Name 2:": "IT-Abteilung",
                "Straße:": "Hauptstraße 1",
                "PLZ:": "12345",
                "Ort:": "Musterstadt",
                "Tel:": "+49 123 456789",
                "E-Mail:": "info@musterfirma.de",
                "Kontonutzung für Rechnung": "Ja",
                "Kontoauszug gewünscht": "Ja",
                "Direktes Konto": "Nein",
                "Selbstabholer-Rabatt": "5",
                "Zahlungsbedingungen (Tage / Skonto / netto Kasse)": "30",
                "Skonto": "2",
                "Währung": "EUR",
                "Webshop-Kunde ja/nein": "Ja"
            }
        ]
        
        migrator.export_to_csv(example_data, l3_csv_file)
    
    # Lade L3-Daten
    print(f"\n📂 Lade L3-Daten aus: {l3_csv_file}")
    
    l3_data = []
    with open(l3_csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        l3_data = list(reader)
    
    print(f"✅ {len(l3_data)} Datensätze geladen")
    
    # Migriere Haupttabelle
    print("\n🔄 Migriere Haupttabelle: kunden")
    valeo_kunden = migrator.migrate_main_table(l3_data)
    
    # Exportiere Ergebnisse
    output_dir = Path("migration-output")
    output_dir.mkdir(exist_ok=True)
    
    migrator.export_to_csv(valeo_kunden, output_dir / "kunden.csv")
    migrator.export_to_sql(valeo_kunden, "kunden", output_dir / "kunden.sql")
    
    # Migriere Untertabellen (Beispiel)
    print("\n🔄 Migriere Untertabellen...")
    
    for subtable_name in migrator.subtable_mappings.keys():
        print(f"   • {subtable_name}")
        # Hier würde die L3-Untertabellen-Daten geladen werden
        # Für jetzt: Überspringe
        
    print("\n" + "=" * 80)
    print("✅ MIGRATION ABGESCHLOSSEN")
    print("=" * 80)
    print(f"\n📁 Output-Verzeichnis: {output_dir}")
    print(f"📄 CSV-Dateien: kunden.csv")
    print(f"📄 SQL-Dateien: kunden.sql")
    print(f"\n🎯 Nächste Schritte:")
    print(f"   1. Überprüfe Output-Dateien")
    print(f"   2. Importiere SQL in PostgreSQL")
    print(f"   3. Validiere Daten")

if __name__ == "__main__":
    main()

