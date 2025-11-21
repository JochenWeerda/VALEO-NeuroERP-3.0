#!/usr/bin/env python3
"""
LLM-basierte L3-Feldanalyse

Nutzt LLM (Claude/GPT) um OCR-Ergebnisse in strukturierte Felddefinitionen
zu konvertieren, inkl. Typenerkennung, Validierung und Mapping.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class LLMFieldAnalyzer:
    """LLM-basierte Analyse von OCR-extrahierten L3-Feldern"""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        Args:
            model: LLM-Modell (claude/gpt)
        """
        self.model = model
        self.existing_mapping = self._load_l3_mapping()
    
    def _load_l3_mapping(self) -> Dict[str, Any]:
        """Lädt existierendes L3 → VALEO Mapping"""
        mapping_path = Path(__file__).parent.parent / "scripts" / "l3_import_mapping.json"
        
        if mapping_path.exists():
            with open(mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def analyze_ocr_with_llm(
        self, 
        ocr_text: str, 
        ocr_fields: List[Dict],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analysiert OCR-Ergebnisse mit LLM
        
        Args:
            ocr_text: Raw OCR-Text
            ocr_fields: Strukturierte Felder aus OCR
            context: Zusatzinformationen (mask_name, etc.)
        
        Returns:
            Strukturierte Felddefinition für Mask Builder
        """
        mask_name = context.get('mask_name', 'Unknown')
        
        prompt = self._build_analysis_prompt(
            ocr_text, ocr_fields, mask_name
        )
        
        # LLM-Call (hier: Simulated für Entwicklung)
        # In Produktion: OpenAI/Anthropic API
        response = self._call_llm(prompt)
        
        # Parse LLM-Response
        try:
            analyzed_fields = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: Extrahiere JSON aus Markdown-Code-Block
            analyzed_fields = self._extract_json_from_markdown(response)
        
        # Enrich mit Mapping-Kontext
        analyzed_fields = self._enrich_with_mapping(analyzed_fields, mask_name)
        
        return analyzed_fields
    
    def _build_analysis_prompt(
        self, 
        ocr_text: str, 
        ocr_fields: List[Dict],
        mask_name: str
    ) -> str:
        """Baut strukturierten Analyse-Prompt"""
        
        # Finde relevantes Mapping
        relevant_mapping = self._find_relevant_mapping(mask_name)
        
        prompt = f"""Analyze this OCR text from L3 ERP mask '{mask_name}'.

**Task:** Extract ALL form fields with complete metadata for VALEO-NeuroERP Mask Builder.

**OCR Raw Text:**
```
{ocr_text[:2000]}  # Limit für Token-Effizienz
```

**OCR-erkannte Felder (Vorschlag):**
```json
{json.dumps(ocr_fields[:20], indent=2, ensure_ascii=False)}
```

**Existing VALEO mapping context (for reference):**
```json
{json.dumps(relevant_mapping, indent=2, ensure_ascii=False)}
```

**Required Output Format:**
```json
{{
  "mask_id": "{mask_name.lower().replace(' ', '_')}",
  "mask_name": "{mask_name}",
  "fields": [
    {{
      "id": "field_id_snake_case",
      "label": "Feldname (Deutsch)",
      "label_en": "Field Name (English)",
      "type": "string|number|boolean|date|select|lookup|text|currency|percentage",
      "required": true|false,
      "default": null,
      "max_length": 50,
      "decimals": 2,
      "validation": "unique|email|url|...",
      "ui_hint": "with_search_button|multiline|readonly|...",
      "database_column": "column_name",
      "l3_original_field": "Original L3 Feldname",
      "options": [
        {{"value": "val", "label": "Label"}}
      ],
      "tab": "tab_name",
      "position": {{
        "row": 1,
        "col": 1
      }}
    }}
  ],
  "tabs": [
    {{
      "id": "tab_id",
      "label": "Tab-Name",
      "fields": ["field_id1", "field_id2"]
    }}
  ],
  "relations": [
    {{
      "table": "related_table",
      "foreign_key": "field_id",
      "display_field": "bezeichnung"
    }}
  ]
}}
```

**Important Rules:**
1. Use German labels from L3, but add English `label_en` for i18n
2. Map to existing VALEO columns when possible (use `database_column`)
3. Detect field types from context (e.g., "Nr." → lookup, "Preis" → currency)
4. Mark primary keys as `required: true, validation: "unique"`
5. Detect relations (e.g., "Artikel-Gruppe" → foreign key to artikelgruppen table)
6. Group fields by tabs if visible in OCR
7. Preserve ALL fields from OCR, don't skip any

**Output only valid JSON, no markdown, no explanations.**
"""
        return prompt
    
    def _find_relevant_mapping(self, mask_name: str) -> Dict[str, Any]:
        """Findet relevantes Mapping für Maske"""
        mask_lower = mask_name.lower()
        
        # Mapping-Logik
        relevant = {}
        
        for table_name, mapping in self.existing_mapping.items():
            # Fuzzy-Match: Artikelstamm → ARTIKEL
            if any(keyword in mask_lower for keyword in ['artikel', 'product']):
                if 'artikel' in table_name.lower():
                    relevant[table_name] = mapping
            elif any(keyword in mask_lower for keyword in ['kunde', 'customer']):
                if 'adress' in table_name.lower():  # L3: ADRESSEN
                    relevant[table_name] = mapping
        
        return relevant
    
    def _call_llm(self, prompt: str) -> str:
        """
        Ruft LLM auf (Placeholder für echte API-Integration)
        
        In Produktion:
        - OpenAI API (gpt-4)
        - Anthropic API (claude-3.5-sonnet)
        - Lokales LLM (Ollama)
        """
        # TODO: Echte LLM-Integration
        # Für jetzt: Return Placeholder
        
        print("⚠️  LLM-Call simuliert (keine echte API-Integration)")
        print("📝 In Produktion: OpenAI/Anthropic API aufrufen")
        
        # Placeholder-Response (würde von LLM kommen)
        return json.dumps({
            "mask_id": "placeholder",
            "mask_name": "Placeholder",
            "fields": [],
            "tabs": [],
            "relations": []
        }, indent=2)
    
    def _extract_json_from_markdown(self, text: str) -> Dict[str, Any]:
        """Extrahiert JSON aus Markdown-Code-Block"""
        import re
        
        # Finde JSON-Block
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            return json.loads(match.group(1))
        
        # Fallback: Versuche direktes Parsing
        return json.loads(text)
    
    def _enrich_with_mapping(
        self, 
        analyzed_fields: Dict[str, Any],
        mask_name: str
    ) -> Dict[str, Any]:
        """
        Enriched mit existierendem L3→VALEO Mapping
        
        Fügt hinzu:
        - Korrekte database_column Namen
        - Relations
        - Validierungen
        """
        # Finde Mapping für diese Maske
        relevant_mapping = self._find_relevant_mapping(mask_name)
        
        if not relevant_mapping:
            return analyzed_fields
        
        # Enrich Fields
        for field in analyzed_fields.get('fields', []):
            l3_field = field.get('l3_original_field', '')
            
            # Suche Mapping
            for table_name, table_mapping in relevant_mapping.items():
                for col_name, col_mapping in table_mapping.items():
                    source_col = col_mapping.get('source_column', '')
                    
                    if source_col and source_col.lower() in l3_field.lower():
                        # Update database_column
                        field['database_column'] = col_mapping['target_column']
                        field['mapped_from_l3'] = True
                        break
        
        return analyzed_fields
    
    def analyze_batch(
        self, 
        ocr_results_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Batch-Analyse mehrerer OCR-Ergebnisse
        
        Args:
            ocr_results_list: Liste von OCR-Ergebnissen
        
        Returns:
            Liste von analysierten Felddefinitionen
        """
        analyzed = []
        
        for ocr_result in ocr_results_list:
            mask_name = ocr_result.get('context', {}).get('mask_name', 'Unknown')
            
            print(f"🔍 Analysiere: {mask_name}")
            
            result = self.analyze_ocr_with_llm(
                ocr_result['raw_text'],
                ocr_result['fields'],
                {'mask_name': mask_name}
            )
            
            analyzed.append(result)
        
        return analyzed


def main():
    """Test-Funktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM-Feldanalyse')
    parser.add_argument('ocr_json', help='Pfad zur OCR-JSON-Datei')
    parser.add_argument('--mask-name', required=True, help='Name der L3-Maske')
    
    args = parser.parse_args()
    
    # Lade OCR-Ergebnisse
    with open(args.ocr_json, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    # Analysiere
    analyzer = LLMFieldAnalyzer()
    result = analyzer.analyze_ocr_with_llm(
        ocr_data['raw_text'],
        ocr_data['fields'],
        {'mask_name': args.mask_name}
    )
    
    # Ausgabe
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Speichere
    output_path = Path(args.ocr_json).with_suffix('.analyzed.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analyse gespeichert: {output_path}")


if __name__ == '__main__':
    main()

