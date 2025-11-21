***REMOVED***!/usr/bin/env python3
"""
Vision-basierte Koordinaten-Erkennung für L3-Icons

Nutzt GPT-4 Vision / Claude Vision um Icons und Buttons zu erkennen
und deren relative Koordinaten zu bestimmen.
"""

import base64
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image


class VisionCoordinateDetector:
    """Erkennt UI-Elemente und deren Koordinaten via Vision Model"""
    
    def __init__(self, model: str = "gpt-4-vision"):
        """
        Args:
            model: Vision Model (gpt-4-vision oder claude-3)
        """
        self.model = model
    
    def encode_image_base64(self, image_path: str) -> str:
        """Kodiert Bild als Base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def detect_all_icons(self, screenshot_path: str) -> List[Dict]:
        """
        Erkennt alle klickbaren Icons/Buttons im Screenshot
        
        Returns:
            Liste von Icons mit Namen und Koordinaten
        """
        img = Image.open(screenshot_path)
        width, height = img.size
        
        ***REMOVED*** Base64-Encoding
        image_b64 = self.encode_image_base64(screenshot_path)
        
        ***REMOVED*** Vision-Prompt
        prompt = f"""Analyze this screenshot of the L3 ERP software (zvoove).

**Task:** Identify ALL clickable icons and buttons in the toolbar/ribbon area.

For EACH icon/button, provide:
1. **Name/Label** (German text below icon)
2. **Relative position** as percentage (x%, y%) from top-left corner
3. **Icon type** (menu_tab, ribbon_icon, button)

**Image dimensions:** {width} x {height} pixels

**Focus on:**
- Top menu tabs: DATEI, FAVORITEN, ALLGEMEIN, ERFASSUNG, etc.
- Ribbon icons: CRM, Kunden, Artikel, Kalender, etc.
- Ignore status bar at bottom

**Output format (JSON only, no explanation):**
```json
[
  {{
    "name": "ERFASSUNG",
    "label": "ERFASSUNG",
    "type": "menu_tab",
    "x_pct": 25.0,
    "y_pct": 6.5,
    "confidence": 0.95
  }},
  {{
    "name": "Kunden",
    "label": "Kunden",
    "type": "ribbon_icon",
    "x_pct": 55.5,
    "y_pct": 10.0,
    "confidence": 0.92
  }}
]
```

Provide ALL visible clickable elements (15-25 expected).
"""
        
        ***REMOVED*** LLM-Call (Simulated - hier würde OpenAI/Anthropic API aufgerufen)
        print("🔍 Vision-Analyse läuft...")
        print(f"   Bild: {width}x{height}px")
        print(f"   Modell: {self.model}")
        print(f"   Prompt-Länge: {len(prompt)} Zeichen")
        
        ***REMOVED*** TODO: Echter API-Call
        ***REMOVED*** response = self._call_vision_api(image_b64, prompt)
        
        ***REMOVED*** Placeholder-Response
        print("\n⚠️  Vision-API nicht konfiguriert - verwende Fallback")
        print("   Bitte konfigurieren Sie OPENAI_API_KEY oder ANTHROPIC_API_KEY")
        
        return []
    
    def _call_vision_api(self, image_b64: str, prompt: str) -> str:
        """
        Ruft Vision-API auf
        
        TODO: Implementieren mit:
        - OpenAI GPT-4 Vision
        - Anthropic Claude 3 Vision
        - Google Gemini Vision
        """
        ***REMOVED*** OpenAI-Beispiel:
        ***REMOVED*** import openai
        ***REMOVED*** response = openai.ChatCompletion.create(
        ***REMOVED***     model="gpt-4-vision-preview",
        ***REMOVED***     messages=[{
        ***REMOVED***         "role": "user",
        ***REMOVED***         "content": [
        ***REMOVED***             {"type": "text", "text": prompt},
        ***REMOVED***             {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
        ***REMOVED***         ]
        ***REMOVED***     }]
        ***REMOVED*** )
        ***REMOVED*** return response.choices[0].message.content
        
        pass
    
    def calibrate_from_screenshot(self, screenshot_path: str, output_csv: str):
        """
        Einmalige Kalibrierung: Screenshot → Koordinaten-CSV
        
        Args:
            screenshot_path: L3-Startseite Screenshot
            output_csv: Output-Pfad für generierte CSV
        """
        print("🎯 Starte Kalibrierung...\n")
        
        ***REMOVED*** Vision-Analyse
        icons = self.detect_all_icons(screenshot_path)
        
        if not icons:
            print("\n❌ Keine Icons erkannt - Vision-API erforderlich!")
            print("\n💡 Alternative: Verwenden Sie die vorhandene CSV:")
            print("   C:\\Users\\Jochen\\Downloads\\L3_GUI_Map__percent_coordinates_.csv")
            return
        
        ***REMOVED*** Generiere CSV
        import csv
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['group', 'name', 'x_pct', 'y_pct', 'submenu_y_pct'])
            writer.writeheader()
            
            for icon in icons:
                group = 'tabs' if icon['type'] == 'menu_tab' else 'ribbon'
                writer.writerow({
                    'group': group,
                    'name': icon['name'],
                    'x_pct': icon['x_pct'],
                    'y_pct': icon['y_pct'],
                    'submenu_y_pct': ''
                })
        
        print(f"\n✅ Kalibrierung gespeichert: {output_csv}")
        print(f"   {len(icons)} Icons erkannt")


def main():
    """CLI-Interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vision-basierte Koordinaten-Erkennung')
    parser.add_argument('screenshot', help='Screenshot der L3-Startseite')
    parser.add_argument('--output', default='l3_gui_map_auto.csv', help='Output-CSV')
    parser.add_argument('--model', default='gpt-4-vision', help='Vision Model')
    
    args = parser.parse_args()
    
    detector = VisionCoordinateDetector(model=args.model)
    detector.calibrate_from_screenshot(args.screenshot, args.output)


if __name__ == '__main__':
    main()

