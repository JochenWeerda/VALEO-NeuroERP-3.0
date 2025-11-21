#!/usr/bin/env python3
"""
L3-Masken OCR-Pipeline

Extrahiert Feldnamen und UI-Elemente aus L3-Screenshots mittels Tesseract OCR.
Verwendet image_to_data() für Bounding Boxes und intelligente Feld-Zuordnung.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import json

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    import numpy as np
    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    IMPORT_ERROR = str(e)


class L3MaskOCR:
    """OCR-basierte Feldextraktion aus L3-Screenshots"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Args:
            tesseract_path: Pfad zu tesseract.exe (optional)
        """
        if not DEPS_AVAILABLE:
            raise ImportError(
                f"OCR-Dependencies nicht verfügbar: {IMPORT_ERROR}\n"
                "Installieren Sie: pip install pytesseract pillow opencv-python\n"
                "Tesseract Binary: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.confidence_threshold = 60  # Min. OCR-Confidence
    
    def preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Preprocessing für bessere OCR-Ergebnisse:
        - Graustufen-Konvertierung
        - Kontrast-Erhöhung
        - Schärfung
        - Rauschreduzierung
        """
        # Convert PIL Image to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Graustufen
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Kontrast erhöhen (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Bilateral Filter (Rauschreduzierung, Kanten behalten)
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Schwellwert-Anpassung (Adaptive Thresholding)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to PIL
        return Image.fromarray(thresh)
    
    def extract_fields(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Extrahiert strukturierte Felder aus Screenshot
        
        Returns:
            {
                'raw_text': str,
                'fields': List[Dict],
                'tabs': List[str],
                'metadata': Dict
            }
        """
        img = Image.open(screenshot_path)
        
        # Preprocessing
        processed_img = self.preprocess_image(img)
        
        # OCR mit Bounding Boxes (Nur Englisch - bessere Erkennung!)
        # Erfahrungswert: English traineddata funktioniert besser als Deutsch
        ocr_data = pytesseract.image_to_data(
            processed_img, 
            lang='eng',
            output_type=pytesseract.Output.DICT
        )
        
        # Raw Text für LLM-Analyse
        raw_text = pytesseract.image_to_string(processed_img, lang='eng')
        
        # Parse UI-Felder
        fields = self.parse_ui_fields(ocr_data)
        
        # Extrahiere Tabs
        tabs = self.extract_tabs(ocr_data)
        
        return {
            'raw_text': raw_text,
            'fields': fields,
            'tabs': tabs,
            'metadata': {
                'image_size': img.size,
                'total_words': len([w for w in ocr_data['text'] if w.strip()]),
                'avg_confidence': self._calculate_avg_confidence(ocr_data)
            }
        }
    
    def parse_ui_fields(self, ocr_data: Dict) -> List[Dict[str, Any]]:
        """
        Parst UI-Felder aus OCR-Daten
        
        Logik:
        1. Finde Labels (Texte mit ":" am Ende, linke Seite)
        2. Finde zugehörige Input-Felder (rechts vom Label)
        3. Erkenne Feldtypen (Dropdown "▼", Checkbox "☐", Lookup "...")
        """
        fields = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Filtere niedrige Confidence
            if conf < self.confidence_threshold or not text:
                continue
            
            # Erkenne Label (endet mit ":")
            if text.endswith(':'):
                label = text[:-1].strip()
                
                # Finde zugehöriges Input-Feld (rechts vom Label)
                field_value, field_type = self._find_field_right_of_label(
                    ocr_data, i
                )
                
                fields.append({
                    'label': label,
                    'type': field_type,
                    'example_value': field_value,
                    'position': {
                        'left': ocr_data['left'][i],
                        'top': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    },
                    'confidence': conf
                })
        
        return fields
    
    def _find_field_right_of_label(
        self, ocr_data: Dict, label_idx: int
    ) -> Tuple[str, str]:
        """
        Findet Input-Feld rechts vom Label
        
        Returns:
            (field_value, field_type)
        """
        label_left = ocr_data['left'][label_idx]
        label_top = ocr_data['top'][label_idx]
        label_height = ocr_data['height'][label_idx]
        
        # Suche Texte rechts vom Label (innerhalb 500px, gleiche Höhe ±20px)
        candidates = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            if i == label_idx:
                continue
            
            text = ocr_data['text'][i].strip()
            left = ocr_data['left'][i]
            top = ocr_data['top'][i]
            
            # Rechts vom Label?
            if left > label_left and left < label_left + 500:
                # Gleiche Höhe?
                if abs(top - label_top) < 20:
                    candidates.append({
                        'text': text,
                        'left': left,
                        'conf': int(ocr_data['conf'][i])
                    })
        
        if not candidates:
            return '', 'text'
        
        # Nächster Kandidat = Input-Feld
        candidates.sort(key=lambda x: x['left'])
        field_value = candidates[0]['text']
        
        # Erkenne Feldtyp
        field_type = self._detect_field_type(field_value, ocr_data, label_idx)
        
        return field_value, field_type
    
    def _detect_field_type(
        self, field_value: str, ocr_data: Dict, label_idx: int
    ) -> str:
        """
        Erkennt Feldtyp basierend auf Kontext
        """
        # Lookup-Felder (haben "..." Button)
        if '...' in field_value or '…' in field_value:
            return 'lookup'
        
        # Dropdown (hat ▼ oder Dropdown-Symbol)
        if '▼' in field_value or '▾' in field_value:
            return 'select'
        
        # Checkbox (☐ oder ☑)
        if '☐' in field_value or '☑' in field_value or '✓' in field_value:
            return 'boolean'
        
        # Datum (Pattern matching)
        if self._looks_like_date(field_value):
            return 'date'
        
        # Nummer (nur Ziffern)
        if field_value.replace('.', '').replace(',', '').isdigit():
            return 'number'
        
        # Default: Text
        return 'string'
    
    def _looks_like_date(self, text: str) -> bool:
        """Prüft ob Text ein Datum ist"""
        import re
        date_patterns = [
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
            r'\d{4}-\d{2}-\d{2}',     # YYYY-MM-DD
        ]
        return any(re.match(p, text) for p in date_patterns)
    
    def extract_tabs(self, ocr_data: Dict) -> List[str]:
        """
        Extrahiert Tab-Namen aus Screenshot
        
        Tabs sind typischerweise:
        - Großbuchstaben
        - Horizontal angeordnet
        - Oben im Formular
        """
        tabs = []
        n_boxes = len(ocr_data['text'])
        
        # Suche nach Tab-Texten (Y-Position < 400, nur Großbuchstaben)
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            top = ocr_data['top'][i]
            conf = int(ocr_data['conf'][i])
            
            if conf < self.confidence_threshold or not text:
                continue
            
            # Tab-Kriterien
            if top < 400 and text.isupper() and len(text) > 3:
                tabs.append(text)
        
        return list(set(tabs))  # Deduplizierung
    
    def _calculate_avg_confidence(self, ocr_data: Dict) -> float:
        """Berechnet durchschnittliche OCR-Confidence"""
        confs = [int(c) for c in ocr_data['conf'] if int(c) > 0]
        return sum(confs) / len(confs) if confs else 0.0
    
    def save_debug_image(self, screenshot_path: str, output_path: str):
        """Speichert preprocessed Image für Debugging"""
        img = Image.open(screenshot_path)
        processed = self.preprocess_image(img)
        processed.save(output_path)
        print(f"✅ Debug-Image gespeichert: {output_path}")


def main():
    """Test-Funktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='L3-Masken OCR-Extraktion')
    parser.add_argument('screenshot', help='Pfad zum Screenshot')
    parser.add_argument('--tesseract', help='Pfad zu tesseract.exe', default=None)
    parser.add_argument('--debug', action='store_true', help='Debug-Modus')
    
    args = parser.parse_args()
    
    try:
        ocr = L3MaskOCR(tesseract_path=args.tesseract)
        
        print(f"🔍 Analysiere: {args.screenshot}")
        results = ocr.extract_fields(args.screenshot)
        
        print(f"\n📊 Ergebnisse:")
        print(f"   Gefundene Felder: {len(results['fields'])}")
        print(f"   Gefundene Tabs: {len(results['tabs'])}")
        print(f"   Durchschn. Confidence: {results['metadata']['avg_confidence']:.1f}%")
        
        print(f"\n📋 Felder:")
        for field in results['fields'][:10]:  # Erste 10
            print(f"   - {field['label']}: {field['type']} (Confidence: {field['confidence']}%)")
        
        if results['tabs']:
            print(f"\n📑 Tabs:")
            for tab in results['tabs']:
                print(f"   - {tab}")
        
        if args.debug:
            debug_path = Path(args.screenshot).with_suffix('.debug.png')
            ocr.save_debug_image(args.screenshot, str(debug_path))
        
        # Speichere JSON
        output_path = Path(args.screenshot).with_suffix('.ocr.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ OCR-Ergebnisse gespeichert: {output_path}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

