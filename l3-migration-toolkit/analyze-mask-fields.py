#!/usr/bin/env python3
"""
L3-Masken Feldanalyse → Mask Builder Schema Generator

Analysiert L3-Screenshots und extrahiert:
1. Feldnamen
2. Feldtypen (Text, Nummer, Dropdown, Checkbox, etc.)
3. Validierungen
4. Layout-Informationen

Generiert JSON-Schema für VALEO-NeuroERP Mask Builder.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Feldtyp-Mapping L3 → VALEO-NeuroERP
FIELD_TYPE_MAPPING = {
    "text": "string",
    "number": "number",
    "dropdown": "select",
    "checkbox": "boolean",
    "date": "date",
    "textarea": "text",
    "lookup": "lookup",  # z.B. Artikel-Nr mit "..." Button
    "currency": "currency",
    "percentage": "percentage",
}

class L3MaskAnalyzer:
    """Analysiert L3-Masken und generiert Mask Builder Schemas"""
    
    def __init__(self, screenshot_dir: str = "screenshots/l3-masks"):
        self.screenshot_dir = Path(screenshot_dir)
        self.masks = []
        self.l3_mapping = self.load_l3_mapping()
    
    def load_l3_mapping(self) -> Dict[str, Any]:
        """Lädt existierendes L3 → VALEO Mapping"""
        mapping_path = Path(__file__).parent.parent / "scripts" / "l3_import_mapping.json"
        
        if mapping_path.exists():
            with open(mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def generate_from_ocr(self, screenshot_path: str, mask_name: str) -> Dict[str, Any]:
        """
        Generiert Mask Builder Schema aus OCR-Analyse (AUTOMATISCH)
        
        Args:
            screenshot_path: Pfad zum Screenshot
            mask_name: Name der L3-Maske
        
        Returns:
            Mask Builder Schema (JSON)
        """
        try:
            from ocr_pipeline import L3MaskOCR
            from llm_field_analyzer import LLMFieldAnalyzer
        except ImportError:
            print("⚠️  OCR-Pipeline nicht verfügbar. Tesseract installiert?")
            print("   Fallback: Manuelle Analyse verwenden")
            return None
        
        print(f"🔍 OCR-Analyse: {mask_name}")
        
        # 1. OCR-Extraktion
        ocr = L3MaskOCR()
        ocr_results = ocr.extract_fields(screenshot_path)
        
        print(f"   ✅ {len(ocr_results['fields'])} Felder erkannt")
        print(f"   📑 {len(ocr_results['tabs'])} Tabs erkannt")
        
        # 2. LLM-Analyse
        analyzer = LLMFieldAnalyzer()
        structured_fields = analyzer.analyze_ocr_with_llm(
            ocr_results['raw_text'],
            ocr_results['fields'],
            context={
                'mask_name': mask_name,
                'existing_mapping': self.l3_mapping
            }
        )
        
        # 3. Schema-Generierung
        schema = self.generate_mask_builder_schema(structured_fields)
        
        # 4. Enrich mit VALEO-Relations
        schema = self.enrich_with_valeo_relations(schema)
        
        return schema
    
    def enrich_with_valeo_relations(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erweitert Schema mit VALEO-NeuroERP Relations
        
        Analysiert existierende Datenbank-Struktur und fügt
        Foreign Keys, Display Fields, etc. hinzu
        """
        # TODO: Query VALEO-DB für existierende Tabellen/Relations
        # Für jetzt: Hardcoded Common Relations
        
        common_relations = {
            'artikel_gruppe_id': {
                'table': 'artikelgruppen',
                'display_field': 'bezeichnung'
            },
            'einheit_id': {
                'table': 'einheiten',
                'display_field': 'kurzbezeichnung'
            },
            'kunde_id': {
                'table': 'kunden',
                'display_field': 'name'
            },
            'lieferant_id': {
                'table': 'lieferanten',
                'display_field': 'name'
            }
        }
        
        # Enrich Relations
        if 'database' in schema and 'relations' not in schema['database']:
            schema['database']['relations'] = []
        
        for field in schema.get('form', {}).get('fields', []):
            field_name = field.get('name', '')
            
            if field_name in common_relations:
                rel = common_relations[field_name]
                schema['database']['relations'].append({
                    'foreign_key': field_name,
                    'table': rel['table'],
                    'display_field': rel['display_field']
                })
        
        return schema
    
    def analyze_artikelstamm(self) -> Dict[str, Any]:
        """
        Manuelle Analyse: Artikelstamm (basierend auf Screenshot)
        """
        return {
            "mask_id": "artikelstamm",
            "mask_name": "Artikel-Stammdaten",
            "l3_original": "Artikel-Stammdaten",
            "valeo_route": "/artikel/stamm",
            "priority": 5,
            "category": "Stammdaten",
            "fields": [
                {
                    "id": "artikel_nr",
                    "label": "Artikel-Nr.",
                    "type": "lookup",
                    "required": True,
                    "validation": "unique",
                    "ui_hint": "with_search_button",
                    "max_length": 20,
                    "database_column": "artikel_nr"
                },
                {
                    "id": "kurztext",
                    "label": "Kurztext",
                    "type": "string",
                    "required": False,
                    "max_length": 50,
                    "database_column": "kurztext"
                },
                {
                    "id": "artikel_gruppe",
                    "label": "Artikel-Gruppe",
                    "type": "lookup",
                    "required": False,
                    "ui_hint": "with_search_button",
                    "database_column": "artikel_gruppe_id"
                },
                {
                    "id": "bezeichnung",
                    "label": "Bezeichnung",
                    "type": "string",
                    "required": True,
                    "max_length": 255,
                    "database_column": "bezeichnung"
                },
                {
                    "id": "beschreibung",
                    "label": "Beschreibung",
                    "type": "text",
                    "required": False,
                    "ui_hint": "multiline",
                    "database_column": "beschreibung"
                },
                {
                    "id": "matchcode_2",
                    "label": "2. Matchcode",
                    "type": "string",
                    "required": False,
                    "max_length": 50,
                    "database_column": "matchcode_2"
                },
                {
                    "id": "artikel_gesperrt",
                    "label": "Artikel gesperrt",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                    "database_column": "gesperrt"
                },
                {
                    "id": "artikel_art",
                    "label": "Artikel-Art",
                    "type": "select",
                    "required": False,
                    "options": [
                        {"value": "standard", "label": "Standard"},
                        {"value": "dienstleistung", "label": "Dienstleistung"},
                        {"value": "verpackung", "label": "Verpackung"}
                    ],
                    "database_column": "artikel_art"
                },
                {
                    "id": "mengen_einheit",
                    "label": "Mengen-Einheit",
                    "type": "lookup",
                    "required": True,
                    "ui_hint": "with_search_button",
                    "database_column": "einheit_id"
                },
                {
                    "id": "gewicht",
                    "label": "Gewicht",
                    "type": "number",
                    "required": False,
                    "unit": "kg",
                    "decimals": 3,
                    "database_column": "gewicht"
                },
                {
                    "id": "hl_gewicht",
                    "label": "hl-Gewicht",
                    "type": "number",
                    "required": False,
                    "unit": "kg",
                    "decimals": 2,
                    "database_column": "hl_gewicht"
                },
                {
                    "id": "steuerschluessel",
                    "label": "Steuerschlüssel",
                    "type": "lookup",
                    "required": True,
                    "ui_hint": "with_search_button",
                    "database_column": "steuerschluessel_id"
                },
                {
                    "id": "steuersatz",
                    "label": "Steuersatz %",
                    "type": "percentage",
                    "required": True,
                    "decimals": 2,
                    "database_column": "steuersatz"
                },
            ],
            "tabs": [
                {
                    "id": "einheiten",
                    "label": "Einheiten",
                    "fields": ["mengen_einheit", "gewicht", "hl_gewicht"]
                },
                {
                    "id": "preise",
                    "label": "Preise",
                    "fields": []  # TODO: Separate Screenshot benötigt
                },
                {
                    "id": "rabatte",
                    "label": "Rabatte",
                    "fields": []  # TODO
                },
                {
                    "id": "saatgut",
                    "label": "Saatgut",
                    "fields": []  # TODO - AGRAR-SPEZIFISCH!
                },
            ],
            "relations": [
                {
                    "table": "artikel_gruppen",
                    "foreign_key": "artikel_gruppe_id",
                    "display_field": "bezeichnung"
                },
                {
                    "table": "einheiten",
                    "foreign_key": "einheit_id",
                    "display_field": "bezeichnung"
                },
            ]
        }
    
    def generate_mask_builder_schema(self, mask_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiert Mask Builder Schema (kompatibel mit FormBuilder)
        """
        schema = {
            "schema_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "source": "L3-Migration",
            "mask": {
                "id": mask_data["mask_id"],
                "name": mask_data["mask_name"],
                "route": mask_data["valeo_route"],
                "category": mask_data["category"],
                "priority": mask_data["priority"],
            },
            "form": {
                "fields": [],
                "validation": {},
                "layout": {
                    "type": "tabs" if mask_data.get("tabs") else "single",
                    "tabs": mask_data.get("tabs", [])
                }
            },
            "database": {
                "table": mask_data["mask_id"].replace("-", "_"),
                "columns": []
            }
        }
        
        # Konvertiere Felder
        for field in mask_data["fields"]:
            # Form-Schema
            form_field = {
                "name": field["id"],
                "label": field["label"],
                "type": field["type"],
                "required": field.get("required", False),
            }
            
            # Optional: Validierung
            if "validation" in field:
                form_field["validation"] = field["validation"]
            
            if "max_length" in field:
                form_field["maxLength"] = field["max_length"]
            
            if "options" in field:
                form_field["options"] = field["options"]
            
            if "ui_hint" in field:
                form_field["uiHint"] = field["ui_hint"]
            
            schema["form"]["fields"].append(form_field)
            
            # Datenbank-Schema
            db_column = {
                "name": field["database_column"],
                "type": self._get_db_type(field["type"]),
                "nullable": not field.get("required", False),
            }
            
            if "max_length" in field:
                db_column["length"] = field["max_length"]
            
            if field.get("validation") == "unique":
                db_column["unique"] = True
            
            schema["database"]["columns"].append(db_column)
        
        # Relationen
        if "relations" in mask_data:
            schema["database"]["relations"] = mask_data["relations"]
        
        return schema
    
    def _get_db_type(self, field_type: str) -> str:
        """Konvertiert Feldtyp zu Datenbank-Typ"""
        mapping = {
            "string": "VARCHAR",
            "text": "TEXT",
            "number": "DECIMAL",
            "boolean": "BOOLEAN",
            "date": "DATE",
            "lookup": "INTEGER",  # Foreign Key
            "select": "VARCHAR",
            "currency": "DECIMAL",
            "percentage": "DECIMAL",
        }
        return mapping.get(field_type, "VARCHAR")
    
    def export_to_json(self, mask_data: Dict[str, Any], output_path: str):
        """Exportiert Mask Builder Schema als JSON"""
        schema = self.generate_mask_builder_schema(mask_data)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Mask Builder Schema exportiert: {output_file}")
        return schema
    
    def export_to_sql(self, mask_data: Dict[str, Any], output_path: str):
        """Generiert CREATE TABLE SQL"""
        table_name = mask_data["mask_id"].replace("-", "_")
        
        sql_lines = [
            f"-- L3-Migration: {mask_data['mask_name']}",
            f"CREATE TABLE IF NOT EXISTS {table_name} (",
            "    id SERIAL PRIMARY KEY,",
        ]
        
        for field in mask_data["fields"]:
            col_name = field["database_column"]
            col_type = self._get_db_type(field["type"])
            
            if col_type == "VARCHAR" and "max_length" in field:
                col_type = f"VARCHAR({field['max_length']})"
            elif col_type == "DECIMAL":
                decimals = field.get("decimals", 2)
                col_type = f"DECIMAL(12, {decimals})"
            
            nullable = "NOT NULL" if field.get("required") else "NULL"
            unique = "UNIQUE" if field.get("validation") == "unique" else ""
            
            sql_lines.append(f"    {col_name} {col_type} {nullable} {unique},")
        
        sql_lines.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,")
        sql_lines.append("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        sql_lines.append(");")
        sql_lines.append("")
        
        # Indizes
        if mask_data.get("relations"):
            for rel in mask_data["relations"]:
                fk = rel["foreign_key"]
                sql_lines.append(f"CREATE INDEX idx_{table_name}_{fk} ON {table_name}({fk});")
        
        sql = "\n".join(sql_lines)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql)
        
        print(f"✅ SQL Schema exportiert: {output_file}")
        return sql


def main():
    """Hauptprogramm"""
    print("🔍 L3-Masken Analyse → Mask Builder Schema Generator\n")
    
    analyzer = L3MaskAnalyzer()
    
    # Analysiere Artikelstamm (manuell aus Screenshot extrahiert)
    print("📊 Analysiere: Artikelstamm")
    artikelstamm = analyzer.analyze_artikelstamm()
    
    # Exportiere JSON Schema
    print("\n📝 Generiere Mask Builder Schema...")
    analyzer.export_to_json(
        artikelstamm,
        "schemas/mask-builder/artikelstamm.json"
    )
    
    # Exportiere SQL Schema
    print("📝 Generiere SQL Schema...")
    analyzer.export_to_sql(
        artikelstamm,
        "schemas/sql/artikelstamm.sql"
    )
    
    print("\n✅ Fertig!")
    print("\n📋 Nächste Schritte:")
    print("   1. Weitere L3-Masken screenshotten")
    print("   2. Feldlisten manuell/automatisch extrahieren")
    print("   3. Schemas generieren")
    print("   4. In Mask Builder importieren")
    print("   5. Frontend-Masken automatisch generieren lassen")


if __name__ == "__main__":
    main()

