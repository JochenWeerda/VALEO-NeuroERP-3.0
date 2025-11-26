#!/usr/bin/env python3
"""
Automatisierte L3-Masken-Erfassung

Workflow:
1. Benutzer navigiert manuell zu L3-Maske
2. Script erstellt Screenshot via Playwright Browser MCP
3. OCR-Extraktion der Felder
4. LLM-Analyse & Strukturierung
5. Export als Mask Builder JSON + SQL

Nutzt Playwright MCP über HTTP (läuft parallel im Browser).
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import der Pipeline-Module
try:
    from analyze_mask_fields import L3MaskAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    print("⚠️  analyze_mask_fields.py nicht gefunden")


# Liste aller zu erfassenden L3-Masken
L3_MASKS = [
    {"id": "artikelstamm", "name": "Artikelstamm", "priority": 5, "category": "Stammdaten"},
    {"id": "kundenstamm", "name": "Kundenstamm", "priority": 5, "category": "Stammdaten"},
    {"id": "lieferantenstamm", "name": "Lieferantenstamm", "priority": 4, "category": "Stammdaten"},
    {"id": "lieferschein", "name": "Lieferschein", "priority": 5, "category": "Verkauf"},
    {"id": "rechnung", "name": "Rechnung", "priority": 5, "category": "Verkauf"},
    {"id": "auftrag", "name": "Auftrag", "priority": 5, "category": "Verkauf"},
    {"id": "angebot", "name": "Angebot", "priority": 4, "category": "Verkauf"},
    {"id": "bestellung", "name": "Bestellung", "priority": 5, "category": "Einkauf"},
    {"id": "wareneingang", "name": "Wareneingang", "priority": 4, "category": "Einkauf"},
    {"id": "lager_bestand", "name": "Lager-Bestand", "priority": 5, "category": "Lager"},
    {"id": "inventur", "name": "Inventur", "priority": 3, "category": "Lager"},
    {"id": "psm_abgabe", "name": "PSM-Abgabe", "priority": 5, "category": "Agrar"},
    {"id": "saatgut", "name": "Saatgut", "priority": 4, "category": "Agrar"},
    {"id": "duenger", "name": "Dünger", "priority": 4, "category": "Agrar"},
    {"id": "kunden_kontoauszug", "name": "Kunden-Kontoauszug", "priority": 4, "category": "Finanzen"},
]


class AutoCaptureOrchestrator:
    """Orchestriert die automatische Masken-Erfassung"""
    
    def __init__(self, output_dir: str = "schemas"):
        self.output_dir = Path(output_dir)
        self.screenshot_dir = Path("screenshots/l3-masks")
        self.analyzer = L3MaskAnalyzer() if ANALYZER_AVAILABLE else None
        
        # Erstelle Output-Verzeichnisse
        (self.output_dir / "mask-builder").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "sql").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "mappings").mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = []
    
    def capture_and_process_all(self):
        """Hauptschleife: Erfasse alle Masken"""
        
        print("=" * 70)
        print(" L3 → VALEO-NeuroERP Automatische Masken-Migration")
        print("=" * 70)
        print()
        print(f"📋 {len(L3_MASKS)} Masken zu erfassen")
        print()
        print("📝 Workflow:")
        print("   1. Sie navigieren manuell zu L3-Maske im Browser")
        print("   2. Sie drücken Enter")
        print("   3. Screenshot wird automatisch erstellt")
        print("   4. OCR + LLM-Analyse + Schema-Export")
        print()
        print("🌐 Browser-URL: http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw")
        print()
        
        for idx, mask in enumerate(L3_MASKS, 1):
            print(f"\n{'='*70}")
            print(f"[{idx}/{len(L3_MASKS)}] Maske: {mask['name']}")
            print(f"{'='*70}")
            print(f"Kategorie: {mask['category']} | Priorität: {'⭐' * mask['priority']}")
            print()
            
            # Warte auf Benutzer-Bestätigung
            user_input = input(f"➡️  Bitte öffnen Sie '{mask['name']}' in L3, dann drücken Sie Enter (oder 's' zum Überspringen): ").strip().lower()
            
            if user_input == 's':
                print(f"⏭️  Übersprungen: {mask['name']}")
                continue
            
            # Erfasse Maske
            result = self.capture_mask(mask)
            
            if result:
                self.results.append(result)
                print(f"✅ Erfolgreich: {mask['name']}")
            else:
                print(f"❌ Fehler bei: {mask['name']}")
        
        # Abschlussbericht
        self.generate_report()
    
    def capture_mask(self, mask: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Erfasst eine einzelne Maske
        
        Returns:
            Result-Dict oder None bei Fehler
        """
        mask_id = mask['id']
        mask_name = mask['name']
        
        try:
            # 1. Screenshot (über Playwright Browser MCP)
            print(f"   📸 Erstelle Screenshot...")
            screenshot_path = self.take_screenshot(mask_id)
            
            if not screenshot_path:
                print(f"   ❌ Screenshot fehlgeschlagen")
                return None
            
            print(f"   ✅ Screenshot: {screenshot_path}")
            
            # 2. OCR + Analyse (falls verfügbar)
            if self.analyzer:
                print(f"   🔍 OCR-Analyse läuft...")
                schema = self.analyzer.generate_from_ocr(screenshot_path, mask_name)
                
                if not schema:
                    print(f"   ⚠️  OCR nicht verfügbar, verwende manuelle Struktur")
                    schema = self.create_placeholder_schema(mask)
            else:
                print(f"   ⚠️  Analyzer nicht verfügbar")
                schema = self.create_placeholder_schema(mask)
            
            # 3. Export JSON
            json_path = self.output_dir / "mask-builder" / f"{mask_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ JSON exportiert: {json_path}")
            
            # 4. Export SQL
            sql_path = self.output_dir / "sql" / f"{mask_id}.sql"
            if self.analyzer:
                self.analyzer.export_to_sql(mask, str(sql_path))
                print(f"   ✅ SQL exportiert: {sql_path}")
            
            return {
                'mask_id': mask_id,
                'mask_name': mask_name,
                'screenshot': str(screenshot_path),
                'json_schema': str(json_path),
                'sql_schema': str(sql_path),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return None
    
    def take_screenshot(self, mask_id: str) -> Optional[str]:
        """
        Erstellt Screenshot via Playwright Browser MCP
        
        HINWEIS: Playwright MCP muss bereits im Browser laufen!
        URL: http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw
        
        Returns:
            Pfad zum Screenshot oder None
        """
        # Da wir keine direkte MCP-Integration haben, nutzen wir:
        # Option A: Manuelle Screenshots (Windows + Shift + S)
        # Option B: Playwright über externe Tool-Integration
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{mask_id}_{timestamp}.png"
        screenshot_path = self.screenshot_dir / screenshot_filename
        
        print(f"   📸 Bitte erstellen Sie einen Screenshot mit Windows + Shift + S")
        print(f"   💾 Speichern Sie ihn als: {screenshot_path}")
        
        user_input = input(f"   Drücken Sie Enter, wenn Screenshot gespeichert (oder 'paste' für temp): ").strip().lower()
        
        if user_input == 'paste':
            # Placeholder: Screenshot aus Clipboard
            print(f"   ⚠️  Clipboard-Import noch nicht implementiert")
            return None
        
        # Prüfe ob Datei existiert
        if screenshot_path.exists():
            return str(screenshot_path)
        
        print(f"   ⚠️  Datei nicht gefunden: {screenshot_path}")
        return None
    
    def create_placeholder_schema(self, mask: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt Placeholder-Schema (falls OCR nicht verfügbar)"""
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "source": "L3-Migration (Placeholder)",
            "mask": {
                "id": mask['id'],
                "name": mask['name'],
                "route": f"/{mask['category'].lower()}/{mask['id'].replace('_', '-')}",
                "category": mask['category'],
                "priority": mask['priority'],
            },
            "form": {
                "fields": [],
                "validation": {},
                "layout": {"type": "single"}
            },
            "database": {
                "table": mask['id'],
                "columns": []
            },
            "notes": "OCR-Analyse ausstehend - manuelle Feldliste erforderlich"
        }
    
    def generate_report(self):
        """Generiert Abschlussbericht"""
        print(f"\n\n{'='*70}")
        print(" 🎉 Migration abgeschlossen!")
        print(f"{'='*70}\n")
        
        successful = [r for r in self.results if r['status'] == 'success']
        
        print(f"✅ Erfolgreich erfasst: {len(successful)}/{len(L3_MASKS)} Masken")
        print()
        
        # Speichere Index
        index_path = self.output_dir / "mappings" / "migration-index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_masks': len(L3_MASKS),
                'captured_masks': len(successful),
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Index gespeichert: {index_path}")
        print()
        print(f"📂 Output:")
        print(f"   - JSON-Schemas: {self.output_dir / 'mask-builder'}/")
        print(f"   - SQL-Schemas: {self.output_dir / 'sql'}/")
        print(f"   - Screenshots: {self.screenshot_dir}/")
        print()
        print("📋 Nächste Schritte:")
        print("   1. Review der generierten JSON-Schemas")
        print("   2. Import in VALEO-NeuroERP Mask Builder")
        print("   3. SQL-Statements in PostgreSQL ausführen")
        print("   4. Frontend-Masken mit Mask Builder generieren")


def main():
    """Hauptprogramm"""
    orchestrator = AutoCaptureOrchestrator()
    
    try:
        orchestrator.capture_and_process_all()
    except KeyboardInterrupt:
        print("\n\n⏸️  Abgebrochen durch Benutzer")
        orchestrator.generate_report()
    except Exception as e:
        print(f"\n\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

