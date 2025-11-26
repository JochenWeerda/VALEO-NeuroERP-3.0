#!/usr/bin/env python3
"""
VALEO-NeuroERP Mask Builder Generator
Generiert neue Masken basierend auf Template und Konfiguration
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class MaskBuilderGenerator:
    """Generiert Mask Builder Schemas"""
    
    def __init__(self, template_path: str = "base-template.json"):
        self.template_path = Path(template_path)
        self.template = self.load_template()
        
    def load_template(self) -> Dict:
        """Lädt Template"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate(self, config: Dict) -> Dict:
        """Generiert neue Maske aus Config"""
        
        mask = self.template.copy()
        
        # Ersetze Platzhalter
        mask['meta']['name'] = config.get('name', 'unnamed-mask')
        mask['meta']['description'] = config.get('description', '')
        mask['resource'] = config.get('resource', '')
        mask['routing']['basePath'] = config.get('basePath', '')
        mask['routing']['param'] = config.get('param', 'id')
        
        # Füge Felder hinzu
        if 'fields' in config:
            mask['views'] = self.create_views(config['fields'])
        
        # Füge Navigation hinzu
        if 'navigation' in config:
            mask['layout']['nav'] = config['navigation']
        
        # Füge Actions hinzu
        if 'actions' in config:
            mask['layout']['header']['actions'] = config['actions']
        
        # Füge Validierung hinzu
        if 'validation' in config:
            mask['validation']['rules'] = config['validation']
        
        # Füge AI-Features hinzu
        if 'aiActions' in config:
            mask['ai']['intentBar']['actions'] = config['aiActions']
        
        # Update Metadata
        mask['meta']['lastModified'] = datetime.now().isoformat()
        
        return mask
    
    def create_views(self, fields: List[Dict]) -> List[Dict]:
        """Erstellt Views aus Feldern"""
        
        views = []
        
        # Gruppiere Felder nach Tabs
        tabs = {}
        for field in fields:
            tab_id = field.get('tab', 'general')
            if tab_id not in tabs:
                tabs[tab_id] = []
            tabs[tab_id].append(field)
        
        # Erstelle View pro Tab
        for tab_id, tab_fields in tabs.items():
            view = {
                "id": tab_id,
                "label": self.capitalize(tab_id),
                "sections": []
            }
            
            # Gruppiere Felder nach Sections
            sections = {}
            for field in tab_fields:
                section_id = field.get('section', 'main')
                if section_id not in sections:
                    sections[section_id] = []
                sections[section_id].append(field)
            
            # Erstelle Sections
            for section_id, section_fields in sections.items():
                section = {
                    "title": self.capitalize(section_id),
                    "grid": 3,
                    "fields": []
                }
                
                for field in section_fields:
                    field_def = self.create_field(field)
                    section['fields'].append(field_def)
                
                view['sections'].append(section)
            
            views.append(view)
        
        return views
    
    def create_field(self, field: Dict) -> Dict:
        """Erstellt Feld-Definition"""
        
        comp = field.get('component', 'Text')
        bind = field.get('bind', field.get('id', ''))
        label = field.get('label', self.capitalize(bind))
        
        field_def = {
            "comp": comp,
            "bind": bind,
            "label": label
        }
        
        # Füge Constraints hinzu
        if field.get('required'):
            field_def['validators'] = ['required']
        
        if field.get('optional'):
            field_def['optional'] = True
        
        if field.get('readonly'):
            field_def['readonly'] = True
        
        # Füge Options hinzu
        if 'options' in field:
            field_def['options'] = field['options']
        
        # Füge AI-Assist hinzu
        if 'aiAssist' in field:
            field_def['aiAssist'] = field['aiAssist']
        
        # Füge AI-Validierung hinzu
        if 'aiValidate' in field:
            field_def['aiValidate'] = field['aiValidate']
        
        return field_def
    
    def capitalize(self, text: str) -> str:
        """Capitalisiert Text"""
        return text.replace('_', ' ').title()
    
    def save(self, mask: Dict, output_path: str):
        """Speichert Maske als JSON"""
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(mask, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Maske gespeichert: {output_path}")

def main():
    """Hauptfunktion"""
    
    print("=" * 80)
    print("VALEO-NeuroERP Mask Builder Generator")
    print("=" * 80)
    
    # Beispiel-Config
    config = {
        "name": "artikelstamm",
        "description": "Artikelstamm für VALEO-NeuroERP",
        "resource": "artikel",
        "basePath": "/lager/artikel-stamm",
        "param": "artikel_nr",
        "fields": [
            {
                "id": "artikel_nr",
                "bind": "artikel_nr",
                "label": "Artikelnummer",
                "component": "Text",
                "tab": "general",
                "section": "identifikation",
                "required": True
            },
            {
                "id": "bezeichnung",
                "bind": "bezeichnung",
                "label": "Bezeichnung",
                "component": "Text",
                "tab": "general",
                "section": "identifikation",
                "required": True
            },
            {
                "id": "beschreibung",
                "bind": "beschreibung",
                "label": "Beschreibung",
                "component": "TextArea",
                "tab": "general",
                "section": "details",
                "optional": True
            }
        ],
        "navigation": [
            { "id": "general", "label": "Allgemein", "icon": "Package" },
            { "id": "pricing", "label": "Preise", "icon": "Euro" },
            { "id": "stock", "label": "Lager", "icon": "Warehouse" }
        ],
        "validation": {
            "artikel_nr": { "required": True, "min": 1 },
            "bezeichnung": { "required": True, "min": 2 }
        }
    }
    
    # Generiere Maske
    generator = MaskBuilderGenerator()
    mask = generator.generate(config)
    
    # Speichere Maske
    output_path = f"generated/{config['name']}.json"
    generator.save(mask, output_path)
    
    print(f"\n📊 Statistiken:")
    print(f"   Felder: {len(config['fields'])}")
    print(f"   Views: {len(mask['views'])}")
    print(f"   Navigation: {len(mask['layout']['nav'])}")
    
    print(f"\n🎯 Nächste Schritte:")
    print(f"   1. Überprüfe generierte Maske")
    print(f"   2. Importiere in VALEO-NeuroERP")
    print(f"   3. Teste Funktionalität")

if __name__ == "__main__":
    main()

