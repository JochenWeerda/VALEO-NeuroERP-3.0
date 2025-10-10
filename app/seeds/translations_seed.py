"""
Initial German Translation Seed für erste 10 Agrar-Masken
Kompakter Seed - erweiterbar via API später
"""

INITIAL_TRANSLATIONS = [
    # === COMMON (Überall verwendet) ===
    ('common.save', 'common', 'Speichern', 'Save button'),
    ('common.cancel', 'common', 'Abbrechen', 'Cancel button'),
    ('common.delete', 'common', 'Löschen', 'Delete button'),
    ('common.edit', 'common', 'Bearbeiten', 'Edit button'),
    ('common.create', 'common', 'Neu anlegen', 'Create new button'),
    ('common.export', 'common', 'Exportieren', 'Export button'),
    ('common.import', 'common', 'Importieren', 'Import button'),
    ('common.search', 'common', 'Suchen', 'Search field'),
    ('common.filter', 'common', 'Filtern', 'Filter'),
    ('common.actions', 'common', 'Aktionen', 'Actions column'),
    ('common.loading', 'common', 'Lädt...', 'Loading indicator'),
    ('common.error', 'common', 'Fehler', 'Error message'),
    ('common.success', 'common', 'Erfolgreich', 'Success message'),
    ('common.yes', 'common', 'Ja', 'Yes'),
    ('common.no', 'common', 'Nein', 'No'),
    ('common.back', 'common', 'Zurück', 'Back button'),
    ('common.next', 'common', 'Weiter', 'Next button'),
    ('common.finish', 'common', 'Abschließen', 'Finish button'),
    
    # === AGRAR.SAATGUT (Maske 1-8) ===
    # 1. Saatgutstammdaten
    ('agrar.saatgut.stamm.title', 'agrar', 'Saatgutstammdaten', 'Seed master data title'),
    ('agrar.saatgut.stamm.section.allgemein', 'agrar', 'Allgemein', 'General section'),
    ('agrar.saatgut.stamm.section.zulassung', 'agrar', 'Zulassung', 'Approval section'),
    ('agrar.saatgut.stamm.section.agronomie', 'agrar', 'Agronomie', 'Agronomy section'),
    ('agrar.saatgut.stamm.section.preise', 'agrar', 'Preise & Konditionen', 'Prices section'),
    ('agrar.saatgut.stamm.field.sorte', 'agrar', 'Sorte', 'Variety'),
    ('agrar.saatgut.stamm.field.art', 'agrar', 'Art', 'Species'),
    ('agrar.saatgut.stamm.field.zuechter', 'agrar', 'Züchter', 'Breeder'),
    ('agrar.saatgut.stamm.field.tkm', 'agrar', 'TKM (g)', 'Thousand kernel mass'),
    ('agrar.saatgut.stamm.field.keimfaehigkeit', 'agrar', 'Keimfähigkeit (%)', 'Germination rate'),
    
    # 2. Saatgut-Liste
    ('agrar.saatgut.liste.title', 'agrar', 'Saatgut-Übersicht', 'Seed overview'),
    ('agrar.saatgut.liste.subtitle', 'agrar', 'Alle Saatgutsorten verwalten', 'Manage all seed varieties'),
    ('agrar.saatgut.liste.filter.art', 'agrar', 'Art', 'Species filter'),
    ('agrar.saatgut.liste.filter.zuechter', 'agrar', 'Züchter', 'Breeder filter'),
    ('agrar.saatgut.liste.filter.verfuegbarkeit', 'agrar', 'Verfügbarkeit', 'Availability filter'),
    ('agrar.saatgut.liste.action.sortenkatalog', 'agrar', 'Sortenkatalog drucken', 'Print variety catalog'),
    
    # 3. Saatgut bestellen (Wizard)
    ('agrar.saatgut.bestellung.title', 'agrar', 'Saatgut bestellen', 'Order seed'),
    ('agrar.saatgut.bestellung.step1', 'agrar', 'Kulturart wählen', 'Select crop'),
    ('agrar.saatgut.bestellung.step2', 'agrar', 'Sorte auswählen', 'Select variety'),
    ('agrar.saatgut.bestellung.step3', 'agrar', 'Menge & Einheit', 'Quantity & unit'),
    ('agrar.saatgut.bestellung.step4', 'agrar', 'Liefertermin', 'Delivery date'),
    ('agrar.saatgut.bestellung.step5', 'agrar', 'Bestätigung', 'Confirmation'),
    
    # 4. Lizenzen
    ('agrar.saatgut.lizenzen.title', 'agrar', 'Saatgut-Lizenzen', 'Seed licenses'),
    ('agrar.saatgut.lizenzen.field.lizenzgebuehr', 'agrar', 'Lizenzgebühr', 'License fee'),
    ('agrar.saatgut.lizenzen.field.nachbau', 'agrar', 'Nachbaugebühr', 'Farm-saved seed fee'),
    
    # 5. Zulassungen
    ('agrar.saatgut.zulassungen.title', 'agrar', 'Zulassungsregister', 'Approval register'),
    ('agrar.saatgut.zulassungen.field.bsa', 'agrar', 'BSA-Sortenliste', 'BSA variety list'),
    ('agrar.saatgut.zulassungen.field.eu', 'agrar', 'EU-Sortenkatalog', 'EU variety catalog'),
    
    # 6. Prognose
    ('agrar.saatgut.prognose.title', 'agrar', 'Absatzprognose Saatgut', 'Seed sales forecast'),
    ('agrar.saatgut.prognose.kpi.letzte_saison', 'agrar', 'Absatz letzte Saison', 'Last season sales'),
    ('agrar.saatgut.prognose.kpi.prognose', 'agrar', 'Prognose aktuelle Saison', 'Current season forecast'),
    
    # 7. Qualitätskontrolle
    ('agrar.saatgut.qualitaet.title', 'agrar', 'Qualitätskontrolle Saatgut', 'Seed quality control'),
    ('agrar.saatgut.qualitaet.field.keimfaehigkeit', 'agrar', 'Keimfähigkeitsprüfung', 'Germination test'),
    ('agrar.saatgut.qualitaet.field.sortenechtheit', 'agrar', 'Sortenechtheit', 'Varietal purity'),
    
    # 8. Sortenfinder
    ('agrar.saatgut.finder.title', 'agrar', 'Sortenfinder (AI-gestützt)', 'Variety finder (AI)'),
    ('agrar.saatgut.finder.field.standort', 'agrar', 'Standort', 'Location'),
    ('agrar.saatgut.finder.field.boden', 'agrar', 'Bodentyp', 'Soil type'),
    ('agrar.saatgut.finder.field.klima', 'agrar', 'Klima', 'Climate'),
    
    # === AGRAR.DUENGER (Maske 9-10) ===
    # 9. Düngemittelstammdaten
    ('agrar.duenger.stamm.title', 'agrar', 'Düngemittelstammdaten', 'Fertilizer master data'),
    ('agrar.duenger.stamm.section.inhaltsstoffe', 'agrar', 'Inhaltsstoffe', 'Ingredients'),
    ('agrar.duenger.stamm.field.typ', 'agrar', 'Typ', 'Type'),
    ('agrar.duenger.stamm.field.hersteller', 'agrar', 'Hersteller', 'Manufacturer'),
    ('agrar.duenger.stamm.field.npk', 'agrar', 'N-P-K-Verhältnis', 'NPK ratio'),
    
    # 10. Düngemittel-Liste
    ('agrar.duenger.liste.title', 'agrar', 'Düngemittel-Übersicht', 'Fertilizer overview'),
    ('agrar.duenger.liste.filter.typ', 'agrar', 'Typ', 'Type filter'),
    ('agrar.duenger.liste.filter.naehrstoff', 'agrar', 'Nährstoffgehalt', 'Nutrient content filter'),
    ('agrar.duenger.liste.action.duengeplan', 'agrar', 'Düngeplan erstellen', 'Create fertilization plan'),
    
    # === VALIDATION ===
    ('validation.required', 'common', 'Pflichtfeld', 'Required field'),
    ('validation.min_length', 'common', 'Mindestens {{count}} Zeichen', 'Min length validation'),
    ('validation.email', 'common', 'Ungültige E-Mail-Adresse', 'Invalid email'),
    ('validation.number', 'common', 'Muss eine Zahl sein', 'Must be a number'),
    
    # === FIORI PATTERNS ===
    ('pattern.listreport.items_count', 'common', '{{count}} Einträge', 'Items count'),
    ('pattern.listreport.no_data', 'common', 'Keine Daten vorhanden', 'No data'),
    ('pattern.wizard.progress', 'common', 'Schritt {{current}} von {{total}}', 'Wizard progress'),
    ('pattern.objectpage.unsaved_changes', 'common', 'Ungespeicherte Änderungen', 'Unsaved changes warning'),
]

def seed_translations(db):
    """Seed initial German translations"""
    from app.models.translation import create_translation
    
    for key, context, de_value, description in INITIAL_TRANSLATIONS:
        try:
            create_translation(
                db,
                key=key,
                context=context,
                values={'de': de_value},
                description=description
            )
        except Exception as e:
            print(f"Skipping {key}: {e}")
    
    db.commit()
    print(f"✅ {len(INITIAL_TRANSLATIONS)} German translations seeded!")

