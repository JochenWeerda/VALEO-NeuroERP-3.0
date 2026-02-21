# Harvest Acceptance - Commit-Zusammenfassung

**Datum:** 2026-02-17  
**Branch:** `feature/harvest-acceptance` (oder main, je nach Workflow)  
**Status:** ✅ Ready for Commit & Migration

---

## Übersicht

Vollständige Backend-Implementierung der Ernte-Annahme-Maske (Harvest Acceptance) für den Landhandel mit NUTS-2-Unterstützung, Berechnungslogik, Drying Rule Engine Integration und automatischer Wareneingang-Erstellung.

---

## Geänderte/Neue Dateien

### Neue Dateien

1. **`app/infrastructure/models/l3c_models.py`**
   - `HarvestAcceptance` Model (Hauptbeleg)
   - `HarvestAcceptancePosition` Model (14 Abrechnungs-Positionen)

2. **`alembic/versions/b38680c2f581_add_harvest_acceptance_with_nuts2_20260217.py`**
   - Migration für `harvest_acceptances` und `harvest_acceptance_positions` Tabellen

3. **`app/api/v1/endpoints/harvest_acceptance.py`**
   - 8 API-Endpoints (CRUD + Berechnung + Freigabe + NUTS-2-Ableitung)

4. **`modules/agrar/services/harvest_calculator.py`**
   - Berechnungslogik für alle 14 Abrechnungs-Positionen
   - Drying Rule Engine Integration

5. **`docs/harvest-acceptance-README.md`**
   - Vollständige README mit Schnellstart, API-Referenz, Architektur

6. **`docs/harvest-acceptance-implementation-summary.md`**
   - Detaillierte Implementierungs-Zusammenfassung

7. **`docs/harvest-acceptance-nuts2.md`**
   - NUTS-2-Dokumentation

### Geänderte Dateien

1. **`app/infrastructure/models/__init__.py`**
   - Import von `HarvestAcceptance`, `HarvestAcceptancePosition` hinzugefügt

2. **`app/api/v1/api.py`**
   - Router für `harvest_acceptance` hinzugefügt

3. **`app/api/v1/endpoints/__init__.py`**
   - Import von `harvest_acceptance` hinzugefügt

4. **`docs/ernte-annahme-pruefung-fragen.md`**
   - Implementierungsstatus aktualisiert
   - Offene Fragen als geklärt markiert

---

## Datenbank-Änderungen

### Neue Tabellen

1. **`domain_inventory.harvest_acceptances`**
   - 40+ Spalten (Header, Kunde, Anlieferung, NUTS-2, Status, Summen)
   - Foreign Keys zu: tenants, branches, warehouses, weighing_tickets, customers, agrar_contracts, business_partners, articles, inventory_stock_movements
   - Indizes: `uq_harvest_acceptances_tenant_number`, `ix_harvest_acceptances_customer`, `ix_harvest_acceptances_weighing_ticket`, `ix_harvest_acceptances_nuts2`

2. **`domain_inventory.harvest_acceptance_positions`**
   - 15+ Spalten (Position, Berechnung, NUTS-2 pro Position)
   - Foreign Keys zu: harvest_acceptances, articles
   - Indizes: `ix_harvest_acceptance_positions_acceptance`, `ix_harvest_acceptance_positions_nuts2`

### Migration-Reihenfolge

```
agrar_drying_rules_20260217
  ↓
agrar_drying_rules_audit_contract_dms_20260217
  ↓
b38680c2f581_add_harvest_acceptance_with_nuts2_20260217  ← NEU
```

---

## API-Endpoints

**Base Path:** `/api/v1/agrar/harvest-acceptance`

| Method | Endpoint | Beschreibung | Auth |
|--------|----------|--------------|------|
| `POST` | `/` | Ernte-Annahme anlegen | ✅ |
| `GET` | `/` | Liste (mit Filtern) | ✅ |
| `GET` | `/{acceptance_id}` | Einzelne Ernte-Annahme | ✅ |
| `PUT` | `/{acceptance_id}` | Aktualisieren (nur Draft/Provisional) | ✅ |
| `DELETE` | `/{acceptance_id}` | Löschen (nur Admin, nur Draft) | ✅ Admin |
| `POST` | `/{acceptance_id}/derive-nuts2` | NUTS-2 aus PLZ ableiten | ✅ |
| `POST` | `/{acceptance_id}/release` | Freigeben (provisional/final) | ✅ |
| `POST` | `/{acceptance_id}/calculate` | Berechnung durchführen | ✅ |

---

## Features

### ✅ Implementiert

- Vollständiges CRUD für Ernte-Annahmen
- 14 Abrechnungs-Positionen automatisch berechnet
- Drying Rule Engine Integration (automatisch, mit Fallback)
- NUTS-2-Unterstützung (Herkunft/Region der Erzeugung)
- Automatische Wareneingang-Erstellung bei Freigabe
- Preisermittlung (Vertrag > Artikel, mit `price_source` Tracking)
- Status-Workflow (Draft → Provisional → Final)
- Audit-Trail (calculation_formula für jede Position)
- Warnungen-System (systematische Sammlung und Rückgabe)

### ⏳ TODO (nicht Teil dieses Commits)

- Tagespreis-API für dynamische Preise
- Gutschrift-Erstellung (Self-Billing Workflow)
- Qualitätsprotokoll-Integration
- Frontend-Integration
- Vollständige PLZ → NUTS-2-Zuordnungstabelle (Eurostat)

---

## Testing

### Vor Migration

```bash
# Syntax-Prüfung
python -m compileall app/infrastructure/models/l3c_models.py
python -m compileall app/api/v1/endpoints/harvest_acceptance.py
python -m compileall modules/agrar/services/harvest_calculator.py

# Linter-Prüfung
# (bereits durchgeführt, keine Fehler)
```

### Nach Migration

```bash
# Migration ausführen
alembic upgrade head

# Tabellen prüfen
psql -d neuroerp -c "\d domain_inventory.harvest_acceptances"
psql -d neuroerp -c "\d domain_inventory.harvest_acceptance_positions"

# API testen
curl -X POST http://localhost:8000/api/v1/agrar/harvest-acceptance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"customer_id": "...", "delivery_date": "2025-02-17"}'
```

---

## Breaking Changes

**Keine** - Dies ist eine neue Funktionalität, keine Änderungen an bestehenden APIs.

---

## Dependencies

- Bestehende Dependencies (keine neuen)
- Nutzt vorhandene Models: `WeighingTicket`, `Customer`, `Article`, `AgrarContract`, `Warehouse`, `StockMovement`
- Nutzt vorhandene Services: `drying_rule_engine.py`, `settlement_calculator.py`

---

## Rollback

Falls Rollback notwendig:

```bash
# Migration rückgängig machen
alembic downgrade -1

# Oder spezifisch
alembic downgrade agrar_drying_rules_audit_contract_dms_20260217
```

---

## Commit-Message (Vorschlag)

```
feat(agrar): Implementiere Harvest Acceptance (Ernte-Annahme) Backend

- DB-Modelle: HarvestAcceptance, HarvestAcceptancePosition mit NUTS-2
- Migration: b38680c2f581_add_harvest_acceptance_with_nuts2_20260217
- API-Endpoints: CRUD + Berechnung + Freigabe (8 Endpoints)
- Berechnungslogik: 14 Abrechnungs-Positionen automatisch berechnet
- Drying Rule Engine Integration: Automatische Feuchte-Berechnung
- NUTS-2-Unterstützung: Herkunft/Region der Erzeugung für RED-II/ISCC
- Automatische Wareneingang-Erstellung bei Freigabe
- Preisermittlung: Vertrag > Artikel (mit price_source Tracking)
- Vollständige Dokumentation: README, Implementation Summary, NUTS-2 Docs

Features:
- Status-Workflow: Draft → Provisional → Final
- Audit-Trail: calculation_formula für jede Position
- Warnungen-System: Systematische Sammlung und Rückgabe
- Mischladungen: NUTS-2 pro Position unterstützt

TODO (nicht Teil dieses Commits):
- Tagespreis-API für dynamische Preise
- Gutschrift-Erstellung (Self-Billing Workflow)
- Frontend-Integration

Closes: #XXX (falls vorhanden)
```

---

## Checkliste vor Commit

- [x] Alle Dateien kompiliert (keine Syntax-Fehler)
- [x] Linter-Prüfung durchgeführt (keine Fehler)
- [x] Migration getestet (Syntax korrekt)
- [x] Dokumentation vollständig
- [x] API-Endpoints dokumentiert
- [x] Breaking Changes dokumentiert (keine)
- [x] Dependencies geprüft (keine neuen)
- [ ] Migration ausgeführt (nach Commit)
- [ ] API-Endpoints getestet (nach Migration)

---

**Stand:** 2026-02-17  
**Bereit für:** Commit & Migration


