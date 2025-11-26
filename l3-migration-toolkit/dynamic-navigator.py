#!/usr/bin/env python3
"""
Dynamischer L3-Navigator mit prozentualen Koordinaten

Nutzt CSV mit relativen Koordinaten (%) für fenstergrößen-unabhängige Navigation.
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple


class DynamicNavigator:
    """Navigator mit dynamischen, prozentualen Koordinaten"""
    
    def __init__(self, csv_path: str = None):
        """
        Args:
            csv_path: Pfad zur GUI-Map CSV
        """
        if csv_path is None:
            # Suche CSV im aktuellen Verzeichnis
            local_csv = Path(__file__).parent / "l3_gui_map.csv"
            if local_csv.exists():
                csv_path = str(local_csv)
            else:
                csv_path = r"C:\Users\Jochen\Downloads\L3_GUI_Map__percent_coordinates_.csv"
        
        self.gui_map = self._load_gui_map(csv_path)
        total_elements = sum(len(v) for v in self.gui_map.values())
        print(f"✅ GUI-Map geladen: {total_elements} Elemente")
    
    def _load_gui_map(self, csv_path: str) -> Dict[str, Dict]:
        """Lädt GUI-Map aus CSV"""
        gui_map = {}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name']
                gui_map[name] = {
                    'group': row['group'],
                    'x_pct': float(row['x_pct']),
                    'y_pct': float(row['y_pct']),
                    'submenu_y_pct': float(row['submenu_y_pct']) if row['submenu_y_pct'] else None
                }
        
        return gui_map
    
    def get_absolute_coordinates(
        self, 
        element_name: str, 
        canvas_width: int, 
        canvas_height: int
    ) -> Tuple[int, int]:
        """
        Berechnet absolute Koordinaten aus Prozent-Werten
        
        Args:
            element_name: Name des Elements (z.B. "Kunden", "ERFASSUNG")
            canvas_width: Aktuelle Canvas-Breite in Pixel
            canvas_height: Aktuelle Canvas-Höhe in Pixel
        
        Returns:
            (x, y) in absoluten Pixeln
        """
        if element_name not in self.gui_map:
            raise ValueError(f"Element '{element_name}' nicht in GUI-Map gefunden")
        
        elem = self.gui_map[element_name]
        
        x = int((elem['x_pct'] / 100) * canvas_width)
        y = int((elem['y_pct'] / 100) * canvas_height)
        
        return (x, y)
    
    def generate_playwright_click_code(
        self, 
        element_name: str,
        wait_seconds: int = 2
    ) -> str:
        """
        Generiert Playwright JavaScript-Code für dynamischen Klick
        
        Returns:
            JavaScript-Code für browser_evaluate
        """
        if element_name not in self.gui_map:
            return f"// ERROR: '{element_name}' nicht gefunden"
        
        elem = self.gui_map[element_name]
        
        code = f"""() => {{
  const canvas = document.querySelector('canvas');
  const rect = canvas.getBoundingClientRect();
  
  // {element_name}: {elem['x_pct']}% × {elem['y_pct']}%
  const x = rect.left + (rect.width * {elem['x_pct'] / 100});
  const y = rect.top + (rect.height * {elem['y_pct'] / 100});
  
  const clickEvent = new MouseEvent('click', {{
    view: window,
    bubbles: true,
    cancelable: true,
    clientX: x,
    clientY: y
  }});
  
  canvas.dispatchEvent(clickEvent);
  
  return {{ success: true, element: '{element_name}', coords: {{ x: x, y: y }} }};
}}"""
        
        return code
    
    def list_elements(self, group: str = None) -> List[str]:
        """Listet alle verfügbaren Elemente auf"""
        if group:
            return [name for name, elem in self.gui_map.items() if elem['group'] == group]
        return list(self.gui_map.keys())


# L3-Masken Navigation mit prozentualen Koordinaten
L3_MASKS_DYNAMIC = [
    {
        "id": "kundenstamm",
        "name": "Kundenstamm",
        "clicks": ["Kunden"],  # Element-Namen aus CSV
        "wait": 3
    },
    {
        "id": "lieferantenstamm",
        "name": "Lieferantenstamm",
        "clicks": ["Lieferanten"],
        "wait": 3
    },
    {
        "id": "crm",
        "name": "CRM Dashboard",
        "clicks": ["CRM"],
        "wait": 3
    },
    {
        "id": "kalender",
        "name": "Kalender",
        "clicks": ["Kalender"],
        "wait": 2
    },
    {
        "id": "erfassung_menu",
        "name": "Erfassung-Menü",
        "clicks": ["ERFASSUNG"],
        "wait": 1
    }
]


def main():
    """Test & Beispiel"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dynamischer L3-Navigator')
    parser.add_argument('--list', action='store_true', help='Alle Elemente auflisten')
    parser.add_argument('--list-group', help='Elemente einer Gruppe auflisten')
    parser.add_argument('--generate', help='Playwright-Code für Element generieren')
    
    args = parser.parse_args()
    
    nav = DynamicNavigator()
    
    if args.list:
        print("📋 Alle verfügbaren UI-Elemente:\n")
        for group in ['tabs', 'ribbon']:
            elements = nav.list_elements(group)
            print(f"  {group.upper()}:")
            for elem in elements:
                coords = nav.gui_map[elem]
                print(f"    - {elem:25s} ({coords['x_pct']:5.1f}%, {coords['y_pct']:5.1f}%)")
            print()
    
    elif args.list_group:
        elements = nav.list_elements(args.list_group)
        print(f"📋 {args.list_group.upper()}-Elemente:\n")
        for elem in elements:
            print(f"  - {elem}")
    
    elif args.generate:
        code = nav.generate_playwright_click_code(args.generate)
        print("📝 Playwright JavaScript-Code:\n")
        print(code)
        print("\n✅ Kopieren Sie diesen Code in browser_evaluate()")
    
    else:
        # Beispiel: Koordinaten für 1920x1024 Canvas
        print("📊 Beispiel-Koordinaten für 1920×1024 Canvas:\n")
        for elem_name in ['Kunden', 'ERFASSUNG', 'LAGER']:
            if elem_name in nav.gui_map:
                x, y = nav.get_absolute_coordinates(elem_name, 1920, 1024)
                print(f"  {elem_name:20s} → ({x:4d}, {y:4d})")


if __name__ == '__main__':
    main()

