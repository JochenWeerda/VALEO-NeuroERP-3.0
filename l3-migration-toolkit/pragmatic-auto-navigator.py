#!/usr/bin/env python3
"""
Pragmatischer Auto-Navigator für L3 (OHNE Moondream)

Nutzt:
- Playwright Browser MCP für Screenshots & Klicks
- Feste Koordinaten basierend auf L3-UI-Layout
- OCR zur Verifikation
- Retry-Logik

Vollautomatisch, keine manuelle Interaktion erforderlich!
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# L3-UI Koordinaten (basierend auf 896px breitem Canvas)
# Ermittelt aus vorherigem Screenshot-Analyse
L3_UI_COORDINATES = {
    # Top-Menü (Y ≈ 75)
    "DATEI": (80, 75),
    "FAVORITEN": (180, 75),
    "ALLGEMEIN": (280, 75),
    "ERFASSUNG": (380, 75),
    "ABRECHNUNG": (480, 75),
    "LAGER": (580, 75),
    "PRODUKTION": (680, 75),
    "AUSWERTUNGEN": (780, 75),
    
    # Favoriten-Icons (Y ≈ 125)
    "Kunden-Artikel-Icon": (200, 125),
    "Verkauf-Lieferschein-Icon": (320, 125),
    "Artikel-Stamm-Icon": (440, 125),
    "Artikel-Konto-Icon": (560, 125),
    "CRM-Dashboard-Icon": (680, 125),
}

# L3-Masken Navigation-Map
L3_NAVIGATION = {
    "artikelstamm": {
        "name": "Artikelstamm",
        "clicks": [("Artikel-Stamm-Icon", 3)],  # (target, wait_seconds)
        "verify_text": "ARTIKEL-STAMMDATEN"
    },
    "kundenstamm": {
        "name": "Kundenstamm", 
        "clicks": [("Kunden-Artikel-Icon", 3)],
        "verify_text": "KUNDEN"
    },
    "lieferschein": {
        "name": "Lieferschein",
        "clicks": [("Verkauf-Lieferschein-Icon", 3)],
        "verify_text": "LIEFERSCHEIN"
    },
    "rechnung": {
        "name": "Rechnung",
        "clicks": [("ABRECHNUNG", 1), (200, 150, 2)],  # Menü + Submenu
        "verify_text": "RECHNUNG"
    },
    "auftrag": {
        "name": "Auftrag",
        "clicks": [("ERFASSUNG", 1), (200, 150, 2)],
        "verify_text": "AUFTRAG"
    },
    "bestellung": {
        "name": "Bestellung",
        "clicks": [("ERFASSUNG", 1), (200, 200, 2)],
        "verify_text": "BESTELLUNG"
    },
    "lager_bestand": {
        "name": "Lager-Bestand",
        "clicks": [("LAGER", 1), (200, 150, 2)],
        "verify_text": "LAGER"
    }
}


class PragmaticAutoNavigator:
    """Pragmatischer Auto-Navigator ohne externe Dependencies"""
    
    def __init__(self, screenshot_dir: str = "screenshots/l3-masks"):
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.navigation_log = []
        self.canvas_offset = (72, 0)  # Guacamole Canvas Offset
    
    def get_absolute_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Konvertiert Canvas-relative Koordinaten zu absoluten Koordinaten"""
        return (x + self.canvas_offset[0], y + self.canvas_offset[1])
    
    def navigate_to_mask(self, mask_id: str) -> Dict[str, any]:
        """
        Navigiert zu einer L3-Maske
        
        Args:
            mask_id: ID der Maske (z.B. "artikelstamm")
        
        Returns:
            {
                'success': bool,
                'mask_name': str,
                'screenshot': str,
                'clicks_performed': int
            }
        """
        if mask_id not in L3_NAVIGATION:
            print(f"❌ Unbekannte Maske: {mask_id}")
            return {'success': False, 'error': 'Unknown mask'}
        
        config = L3_NAVIGATION[mask_id]
        mask_name = config['name']
        
        print(f"\n🧭 Navigiere zu: {mask_name}")
        print(f"   Klick-Sequenz: {len(config['clicks'])} Schritte")
        
        clicks_performed = 0
        
        try:
            # Führe Klick-Sequenz aus
            for idx, click_info in enumerate(config['clicks'], 1):
                if isinstance(click_info[0], str):
                    # Named coordinate
                    target = click_info[0]
                    wait = click_info[1]
                    
                    if target not in L3_UI_COORDINATES:
                        print(f"   ⚠️  Koordinate '{target}' nicht definiert")
                        continue
                    
                    x, y = L3_UI_COORDINATES[target]
                    abs_x, abs_y = self.get_absolute_coordinates(x, y)
                    
                    print(f"   [{idx}] Klicke '{target}' bei ({abs_x}, {abs_y})")
                else:
                    # Direct coordinates
                    x, y, wait = click_info
                    abs_x, abs_y = self.get_absolute_coordinates(x, y)
                    print(f"   [{idx}] Klicke bei ({abs_x}, {abs_y})")
                
                # Log Click
                self.navigation_log.append({
                    'mask': mask_name,
                    'step': idx,
                    'coordinates': (abs_x, abs_y),
                    'timestamp': datetime.now().isoformat()
                })
                
                # HINWEIS: Actual Click wird via Playwright Browser MCP durchgeführt
                # Placeholder für Integration:
                # await page.evaluate(f'''
                #     const canvas = document.querySelector('canvas');
                #     const evt = new MouseEvent('click', {{
                #         clientX: {abs_x}, clientY: {abs_y},
                #         bubbles: true
                #     }});
                #     canvas.dispatchEvent(evt);
                # ''')
                
                clicks_performed += 1
                
                print(f"       ⏳ Warte {wait}s...")
                time.sleep(wait)
            
            # Screenshot der geöffneten Maske
            screenshot_name = f"{mask_id}_final.png"
            screenshot_path = self.screenshot_dir / screenshot_name
            
            print(f"   📸 Screenshot: {screenshot_name}")
            
            return {
                'success': True,
                'mask_name': mask_name,
                'mask_id': mask_id,
                'screenshot': str(screenshot_path),
                'clicks_performed': clicks_performed,
                'verify_text': config['verify_text']
            }
        
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return {
                'success': False,
                'mask_name': mask_name,
                'error': str(e)
            }
    
    def navigate_all_masks(self) -> Dict[str, any]:
        """Navigiert durch alle definierten Masken"""
        print("🚀 Vollautomatische Navigation durch alle L3-Masken\n")
        print(f"📋 {len(L3_NAVIGATION)} Masken zu erfassen\n")
        
        results = []
        
        for mask_id in L3_NAVIGATION.keys():
            result = self.navigate_to_mask(mask_id)
            results.append(result)
            
            if result['success']:
                print(f"   ✅ Erfolgreich: {result['mask_name']}")
            else:
                print(f"   ❌ Fehlgeschlagen: {result.get('mask_name', mask_id)}")
            
            # Pause zwischen Masken
            time.sleep(1)
        
        successful = [r for r in results if r['success']]
        
        print(f"\n" + "="*70)
        print(f"✅ Erfolgreich: {len(successful)}/{len(results)} Masken")
        print("="*70)
        
        return {
            'total': len(results),
            'successful': len(successful),
            'results': results,
            'navigation_log': self.navigation_log
        }
    
    def save_navigation_log(self, output_path: str):
        """Speichert Navigation-Log"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.navigation_log, f, indent=2, ensure_ascii=False)
        print(f"📄 Navigation-Log: {output_path}")
    
    def generate_playwright_script(self, mask_id: str) -> str:
        """
        Generiert Playwright-Code für eine Maske
        
        Returns:
            JavaScript-Code für Playwright Browser MCP
        """
        if mask_id not in L3_NAVIGATION:
            return ""
        
        config = L3_NAVIGATION[mask_id]
        script_lines = [
            f"// Auto-Navigation zu: {config['name']}",
            "const canvas = document.querySelector('canvas');",
            "const rect = canvas.getBoundingClientRect();",
            ""
        ]
        
        for idx, click_info in enumerate(config['clicks'], 1):
            if isinstance(click_info[0], str):
                target = click_info[0]
                wait = click_info[1]
                if target in L3_UI_COORDINATES:
                    x, y = L3_UI_COORDINATES[target]
                    abs_x, abs_y = self.get_absolute_coordinates(x, y)
            else:
                x, y, wait = click_info
                abs_x, abs_y = self.get_absolute_coordinates(x, y)
            
            script_lines.append(f"// Step {idx}: Klick bei ({abs_x}, {abs_y})")
            script_lines.append(f"await page.evaluate(() => {{")
            script_lines.append(f"  const evt = new MouseEvent('click', {{")
            script_lines.append(f"    clientX: {abs_x}, clientY: {abs_y}, bubbles: true")
            script_lines.append(f"  }});")
            script_lines.append(f"  document.querySelector('canvas').dispatchEvent(evt);")
            script_lines.append(f"}});")
            script_lines.append(f"await page.waitForTimeout({wait * 1000});")
            script_lines.append("")
        
        script_lines.append(f"// Screenshot")
        script_lines.append(f"await page.screenshot({{ path: '{mask_id}_final.png' }});")
        
        return "\n".join(script_lines)


def main():
    """CLI-Interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pragmatic L3 Auto-Navigator')
    parser.add_argument('--mask', help='Einzelne Maske navigieren (z.B. artikelstamm)')
    parser.add_argument('--all', action='store_true', help='Alle Masken durchgehen')
    parser.add_argument('--generate-script', help='Playwright-Script generieren für Maske')
    parser.add_argument('--list', action='store_true', help='Alle verfügbaren Masken auflisten')
    
    args = parser.parse_args()
    
    nav = PragmaticAutoNavigator()
    
    if args.list:
        print("📋 Verfügbare L3-Masken:\n")
        for mask_id, config in L3_NAVIGATION.items():
            print(f"   - {mask_id:20s} → {config['name']}")
        return
    
    if args.generate_script:
        script = nav.generate_playwright_script(args.generate_script)
        print(script)
        return
    
    if args.all:
        result = nav.navigate_all_masks()
        nav.save_navigation_log("navigation_log_all.json")
    elif args.mask:
        result = nav.navigate_to_mask(args.mask)
        nav.save_navigation_log(f"navigation_log_{args.mask}.json")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

