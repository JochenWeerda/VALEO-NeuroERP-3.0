# Harvest Acceptance - Migration-Checkliste

**Datum:** 2026-02-17  
**Status:** ✅ Bereit für Migration

---

## Pre-Migration Checkliste

### ✅ Code-Qualität

- [x] Alle Python-Dateien kompilieren ohne Fehler
- [x] Linter-Prüfung durchgeführt (keine Fehler)
- [x] Migration-Syntax geprüft (beide Migrationen)
- [x] Modelle korrekt definiert und registriert
- [x] API-Endpoints vollständig implementiert
- [x] Validierung implementiert

### ✅ Datenbank-Modelle

- [x] `HarvestAcceptance` - Hauptbeleg
- [x] `HarvestAcceptancePosition` - Abrechnungs-Positionen
- [x] `HarvestAcceptanceLine` - Silo/Partie-Splits (NEU)
- [x] `SupplierTaxProfile` - Steuerprofile (NEU)
- [x] `PriceAdjustmentRule` - Zu-/Abschläge (NEU)
- [x] Alle Modelle in `__init__.py` importiert

### ✅ Migrationen

- [x] `b38680c2f581_add_harvest_acceptance_with_nuts2_20260217.py` (Basis)
- [x] `c4d5e6f7a8b9_add_harvest_acceptance_extensions_20260217.py` (Erweiterungen)
- [x] Beide Migrationen haben `upgrade()` und `downgrade()`
- [x] `down_revision` korrekt gesetzt
- [x] Syntax geprüft (Python AST)

### ✅ API-Endpoints

- [x] `POST /api/v1/agrar/harvest-acceptance` - Erstellen
- [x] `GET /api/v1/agrar/harvest-acceptance` - Liste
- [x] `GET /api/v1/agrar/harvest-acceptance/{id}` - Einzelne
- [x] `PUT /api/v1/agrar/harvest-acceptance/{id}` - Aktualisieren
- [x] `DELETE /api/v1/agrar/harvest-acceptance/{id}` - Löschen
- [x] `POST /api/v1/agrar/harvest-acceptance/{id}/derive-nuts2` - NUTS-2 ableiten
- [x] `POST /api/v1/agrar/harvest-acceptance/{id}/release` - Freigeben
- [x] `POST /api/v1/agrar/harvest-acceptance/{id}/calculate` - Berechnen
- [x] Pydantic Models erweitert (`pricing_mode`, `price_source_id`)
- [x] Validierung implementiert

### ✅ Dokumentation

- [x] `harvest-acceptance-README.md` - Schnellstart
- [x] `harvest-acceptance-implementation-summary.md` - Übersicht
- [x] `harvest-acceptance-nuts2.md` - NUTS-2 Details
- [x] `harvest-acceptance-extensions-summary.md` - Erweiterungen
- [x] `harvest-acceptance-commit-summary.md` - Commit-Vorbereitung
- [x] `harvest-acceptance-final-summary.md` - Finale Zusammenfassung
- [x] `harvest-acceptance-migration-checklist.md` - Diese Datei
- [x] `ernte-annahme-pruefung-fragen.md` - Aktualisiert

---

## Migration-Schritte

### 1. Backup erstellen (empfohlen)

```bash
# PostgreSQL Backup
pg_dump -U postgres -d neuroerp -F c -f backup_pre_harvest_acceptance_$(date +%Y%m%d_%H%M%S).dump
```

### 2. Aktuellen Stand prüfen

```bash
# Prüfe aktuelle Revision
alembic current

# Prüfe Migration-Status
alembic history
```

**Erwartete letzte Revision vor Migration:**
- `agrar_drying_rules_audit_contract_dms_20260217` (oder später)

### 3. Migration ausführen

```bash
# Migration ausführen
alembic upgrade head

# Oder spezifisch
alembic upgrade c4d5e6f7a8b9
```

**Erwartete Ausgabe:**
```
INFO  [alembic.runtime.migration] Running upgrade <previous> -> b38680c2f581, add_harvest_acceptance_with_nuts2_20260217
INFO  [alembic.runtime.migration] Running upgrade b38680c2f581 -> c4d5e6f7a8b9, add_harvest_acceptance_extensions_20260217
```

### 4. Tabellen prüfen

```bash
# Prüfe Tabellen existieren
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptances"
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptance_positions"
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptance_lines"
psql -d neuroerp -c "\dt domain_crm.supplier_tax_profiles"
psql -d neuroerp -c "\dt domain_inventory.price_adjustment_rules"
```

**Erwartete Ausgabe:**
- Alle 5 Tabellen sollten existieren

### 5. Spalten prüfen

```bash
# Prüfe HarvestAcceptance Spalten
psql -d neuroerp -c "\d domain_inventory.harvest_acceptances" | grep -E "(pricing_mode|price_source_id)"
```

**Erwartete Ausgabe:**
- `pricing_mode` sollte existieren (default: 'spot_daily')
- `price_source_id` sollte existieren (nullable)

### 6. Indizes prüfen

```bash
# Prüfe Indizes
psql -d neuroerp -c "\di domain_inventory.*harvest_acceptance*"
psql -d neuroerp -c "\di domain_crm.*supplier_tax*"
psql -d neuroerp -c "\di domain_inventory.*price_adjustment*"
```

**Erwartete Indizes:**
- `ix_harvest_acceptance_lines_acceptance`
- `ix_supplier_tax_profiles_supplier_valid`
- `ix_price_adjustment_rules_article_valid`

---

## Post-Migration Checkliste

### ✅ Datenbank-Verifikation

- [ ] Alle Tabellen existieren
- [ ] Alle Spalten vorhanden
- [ ] Alle Indizes erstellt
- [ ] Foreign Keys korrekt
- [ ] Constraints vorhanden

### ✅ API-Tests

- [ ] Backend-Container läuft
- [ ] API erreichbar
- [ ] `POST /api/v1/agrar/harvest-acceptance` funktioniert
- [ ] `GET /api/v1/agrar/harvest-acceptance` funktioniert
- [ ] `POST /api/v1/agrar/harvest-acceptance/{id}/calculate` funktioniert
- [ ] `POST /api/v1/agrar/harvest-acceptance/{id}/release` funktioniert

### ✅ Funktionalität

- [ ] Ernte-Annahme kann angelegt werden
- [ ] `pricing_mode` wird gespeichert
- [ ] `price_source_id` wird gespeichert
- [ ] Berechnung funktioniert
- [ ] Freigabe funktioniert
- [ ] Stock Movement wird erstellt (bei Freigabe)

---

## Rollback-Plan

Falls Probleme auftreten:

```bash
# Rollback zur vorherigen Revision
alembic downgrade -1

# Oder spezifisch
alembic downgrade b38680c2f581
```

**Warnung:** Rollback löscht alle Daten in den neuen Tabellen!

---

## Bekannte Einschränkungen / TODOs

### Nicht Teil dieser Migration:

1. **Tagespreis-API:** Für dynamische Preise (Vertrag > Tagespreis > Artikel)
2. **Gutschrift-Erstellung:** Self-Billing Workflow mit E-Rechnung
3. **Frontend-Integration:** Eingabemaske für Ernte-Annahme
4. **Vollständige PLZ → NUTS-2-Zuordnungstabelle:** Eurostat correspondence tables
5. **API-Endpoints für neue Modelle:** CRUD für HarvestAcceptanceLine, SupplierTaxProfile, PriceAdjustmentRule
6. **Berechnungslogik erweitern:** Integration von PriceAdjustmentRule, Windabgang-Modus, Besatz-Regel-Engine

### Placeholder / TODO im Code:

- `derive_nuts2_from_postal_code()`: Placeholder-Implementierung (TODO: vollständige Zuordnungstabelle)
- `exchange_fix_later`: TODO: pricing_fixation_status + Referenz auf Börsen/Indexdaten
- `daily_prices` Tabelle: TODO: Tagespreis-API implementieren

---

## Support & Troubleshooting

### Häufige Probleme

**Problem:** Migration schlägt fehl mit "relation already exists"
- **Lösung:** Prüfe, ob Tabellen bereits existieren. Falls ja, prüfe ob Migration bereits ausgeführt wurde.

**Problem:** Foreign Key Constraint fehlt
- **Lösung:** Prüfe, ob referenzierte Tabellen existieren (z.B. `business_partners`, `articles`).

**Problem:** `pricing_mode` Default-Wert wird nicht gesetzt
- **Lösung:** Prüfe `server_default` in Migration. Sollte `"spot_daily"` sein.

### Logs prüfen

```bash
# Backend-Logs
docker logs valeo-neuro-erp-backend --tail 100

# Alembic-Logs
# (sollten in der Migration-Ausgabe sichtbar sein)
```

---

## Erfolgskriterien

✅ **Migration erfolgreich, wenn:**
- Alle Tabellen existieren
- Alle Spalten vorhanden
- Alle Indizes erstellt
- API-Endpoints funktionieren
- Keine Fehler in Logs

---

**Stand:** 2026-02-17  
**Nächster Schritt:** Migration ausführen


