#!/usr/bin/env python3
"""
Icon-Detektor mit OCR + Computer Vision

Erkennt Icons und Buttons in L3-Screenshots ohne externe Vision-API.
Nutzt nur: pytesseract + OpenCV
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import json
from pathlib import Path
from typing import List, Dict, Tuple


class IconDetectorOCR:
    """Erkennt Icons via OCR + Template Matching"""
    
    def __init__(self):
        self.min_confidence = 60
    
    def detect_all_clickable_elements(self, screenshot_path: str) -> List[Dict]:
        """
        Erkennt alle klickbaren Elemente (Icons + Tabs)
        
        Returns:
            Liste von Elementen mit Koordinaten
        """
        # Bild laden
        img = Image.open(screenshot_path)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        width, height = img.size
        
        print(f"🔍 Analysiere Screenshot: {width}x{height}px")
        
        # OCR mit Bounding Boxes
        ocr_data = pytesseract.image_to_data(
            img,
            lang='eng',
            output_type=pytesseract.Output.DICT
        )
        
        elements = []
        
        # Extrahiere Text-Labels
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            if conf < self.min_confidence or not text:
                continue
            
            left = ocr_data['left'][i]
            top = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            
            # Berechne Zentrum
            center_x = left + w // 2
            center_y = top + h // 2
            
            # Prozentuale Koordinaten
            x_pct = (center_x / width) * 100
            y_pct = (center_y / height) * 100
            
            # Klassifiziere Element-Typ
            element_type = self._classify_element(text, top, height)
            
            # Nur relevante Elemente (Tabs + Icons in oberen 20%)
            if top < height * 0.2:
                elements.append({
                    'name': text,
                    'type': element_type,
                    'x_pct': round(x_pct, 1),
                    'y_pct': round(y_pct, 1),
                    'absolute': {'x': center_x, 'y': center_y},
                    'bbox': {'left': left, 'top': top, 'width': w, 'height': h},
                    'confidence': conf
                })
        
        print(f"✅ {len(elements)} Elemente erkannt")
        
        # Sortiere nach Y-Position (oben → unten)
        elements.sort(key=lambda e: (e['y_pct'], e['x_pct']))
        
        return elements
    
    def _classify_element(self, text: str, top: int, canvas_height: int) -> str:
        """Klassifiziert Element-Typ basierend auf Position und Text"""
        
        # Top 10% = Tabs (Menü-Leiste)
        if top < canvas_height * 0.10:
            # Großbuchstaben = Tab
            if text.isupper() and len(text) > 3:
                return 'menu_tab'
        
        # 10-15% = Ribbon Icons
        if top >= canvas_height * 0.08 and top < canvas_height * 0.15:
            return 'ribbon_icon'
        
        return 'other'
    
    def generate_csv(self, elements: List[Dict], output_path: str):
        """Generiert CSV aus erkannten Elementen"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=['group', 'name', 'x_pct', 'y_pct', 'submenu_y_pct']
            )
            writer.writeheader()
            
            for elem in elements:
                if elem['type'] in ['menu_tab', 'ribbon_icon']:
                    group = 'tabs' if elem['type'] == 'menu_tab' else 'ribbon'
                    writer.writerow({
                        'group': group,
                        'name': elem['name'].replace(' ', '_'),
                        'x_pct': elem['x_pct'],
                        'y_pct': elem['y_pct'],
                        'submenu_y_pct': ''
                    })
        
        print(f"✅ CSV generiert: {output_path}")
    
    def visualize_detections(
        self, 
        screenshot_path: str, 
        elements: List[Dict],
        output_path: str
    ):
        """Erstellt Debug-Bild mit markierten Elementen"""
        img = cv2.imread(screenshot_path)
        
        for elem in elements:
            if elem['type'] not in ['menu_tab', 'ribbon_icon']:
                continue
            
            bbox = elem['bbox']
            
            # Zeichne Bounding Box
            color = (0, 255, 0) if elem['type'] == 'menu_tab' else (255, 0, 0)
            cv2.rectangle(
                img,
                (bbox['left'], bbox['top']),
                (bbox['left'] + bbox['width'], bbox['top'] + bbox['height']),
                color,
                2
            )
            
            # Label
            label = f"{elem['name']} ({elem['x_pct']:.1f}%)"
            cv2.putText(
                img,
                label,
                (bbox['left'], bbox['top'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )
        
        cv2.imwrite(output_path, img)
        print(f"✅ Debug-Bild gespeichert: {output_path}")


def main():
    """Hauptprogramm"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Icon-Detektor mit OCR')
    parser.add_argument('screenshot', help='Screenshot der L3-Startseite')
    parser.add_argument('--output-csv', default='l3_gui_map_detected.csv', help='Output-CSV')
    parser.add_argument('--debug-image', help='Debug-Bild mit Markierungen')
    
    args = parser.parse_args()
    
    detector = IconDetectorOCR()
    
    print("🚀 Starte Icon-Erkennung...\n")
    
    # Erkenne Elemente
    elements = detector.detect_all_clickable_elements(args.screenshot)
    
    # Zeige Ergebnisse
    print(f"\n📋 Erkannte Elemente:\n")
    for elem in elements:
        if elem['type'] in ['menu_tab', 'ribbon_icon']:
            print(f"  {elem['type']:12s} | {elem['name']:20s} | "
                  f"({elem['x_pct']:5.1f}%, {elem['y_pct']:5.1f}%) | "
                  f"Conf: {elem['confidence']}%")
    
    # Export CSV
    detector.generate_csv(elements, args.output_csv)
    
    # Debug-Visualisierung
    if args.debug_image:
        detector.visualize_detections(args.screenshot, elements, args.debug_image)
    
    # Export JSON
    json_path = Path(args.output_csv).with_suffix('.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(elements, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ JSON exportiert: {json_path}")
    print(f"\n🎉 Fertig! {len(elements)} Elemente erkannt")


if __name__ == '__main__':
    main()

