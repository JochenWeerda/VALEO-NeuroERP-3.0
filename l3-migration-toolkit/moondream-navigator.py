#!/usr/bin/env python3
"""
Moondream-basierter UI-Navigator für L3

Nutzt Moondream Vision Model zur Erkennung von UI-Elementen (Buttons, Icons, Menüs)
und liefert Koordinaten für automatisches Klicken via Playwright.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image

# Versuche Moondream Python API zu importieren
try:
    from moondream import VL
    MOONDREAM_API_AVAILABLE = True
except ImportError:
    try:
        # Fallback: transformers-basiert
        from transformers import AutoModelForCausalLM, AutoTokenizer
        MOONDREAM_API_AVAILABLE = "transformers"
    except ImportError:
        MOONDREAM_API_AVAILABLE = False


class MoondreamNavigator:
    """UI-Element-Erkennung mit Moondream Vision Model"""
    
    def __init__(self):
        self.moondream_available = self._check_moondream()
        self.model = None
        
        if self.moondream_available:
            self._initialize_model()
    
    def _check_moondream(self) -> bool:
        """Prüft ob Moondream verfügbar ist"""
        return MOONDREAM_API_AVAILABLE != False
    
    def _initialize_model(self):
        """Initialisiert Moondream Model"""
        try:
            if MOONDREAM_API_AVAILABLE == True:
                # Native Moondream API
                self.model = VL()
                print("✅ Moondream Model geladen (Native API)")
            elif MOONDREAM_API_AVAILABLE == "transformers":
                # Transformers-basiert
                model_id = "vikhyatk/moondream2"
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    revision="2024-08-26"
                )
                self.tokenizer = AutoTokenizer.from_pretrained(model_id)
                print("✅ Moondream Model geladen (Transformers)")
        except Exception as e:
            print(f"⚠️  Moondream Model-Loading fehlgeschlagen: {e}")
            self.moondream_available = False
    
    def detect_ui_elements(
        self, 
        screenshot_path: str, 
        query: str,
        return_coordinates: bool = True
    ) -> Dict[str, any]:
        """
        Erkennt UI-Elemente via Moondream
        
        Args:
            screenshot_path: Pfad zum Screenshot
            query: Moondream-Query (z.B. "Find the 'Artikel' menu button")
            return_coordinates: Ob Koordinaten extrahiert werden sollen
        
        Returns:
            {
                'found': bool,
                'description': str,
                'coordinates': (x, y) oder None,
                'confidence': float
            }
        """
        if not self.moondream_available or self.model is None:
            raise RuntimeError(
                "Moondream Model nicht verfügbar. "
                "Installieren Sie: pip install transformers torch pillow"
            )
        
        # Bild laden
        image = Image.open(screenshot_path)
        
        # Moondream Query ausführen
        try:
            if MOONDREAM_API_AVAILABLE == True:
                # Native API
                response = self.model.query(image, query)["answer"]
            elif MOONDREAM_API_AVAILABLE == "transformers":
                # Transformers API
                enc_image = self.model.encode_image(image)
                response = self.model.answer_question(enc_image, query, self.tokenizer)
        except Exception as e:
            return {
                'found': False,
                'description': f'Moondream-Error: {e}',
                'coordinates': None,
                'confidence': 0.0
            }
        
        # Parse Response
        parsed = self._parse_moondream_response(response, return_coordinates)
        
        return parsed
    
    def _parse_moondream_response(
        self, 
        response: str, 
        extract_coords: bool
    ) -> Dict[str, any]:
        """
        Parst Moondream-Response
        
        Moondream gibt typischerweise Text zurück wie:
        "Yes, there is a button labeled 'Artikel-Stamm' at coordinates (x, y)"
        oder
        "The 'ERFASSUNG' menu is located at the top, coordinates: x=380, y=75"
        """
        response_lower = response.lower()
        
        # Prüfe ob Element gefunden wurde
        found_indicators = ['yes', 'found', 'located', 'visible', 'there is']
        not_found_indicators = ['no', 'not found', 'cannot find', 'unable to locate']
        
        found = any(ind in response_lower for ind in found_indicators)
        not_found = any(ind in response_lower for ind in not_found_indicators)
        
        if not_found:
            found = False
        
        # Extrahiere Koordinaten (verschiedene Formate)
        coordinates = None
        if extract_coords and found:
            coordinates = self._extract_coordinates(response)
        
        # Confidence-Schätzung basierend auf Response
        confidence = 0.8 if found and coordinates else 0.5 if found else 0.0
        
        return {
            'found': found,
            'description': response,
            'coordinates': coordinates,
            'confidence': confidence
        }
    
    def _extract_coordinates(self, text: str) -> Optional[Tuple[int, int]]:
        """
        Extrahiert x,y Koordinaten aus Text
        
        Unterstützte Formate:
        - (x, y)
        - (x,y)
        - x=123, y=456
        - coordinates: 123, 456
        """
        # Pattern 1: (x, y)
        pattern1 = r'\((\d+),\s*(\d+)\)'
        match = re.search(pattern1, text)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        # Pattern 2: x=123, y=456
        pattern2 = r'x\s*=\s*(\d+).*?y\s*=\s*(\d+)'
        match = re.search(pattern2, text, re.IGNORECASE)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        # Pattern 3: coordinates: 123, 456
        pattern3 = r'coordinates?:?\s*(\d+),\s*(\d+)'
        match = re.search(pattern3, text, re.IGNORECASE)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        return None
    
    def find_menu_item(
        self, 
        screenshot_path: str, 
        menu_name: str
    ) -> Dict[str, any]:
        """
        Findet ein Menü-Item (Button, Icon, Menü-Eintrag)
        
        Args:
            screenshot_path: Pfad zum Screenshot
            menu_name: Name des Menü-Items (z.B. "Artikel-Stamm", "ERFASSUNG")
        
        Returns:
            Dict mit 'found', 'coordinates', etc.
        """
        query = (
            f"Find the clickable button, icon, or menu item labeled '{menu_name}'. "
            f"Provide the x,y pixel coordinates where I should click."
        )
        
        return self.detect_ui_elements(screenshot_path, query, return_coordinates=True)
    
    def find_icon_by_description(
        self, 
        screenshot_path: str, 
        description: str
    ) -> Dict[str, any]:
        """
        Findet ein Icon basierend auf Beschreibung
        
        Args:
            screenshot_path: Pfad zum Screenshot
            description: Beschreibung des Icons (z.B. "shopping cart icon", "document icon")
        
        Returns:
            Dict mit 'found', 'coordinates', etc.
        """
        query = (
            f"Find the {description} in the toolbar or menu. "
            f"Provide the x,y pixel coordinates of its center."
        )
        
        return self.detect_ui_elements(screenshot_path, query, return_coordinates=True)
    
    def verify_page_loaded(
        self, 
        screenshot_path: str, 
        expected_title: str
    ) -> bool:
        """
        Verifiziert ob eine Seite/Maske korrekt geladen wurde
        
        Args:
            screenshot_path: Pfad zum Screenshot
            expected_title: Erwarteter Titel der Maske
        
        Returns:
            True wenn Maske korrekt geladen
        """
        query = f"Is there a heading or title that says '{expected_title}'? Answer yes or no."
        
        result = self.detect_ui_elements(screenshot_path, query, return_coordinates=False)
        
        return result['found']
    
    def get_canvas_bounds(self, screenshot_path: str) -> Optional[Dict[str, int]]:
        """
        Ermittelt die Bounds des Guacamole-Canvas (RDP-Inhaltsbereich)
        
        Returns:
            {'left': int, 'top': int, 'width': int, 'height': int}
        """
        query = (
            "Identify the main content area (the RDP/remote desktop canvas). "
            "Provide the coordinates of its top-left corner and dimensions."
        )
        
        result = self.detect_ui_elements(screenshot_path, query, return_coordinates=True)
        
        if result['found'] and result['coordinates']:
            # Schätze Dimensionen basierend auf Screenshot
            img = Image.open(screenshot_path)
            width, height = img.size
            
            # Canvas ist typischerweise zentriert
            return {
                'left': 72,  # Guacamole Standard
                'top': 0,
                'width': width - 72,
                'height': height
            }
        
        return None


def main():
    """Test-Funktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Moondream UI-Navigator Test')
    parser.add_argument('screenshot', help='Pfad zum Screenshot')
    parser.add_argument('--find', required=True, help='UI-Element zu finden (z.B. "Artikel-Stamm")')
    
    args = parser.parse_args()
    
    nav = MoondreamNavigator()
    
    if not nav.moondream_available:
        print("❌ Moondream-Station nicht verfügbar!")
        print("   Installieren Sie: pip install moondream-station")
        return
    
    print(f"🔍 Suche nach: {args.find}")
    print(f"   Screenshot: {args.screenshot}\n")
    
    result = nav.find_menu_item(args.screenshot, args.find)
    
    print(f"📊 Ergebnis:")
    print(f"   Gefunden: {result['found']}")
    print(f"   Confidence: {result['confidence']:.0%}")
    
    if result['coordinates']:
        x, y = result['coordinates']
        print(f"   Koordinaten: ({x}, {y})")
    
    print(f"\n💬 Moondream-Response:")
    print(f"   {result['description']}")


if __name__ == '__main__':
    main()

