#!/usr/bin/env python3
"""Fügt Sales-Übersetzungen zu translation.json hinzu"""
import json
from pathlib import Path

TRANSLATION_FILE = Path("packages/frontend-web/src/i18n/locales/de/translation.json")

NEW_FIELDS = {
    "salesSettings": "Verkaufseinstellungen",
    "priceGroup": "Preisgruppe",
    "priceGroupStandard": "Standard",
    "priceGroupPremium": "Premium",
    "priceGroupWholesale": "Großhandel",
    "priceGroupRetail": "Einzelhandel",
    "customerPriceList": "Kundenpreisliste",
    "priceListDefault": "Standard",
    "priceListSpecial": "Sonderpreisliste",
    "priceListContract": "Vertragspreisliste",
    "taxCategory": "Steuerkategorie",
    "taxCategoryStandard": "Standard (19%)",
    "taxCategoryReduced": "Ermäßigt (7%)",
    "taxCategoryZero": "Nullsatz (0%)",
    "taxCategoryReverseCharge": "Reverse Charge",
    "taxCategoryExempt": "Befreit",
    "customerSegment": "Kundensegment",
    "customerSegmentA": "Segment A (Premium)",
    "customerSegmentB": "Segment B (Standard)",
    "customerSegmentC": "Segment C (Basis)",
    "industry": "Branche",
    "industryAgriculture": "Landwirtschaft",
    "industryTrade": "Handel",
    "industryManufacturing": "Produktion",
    "industryService": "Dienstleistung",
    "industryOther": "Sonstige",
    "region": "Region",
    "regionNorth": "Nord",
    "regionSouth": "Süd",
    "regionEast": "Ost",
    "regionWest": "West",
    "regionCenter": "Mitte"
}

NEW_PLACEHOLDERS = {
    "priceGroup": "Wählen Sie die Preisgruppe für diesen Kunden",
    "customerPriceList": "Wählen Sie die Preisliste für diesen Kunden",
    "taxCategory": "Wählen Sie die Steuerkategorie",
    "customerSegment": "Wählen Sie das Kundensegment",
    "industry": "Wählen Sie die Branche",
    "region": "Wählen Sie die Region"
}

def main():
    with open(TRANSLATION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Füge Fields hinzu
    if 'crud' not in data:
        data['crud'] = {}
    if 'fields' not in data['crud']:
        data['crud']['fields'] = {}
    
    for key, value in NEW_FIELDS.items():
        if key not in data['crud']['fields']:
            data['crud']['fields'][key] = value
    
    # Füge Placeholders hinzu
    if 'tooltips' not in data['crud']:
        data['crud']['tooltips'] = {}
    if 'placeholders' not in data['crud']['tooltips']:
        data['crud']['tooltips']['placeholders'] = {}
    
    for key, value in NEW_PLACEHOLDERS.items():
        if key not in data['crud']['tooltips']['placeholders']:
            data['crud']['tooltips']['placeholders'][key] = value
    
    # Speichere
    with open(TRANSLATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"OK: {len(NEW_FIELDS)} Fields und {len(NEW_PLACEHOLDERS)} Placeholders hinzugefuegt")

if __name__ == "__main__":
    main()

