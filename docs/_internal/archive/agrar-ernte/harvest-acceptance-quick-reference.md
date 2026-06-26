# Harvest Acceptance - Quick Reference

**Schnellübersicht für Entwickler**

---

## Migration ausführen

```bash
# Aktuellen Stand prüfen
alembic current

# Migration ausführen
alembic upgrade head

# Tabellen prüfen
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptances"
```

---

## API-Endpoints

**Base:** `/api/v1/agrar/harvest-acceptance`

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/` | POST | Erstellen |
| `/` | GET | Liste |
| `/{id}` | GET | Einzelne |
| `/{id}` | PUT | Aktualisieren |
| `/{id}` | DELETE | Löschen |
| `/{id}/derive-nuts2` | POST | NUTS-2 ableiten |
| `/{id}/release` | POST | Freigeben |
| `/{id}/calculate` | POST | Berechnen |

---

## Wichtige Felder

### HarvestAcceptance

- `pricing_mode`: `fixed_contract` | `spot_daily` | `exchange_fix_later`
- `price_source_id`: Referenz zu Preisquelle
- `release_status`: `draft` | `provisional` | `final` | `credit_note_created` | `paid` | `disputed` | `cancelled`

### Validierung

- `pricing_mode == "fixed_contract"` ⇒ `contract_id` required

---

## Neue Tabellen

1. `harvest_acceptance_lines` - Silo/Partie-Splits
2. `supplier_tax_profiles` - Steuerprofile
3. `price_adjustment_rules` - Zu-/Abschläge

---

## Dokumentation

- **Schnellstart:** `harvest-acceptance-README.md`
- **Vollständig:** `harvest-acceptance-final-summary.md`
- **Migration:** `harvest-acceptance-migration-checklist.md`

---

**Stand:** 2026-02-17


