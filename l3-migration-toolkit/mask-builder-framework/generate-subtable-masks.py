#!/usr/bin/env python3
"""
Generiert Untertabellen-Masken für Kundenstamm
"""

import json
from pathlib import Path

# Untertabellen-Definitionen
subtable_definitions = {
    "kunden_profil": {
        "name": "kunden_profil",
        "label": "Kundenprofil",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "firmenname", "label": "Firmenname", "type": "string", "grid": 3 },
            { "id": "gruendung", "label": "Gründung", "type": "date", "grid": 3 },
            { "id": "jahresumsatz", "label": "Jahresumsatz", "type": "number", "grid": 3 },
            { "id": "berufsgenossenschaft", "label": "Berufsgenossenschaft", "type": "string", "grid": 3 },
            { "id": "berufsgen_nr", "label": "Berufsgen.-Nr.", "type": "string", "grid": 3 },
            { "id": "branche", "label": "Branche", "type": "string", "grid": 3 },
            { "id": "mitbewerber", "label": "Mitbewerber", "type": "text", "grid": 3 },
            { "id": "engpaesse", "label": "Engpässe", "type": "text", "grid": 3 },
            { "id": "organisationsstruktur", "label": "Organisationsstruktur", "type": "text", "grid": 3 },
            { "id": "mitarbeiteranzahl", "label": "Mitarbeiteranzahl", "type": "number", "grid": 3 },
            { "id": "wettbewerbsdifferenzierung", "label": "Wettbewerbsdifferenzierung", "type": "text", "grid": 3 },
            { "id": "betriebsrat", "label": "Betriebsrat", "type": "boolean", "grid": 3 },
            { "id": "unternehmensphilosophie", "label": "Unternehmensphilosophie", "type": "text", "grid": 1 }
        ]
    },
    "kunden_ansprechpartner": {
        "name": "kunden_ansprechpartner",
        "label": "Ansprechpartner",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": True,
        "fields": [
            { "id": "vorname", "label": "Vorname", "type": "string", "grid": 3 },
            { "id": "nachname", "label": "Nachname", "type": "string", "grid": 3 },
            { "id": "position", "label": "Position", "type": "string", "grid": 3 },
            { "id": "abteilung", "label": "Abteilung", "type": "string", "grid": 3 },
            { "id": "telefon1", "label": "Telefon 1", "type": "string", "grid": 3 },
            { "id": "telefon2", "label": "Telefon 2", "type": "string", "grid": 3 },
            { "id": "mobil", "label": "Mobil", "type": "string", "grid": 3 },
            { "id": "email", "label": "E-Mail", "type": "email", "grid": 3 },
            { "id": "strasse", "label": "Straße", "type": "string", "grid": 3 },
            { "id": "plz", "label": "PLZ", "type": "string", "grid": 3 },
            { "id": "ort", "label": "Ort", "type": "string", "grid": 3 },
            { "id": "anrede", "label": "Anrede", "type": "string", "grid": 3 },
            { "id": "briefanrede", "label": "Briefanrede", "type": "string", "grid": 3 },
            { "id": "geburtsdatum", "label": "Geburtsdatum", "type": "date", "grid": 3 },
            { "id": "hobbys", "label": "Hobbys", "type": "text", "grid": 3 },
            { "id": "info1", "label": "Info 1", "type": "text", "grid": 3 },
            { "id": "info2", "label": "Info 2", "type": "text", "grid": 3 },
            { "id": "empfanger_rechnung_email", "label": "Rechnung per Mail", "type": "boolean", "grid": 3 },
            { "id": "empfanger_mahnung_email", "label": "Mahnung per Mail", "type": "boolean", "grid": 3 },
            { "id": "kontaktart", "label": "Kontaktart", "type": "string", "grid": 3 },
            { "id": "erstanlage", "label": "Erstanlage", "type": "date", "grid": 3 },
            { "id": "cad_system", "label": "CAD-System", "type": "string", "grid": 3 },
            { "id": "softwaresysteme", "label": "Softwaresysteme", "type": "string", "grid": 3 },
            { "id": "datenschutzbeauftragter", "label": "Datenschutzbeauftragter", "type": "boolean", "grid": 3 }
        ]
    },
    "kunden_versand": {
        "name": "kunden_versand",
        "label": "Versandinformationen",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "versandart_rechnung", "label": "Versandart Rechnung", "type": "select", "grid": 3 },
            { "id": "versandart_mahnung", "label": "Versandart Mahnung", "type": "select", "grid": 3 },
            { "id": "versandart_kontakt", "label": "Versandart Kontakt", "type": "select", "grid": 3 },
            { "id": "dispo_nummer", "label": "Dispo-Nummer", "type": "string", "grid": 3 },
            { "id": "initialisierungsweisung", "label": "Initialisierungsweisung", "type": "text", "grid": 1 },
            { "id": "versandmedium", "label": "Versandmedium", "type": "select", "grid": 3 }
        ]
    },
    "kunden_lieferung_zahlung": {
        "name": "kunden_lieferung_zahlung",
        "label": "Lieferung/Zahlung",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "lieferbedingung", "label": "Lieferbedingung", "type": "string", "grid": 3 },
            { "id": "zahlungsbedingung", "label": "Zahlungsbedingung", "type": "string", "grid": 3 },
            { "id": "faelligkeit_ab", "label": "Fälligkeit ab", "type": "select", "grid": 3 },
            { "id": "pro_forma_rechnung", "label": "Pro-Forma-Rechnung", "type": "boolean", "grid": 3 },
            { "id": "pro_forma_rabatt1", "label": "Pro-Forma-Rabatt 1", "type": "number", "grid": 3 },
            { "id": "pro_forma_rabatt2", "label": "Pro-Forma-Rabatt 2", "type": "number", "grid": 3 },
            { "id": "einzel_sammelversand_avis", "label": "Einzel-/Sammelversand-Avis", "type": "select", "grid": 3 }
        ]
    },
    "kunden_datenschutz": {
        "name": "kunden_datenschutz",
        "label": "Datenschutz",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "einwilligung", "label": "Einwilligung", "type": "boolean", "grid": 3 },
            { "id": "anlagedatum", "label": "Anlagedatum", "type": "date", "grid": 3 },
            { "id": "anlagebearbeiter", "label": "Anlagebearbeiter", "type": "string", "grid": 3 },
            { "id": "zusatzbemerkung", "label": "Zusatzbemerkung", "type": "text", "grid": 1 }
        ]
    },
    "kunden_genossenschaft": {
        "name": "kunden_genossenschaft",
        "label": "Genossenschaftsanteile",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "geschaeftsguthaben_konto", "label": "Geschäftsguthaben-Konto", "type": "string", "grid": 3 },
            { "id": "mitgliedschaft_gekuendigt", "label": "Mitgliedschaft gekündigt", "type": "boolean", "grid": 3 },
            { "id": "kuendigungsgrund", "label": "Kündigungsgrund", "type": "text", "grid": 1 },
            { "id": "datum_kuendigung", "label": "Datum Kündigung", "type": "date", "grid": 3 },
            { "id": "datum_austritt", "label": "Datum Austritt", "type": "date", "grid": 3 },
            { "id": "mitgliedsnummer", "label": "Mitgliedsnummer", "type": "string", "grid": 3 },
            { "id": "pflichtanteile", "label": "Pflichtanteile", "type": "number", "grid": 3 },
            { "id": "eintrittsdatum", "label": "Eintrittsdatum", "type": "date", "grid": 3 }
        ]
    },
    "kunden_email_verteiler": {
        "name": "kunden_email_verteiler",
        "label": "E-Mail-Verteiler",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": True,
        "fields": [
            { "id": "verteilername", "label": "Verteilername", "type": "string", "grid": 3 },
            { "id": "bezeichnung", "label": "Bezeichnung", "type": "string", "grid": 3 },
            { "id": "email", "label": "E-Mail-Adresse", "type": "email", "grid": 3 }
        ]
    },
    "kunden_betriebsgemeinschaften": {
        "name": "kunden_betriebsgemeinschaften",
        "label": "Betriebsgemeinschaften",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": True,
        "fields": [
            { "id": "verbundnummer", "label": "Verbundnummer", "type": "string", "grid": 3 },
            { "id": "mitglieder_kunden_nr", "label": "Mitglieder (Kunden-Nr.)", "type": "lookup", "grid": 3 },
            { "id": "anteil_prozent", "label": "Anteil (%)", "type": "number", "grid": 3 }
        ]
    },
    "kunden_freitext": {
        "name": "kunden_freitext",
        "label": "Freitext & Anweisungen",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "chef_anweisung", "label": "Chef-Anweisung", "type": "text", "grid": 1 },
            { "id": "langtext", "label": "Langtext", "type": "text", "grid": 1 },
            { "id": "bemerkungen", "label": "Bemerkungen", "type": "text", "grid": 1 }
        ]
    },
    "kunden_allgemein_erweitert": {
        "name": "kunden_allgemein_erweitert",
        "label": "Allgemein Erweitert",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": False,
        "fields": [
            { "id": "staat", "label": "Staat", "type": "string", "grid": 3 },
            { "id": "bundesland", "label": "Bundesland", "type": "string", "grid": 3 },
            { "id": "kunde_seit", "label": "Kunde seit", "type": "date", "grid": 3 },
            { "id": "debitoren_konto", "label": "Debitoren-Konto", "type": "string", "grid": 3 },
            { "id": "deb_kto_hauptkonto", "label": "Deb.-Kto. Hauptkonto", "type": "string", "grid": 3 },
            { "id": "disponent", "label": "Disponent", "type": "string", "grid": 3 },
            { "id": "vertriebsbeauftragter", "label": "Vertriebsbeauftragter", "type": "string", "grid": 3 },
            { "id": "abc_umsatzstatus", "label": "ABC/Umsatzstatus", "type": "string", "grid": 3 },
            { "id": "betriebsnummer", "label": "Betriebsnummer", "type": "string", "grid": 3 },
            { "id": "ust_id_nr", "label": "UST-ID-Nr.", "type": "string", "grid": 3 },
            { "id": "steuernummer", "label": "Steuernummer", "type": "string", "grid": 3 },
            { "id": "sperrgrund", "label": "Sperrgrund", "type": "text", "grid": 1 },
            { "id": "kundengruppe", "label": "Kundengruppe", "type": "string", "grid": 3 },
            { "id": "fax_sperre", "label": "Fax-Sperre", "type": "boolean", "grid": 3 },
            { "id": "infofeld4", "label": "Info 4", "type": "text", "grid": 3 },
            { "id": "infofeld5", "label": "Info 5", "type": "text", "grid": 3 },
            { "id": "infofeld6", "label": "Info 6", "type": "text", "grid": 3 }
        ]
    },
    "kunden_cpd_konto": {
        "name": "kunden_cpd_konto",
        "label": "CPD-Konto",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": True,
        "fields": [
            { "id": "debitoren_konto", "label": "Debitoren-Konto", "type": "string", "grid": 3 },
            { "id": "suchbegriff", "label": "Suchbegriff", "type": "string", "grid": 3 },
            { "id": "rechnungsadresse", "label": "Rechnungsadresse", "type": "text", "grid": 1 },
            { "id": "geschaeftsstelle", "label": "Geschäftsstelle", "type": "string", "grid": 3 },
            { "id": "kostenstelle", "label": "Kostenstelle", "type": "string", "grid": 3 },
            { "id": "rechnungsart", "label": "Rechnungsart", "type": "string", "grid": 3 },
            { "id": "sammelrechnung", "label": "Sammelrechnung", "type": "boolean", "grid": 3 },
            { "id": "rechnungsformular", "label": "Rechnungsformular", "type": "string", "grid": 3 },
            { "id": "vb", "label": "VB", "type": "string", "grid": 3 },
            { "id": "gebiet", "label": "Gebiet", "type": "string", "grid": 3 },
            { "id": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "type": "text", "grid": 1 }
        ]
    },
    "kunden_rabatte_detail": {
        "name": "kunden_rabatte_detail",
        "label": "Rabatte Detail",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": True,
        "fields": [
            { "id": "artikel_nr", "label": "Artikel-Nr.", "type": "lookup", "grid": 3 },
            { "id": "bezeichnung", "label": "Bezeichnung", "type": "string", "grid": 3 },
            { "id": "rabatt", "label": "Rabatt (%)", "type": "number", "grid": 3 },
            { "id": "rabatt_gueltig_bis", "label": "Rabatt gültig bis", "type": "date", "grid": 3 },
            { "id": "rabatt_liste_id", "label": "Rabatt-Liste", "type": "lookup", "grid": 3 },
            { "id": "rabatt_liste_speichern", "label": "Rabatt-Liste speichern", "type": "boolean", "grid": 3 }
        ]
    },
    "kunden_preise_detail": {
        "name": "kunden_preise_detail",
        "label": "Kundenpreise Detail",
        "parent": "kunden",
        "parentField": "kunden_nr",
        "multiple": True,
        "fields": [
            { "id": "artikel_nr", "label": "Artikel-Nr.", "type": "lookup", "grid": 3 },
            { "id": "bezeichnung", "label": "Bezeichnung", "type": "string", "grid": 3 },
            { "id": "preis_netto", "label": "Preis netto", "type": "number", "grid": 3 },
            { "id": "preis_inkl_fracht", "label": "Preis inkl. Fracht", "type": "number", "grid": 3 },
            { "id": "preis_einheit", "label": "Preis-Einheit", "type": "string", "grid": 3 },
            { "id": "rabatt_erlaubt", "label": "Rabatt erlaubt", "type": "boolean", "grid": 3 },
            { "id": "sonderfracht", "label": "Sonderfracht", "type": "number", "grid": 3 },
            { "id": "zahlungsbedingung", "label": "Zahlungsbedingung", "type": "string", "grid": 3 },
            { "id": "gueltig_bis", "label": "Gültig bis", "type": "date", "grid": 3 },
            { "id": "bediener", "label": "Bediener", "type": "string", "grid": 3 }
        ]
    }
}

def generate_subtable_mask(subtable_def):
    """Generiert Mask für Untertabelle"""
    
    # Lade Template
    with open('base-template.json', 'r', encoding='utf-8') as f:
        template = json.load(f)
    
    # Erstelle Mask
    mask = template.copy()
    
    # Meta
    mask['meta']['name'] = subtable_def['name']
    mask['meta']['description'] = f"{subtable_def['label']} für Kundenstamm"
    
    # Resource
    mask['resource'] = subtable_def['name']
    
    # Routing
    mask['routing']['basePath'] = f"/verkauf/kunden-stamm/{subtable_def['name']}"
    mask['routing']['param'] = "id"
    
    # Erstelle Views
    sections = []
    section_fields = []
    
    for field in subtable_def['fields']:
        field_def = {
            "comp": field['type'].capitalize(),
            "bind": field['id'],
            "label": field['label']
        }
        
        # Grid-Spanning
        if field.get('grid') == 1:
            field_def['span'] = 3
        
        section_fields.append(field_def)
    
    sections.append({
        "title": subtable_def['label'],
        "grid": 3,
        "fields": section_fields
    })
    
    mask['views'] = [{
        "id": "main",
        "label": subtable_def['label'],
        "sections": sections
    }]
    
    # Navigation
    mask['layout']['nav'] = [
        { "id": "main", "label": subtable_def['label'], "icon": "FileText" }
    ]
    
    return mask

def main():
    """Hauptfunktion"""
    
    print("=" * 80)
    print("GENERIERE UNTERTABELLEN-MASKEN")
    print("=" * 80)
    
    output_dir = Path("generated/subtables")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for subtable_name, subtable_def in subtable_definitions.items():
        print(f"\n📝 Generiere: {subtable_def['label']}")
        
        mask = generate_subtable_mask(subtable_def)
        
        output_file = output_dir / f"{subtable_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mask, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Gespeichert: {output_file}")
        print(f"   📊 Felder: {len(subtable_def['fields'])}")
    
    print("\n" + "=" * 80)
    print("✅ ALLE UNTERTABELLEN-MASKEN GENERIERT")
    print("=" * 80)
    print(f"\n📁 Output-Verzeichnis: {output_dir}")
    print(f"📊 Anzahl: {len(subtable_definitions)} Masken")

if __name__ == "__main__":
    main()

