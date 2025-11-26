***REMOVED***!/usr/bin/env python3
"""
Automatischer L3-Navigator

Kombiniert Moondream Vision (UI-Erkennung) mit Playwright Browser MCP (Klicks)
für vollautomatische Navigation durch L3-Masken.
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from moondream_navigator import MoondreamNavigator
    MOONDREAM_AVAILABLE = True
except ImportError:
    MOONDREAM_AVAILABLE = False
    print("⚠️  moondream_navigator.py nicht gefunden")


class L3AutoNavigator:
    """Vollautomatischer Navigator für L3 via Guacamole RDP"""
    
    def __init__(
        self, 
        browser_url: str = "http://localhost:8090/guacamole/***REMOVED***/client/MQBjAHBvc3RncmVzcWw",
        screenshot_dir: str = "screenshots/l3-masks"
    ):
        """
        Args:
            browser_url: Guacamole RDP URL
            screenshot_dir: Verzeichnis für Screenshots
        """
        self.browser_url = browser_url
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        if MOONDREAM_AVAILABLE:
            self.moondream = MoondreamNavigator()
        else:
            self.moondream = None
        
        self.navigation_log = []
    
    def take_screenshot(self, filename: str) -> str:
        """
        Erstellt Screenshot via Playwright Browser MCP
        
        HINWEIS: Muss via Playwright MCP aufgerufen werden,
        da wir keinen direkten Python-Zugriff auf Browser haben.
        
        Returns:
            Pfad zum Screenshot
        """
        screenshot_path = self.screenshot_dir / filename
        
        ***REMOVED*** Placeholder für Playwright MCP Integration
        ***REMOVED*** In der Praxis wird dies über mcp_cursor-playwright_browser_take_screenshot aufgerufen
        print(f"   📸 Screenshot: {filename}")
        
        return str(screenshot_path)
    
    def click_at_coordinates(self, x: int, y: int, element_name: str = "Element"):
        """
        Führt Klick via Playwright Browser MCP aus
        
        Args:
            x, y: Pixel-Koordinaten
            element_name: Name des Elements (für Logging)
        
        HINWEIS: Muss via Playwright MCP browser_evaluate aufgerufen werden
        """
        print(f"   🖱️  Klicke auf '{element_name}' bei ({x}, {y})")
        
        ***REMOVED*** Placeholder für Playwright MCP
        ***REMOVED*** In der Praxis:
        ***REMOVED*** await page.evaluate(f'''
        ***REMOVED***     const canvas = document.querySelector('canvas');
        ***REMOVED***     const rect = canvas.getBoundingClientRect();
        ***REMOVED***     const clickEvent = new MouseEvent('click', {{
        ***REMOVED***         clientX: rect.left + {x},
        ***REMOVED***         clientY: rect.top + {y},
        ***REMOVED***         bubbles: true
        ***REMOVED***     }});
        ***REMOVED***     canvas.dispatchEvent(clickEvent);
        ***REMOVED*** ''')
        
        self.navigation_log.append({
            'action': 'click',
            'element': element_name,
            'coordinates': (x, y),
            'timestamp': datetime.now().isoformat()
        })
    
    def navigate_to_mask(
        self, 
        mask_name: str, 
        navigation_path: List[str]
    ) -> Dict[str, any]:
        """
        Navigiert zu einer L3-Maske
        
        Args:
            mask_name: Name der Ziel-Maske (z.B. "Artikelstamm")
            navigation_path: Pfad zum Navigieren (z.B. ["ERFASSUNG", "Artikel"])
        
        Returns:
            {
                'success': bool,
                'screenshot': str,
                'navigation_log': List[Dict]
            }
        """
        if not MOONDREAM_AVAILABLE:
            print(f"❌ Moondream nicht verfügbar - kann nicht automatisch navigieren")
            return {'success': False, 'screenshot': None, 'navigation_log': []}
        
        print(f"\n🧭 Navigiere zu: {mask_name}")
        print(f"   Pfad: {' → '.join(navigation_path)}")
        
        try:
            ***REMOVED*** Schritt 1: Initial Screenshot
            initial_screenshot = self.take_screenshot(f"nav_{mask_name}_00_start.png")
            time.sleep(1)
            
            ***REMOVED*** Schritt 2: Durch Navigation-Pfad klicken
            for idx, step in enumerate(navigation_path, 1):
                print(f"\n   [{idx}/{len(navigation_path)}] Suche: {step}")
                
                ***REMOVED*** Screenshot des aktuellen Zustands
                current_screenshot = self.take_screenshot(
                    f"nav_{mask_name}_{str(idx).zfill(2)}_{step.replace(' ', '_')}.png"
                )
                
                ***REMOVED*** Moondream: Finde UI-Element
                result = self.moondream.find_menu_item(current_screenshot, step)
                
                if not result['found'] or not result['coordinates']:
                    print(f"   ❌ '{step}' nicht gefunden")
                    print(f"      Moondream: {result['description']}")
                    return {
                        'success': False,
                        'screenshot': current_screenshot,
                        'navigation_log': self.navigation_log,
                        'error': f"Element '{step}' nicht gefunden"
                    }
                
                x, y = result['coordinates']
                print(f"   ✅ Gefunden bei ({x}, {y}) - Confidence: {result['confidence']:.0%}")
                
                ***REMOVED*** Klicke auf Element
                self.click_at_coordinates(x, y, step)
                
                ***REMOVED*** Warte auf Seitenladezeit
                time.sleep(2)
            
            ***REMOVED*** Schritt 3: Final Screenshot der geöffneten Maske
            final_screenshot = self.take_screenshot(f"{mask_name.lower()}_final.png")
            
            ***REMOVED*** Schritt 4: Verifiziere dass Maske geladen ist
            verified = self.moondream.verify_page_loaded(final_screenshot, mask_name)
            
            if verified:
                print(f"   ✅ Maske '{mask_name}' erfolgreich geöffnet!")
            else:
                print(f"   ⚠️  Maske möglicherweise nicht korrekt geladen")
            
            return {
                'success': True,
                'screenshot': final_screenshot,
                'navigation_log': self.navigation_log,
                'verified': verified
            }
        
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return {
                'success': False,
                'screenshot': None,
                'navigation_log': self.navigation_log,
                'error': str(e)
            }
    
    def navigate_to_mask_by_icon(
        self, 
        mask_name: str, 
        icon_description: str
    ) -> Dict[str, any]:
        """
        Navigiert zu Maske via direktem Icon-Klick (z.B. Favoriten-Leiste)
        
        Args:
            mask_name: Name der Maske
            icon_description: Beschreibung des Icons für Moondream
        
        Returns:
            Navigation-Result
        """
        if not MOONDREAM_AVAILABLE:
            return {'success': False, 'screenshot': None}
        
        print(f"\n🧭 Navigiere zu: {mask_name} (via Icon)")
        print(f"   Icon: {icon_description}")
        
        try:
            ***REMOVED*** Screenshot
            screenshot = self.take_screenshot(f"nav_{mask_name}_icon.png")
            time.sleep(1)
            
            ***REMOVED*** Moondream: Finde Icon
            result = self.moondream.find_icon_by_description(screenshot, icon_description)
            
            if not result['found'] or not result['coordinates']:
                print(f"   ❌ Icon nicht gefunden")
                return {'success': False, 'screenshot': screenshot, 'error': 'Icon nicht gefunden'}
            
            x, y = result['coordinates']
            print(f"   ✅ Icon gefunden bei ({x}, {y})")
            
            ***REMOVED*** Klicke auf Icon
            self.click_at_coordinates(x, y, mask_name)
            time.sleep(2)
            
            ***REMOVED*** Final Screenshot
            final_screenshot = self.take_screenshot(f"{mask_name.lower()}_final.png")
            
            return {
                'success': True,
                'screenshot': final_screenshot,
                'navigation_log': self.navigation_log
            }
        
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return {'success': False, 'screenshot': None, 'error': str(e)}
    
    def save_navigation_log(self, output_path: str):
        """Speichert Navigation-Log als JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.navigation_log, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Navigation-Log gespeichert: {output_path}")


***REMOVED*** L3-Masken Navigation-Mapping
L3_NAVIGATION_MAP = {
    "artikelstamm": {
        "name": "Artikelstamm",
        "method": "icon",
        "icon_description": "article or product master data icon in the toolbar",
        "alternative_path": ["ERFASSUNG", "Artikel"]
    },
    "kundenstamm": {
        "name": "Kundenstamm",
        "method": "menu",
        "path": ["ERFASSUNG", "Kunden"],
        "alternative_icon": "customer icon"
    },
    "lieferantenstamm": {
        "name": "Lieferantenstamm",
        "method": "menu",
        "path": ["ERFASSUNG", "Lieferanten"]
    },
    "lieferschein": {
        "name": "Lieferschein",
        "method": "icon",
        "icon_description": "delivery note or shipping icon",
        "alternative_path": ["ERFASSUNG", "Lieferschein"]
    },
    "rechnung": {
        "name": "Rechnung",
        "method": "menu",
        "path": ["ABRECHNUNG", "Rechnung"]
    },
    "auftrag": {
        "name": "Auftrag",
        "method": "menu",
        "path": ["ERFASSUNG", "Auftrag"]
    },
    "bestellung": {
        "name": "Bestellung",
        "method": "menu",
        "path": ["ERFASSUNG", "Bestellung"]
    },
    "lager_bestand": {
        "name": "Lager-Bestand",
        "method": "menu",
        "path": ["LAGER", "Bestand"]
    },
    "psm_abgabe": {
        "name": "PSM-Abgabe",
        "method": "menu",
        "path": ["ERFASSUNG", "PSM-Abgabe"]
    }
}


def main():
    """Test-Funktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='L3 Auto-Navigator')
    parser.add_argument('mask_id', help='Masken-ID (z.B. artikelstamm, kundenstamm)')
    
    args = parser.parse_args()
    
    if args.mask_id not in L3_NAVIGATION_MAP:
        print(f"❌ Unbekannte Maske: {args.mask_id}")
        print(f"   Verfügbar: {', '.join(L3_NAVIGATION_MAP.keys())}")
        return
    
    nav = L3AutoNavigator()
    mask_config = L3_NAVIGATION_MAP[args.mask_id]
    
    print(f"🚀 Auto-Navigation zu: {mask_config['name']}")
    
    if mask_config['method'] == 'icon':
        result = nav.navigate_to_mask_by_icon(
            mask_config['name'],
            mask_config['icon_description']
        )
    else:
        result = nav.navigate_to_mask(
            mask_config['name'],
            mask_config['path']
        )
    
    if result['success']:
        print(f"\n✅ Navigation erfolgreich!")
        print(f"   Screenshot: {result['screenshot']}")
    else:
        print(f"\n❌ Navigation fehlgeschlagen")
        if 'error' in result:
            print(f"   Fehler: {result['error']}")
    
    ***REMOVED*** Speichere Log
    nav.save_navigation_log(f"navigation_{args.mask_id}.json")


if __name__ == '__main__':
    main()

