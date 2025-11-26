***REMOVED*** SALES-CRM-02: Feld-Integration abgeschlossen

***REMOVED******REMOVED*** Datum: 2025-01-24

***REMOVED******REMOVED*** Problem
6 neue Sales-Felder wurden hinzugefügt, aber es existieren bereits 250+ definierte Kundenstammdatenfelder. Doppelstrukturen mussten vermieden werden.

***REMOVED******REMOVED*** Analyse-Ergebnis
**4 von 6 Feldern existieren bereits:**
- `kundensegment` → `analytics.segment` (Frontend) + `customer_segment` (Backend)
- `branche` → `profile.industry_code` (Frontend) + `industry` (Backend)
- `region` → `region` (crm-core)
- `kundenpreisliste` → `customer.price_list_id` (valeo-modern.json)

**2 Felder sind wirklich neu:**
- `preisgruppe` → `sales.price_group` (NEU)
- `steuerkategorie` → `tax.category` (NEU)

***REMOVED******REMOVED*** Durchgeführte Änderungen

***REMOVED******REMOVED******REMOVED*** 1. Frontend (`kunden-stamm.tsx`)

**Zod-Schema angepasst:**
- ❌ Entfernt: `kundensegment`, `branche`, `region`, `kundenpreisliste`
- ✅ Behalten: `preisgruppe`, `steuerkategorie`

**Tab-Struktur angepasst:**
- ❌ Sales-Tab entfernt
- ✅ `preisgruppe` → in "konditionen" Tab verschoben
- ✅ `steuerkategorie` → in "steuern" Tab verschoben

**Kommentare hinzugefügt:**
- Dokumentation, welche bestehenden Felder verwendet werden sollen

***REMOVED******REMOVED******REMOVED*** 2. Backend (`app/domains/crm/models.py`)

**Nur neue Felder hinzugefügt:**
```python
price_group = Column(String(50))  ***REMOVED*** NEU: sales.price_group
tax_category = Column(String(50))  ***REMOVED*** NEU: tax.category
```

**Kommentare hinzugefügt:**
- Dokumentation, welche bestehenden Felder über Mapping verwendet werden

***REMOVED******REMOVED******REMOVED*** 3. API-Schemas (`app/api/v1/schemas/crm.py`)

**Neue Felder in allen Schemas hinzugefügt:**
- `CustomerBase`: `price_group`, `tax_category`
- `CustomerCreate`: `price_group`, `tax_category`
- `CustomerUpdate`: `price_group`, `tax_category`
- `Customer`: `price_group`, `tax_category`

***REMOVED******REMOVED******REMOVED*** 4. Migration (`migrations/sql/crm/003_add_sales_fields_to_customers.sql`)

**Erstellt:**
- Migration für `domain_crm.crm_customers` Tabelle
- Nur `price_group` und `tax_category` hinzugefügt
- Indizes erstellt
- Kommentare hinzugefügt

***REMOVED******REMOVED*** Mapping-Tabelle

| Frontend (kunden-stamm.tsx) | Bestehendes Feld | Tab | Status |
|------------------------------|------------------|-----|--------|
| `kundensegment` | `analytics.segment` | potential | ✅ Verwende bestehendes |
| `branche` | `profile.industry_code` | marketing | ✅ Verwende bestehendes |
| `region` | `region` | - | ✅ Verwende bestehendes (crm-core) |
| `kundenpreisliste` | `customer.price_list_id` | finance | ✅ Verwende bestehendes |
| `preisgruppe` | `sales.price_group` | konditionen | ✅ NEU hinzugefügt |
| `steuerkategorie` | `tax.category` | steuern | ✅ NEU hinzugefügt |

***REMOVED******REMOVED*** Nächste Schritte

1. **Mapping-Logik implementieren:**
   - API-Endpoint erweitern, um bestehende Felder zu mappen
   - Frontend-Backend-Mapping dokumentieren

2. **Tests:**
   - Unit-Tests für neue Felder
   - Integration-Tests für Mapping

3. **Dokumentation:**
   - Feld-Mapping-Tabelle in README
   - Entscheidungsgrundlage dokumentieren

***REMOVED******REMOVED*** Status
✅ **Abgeschlossen**: Doppelstrukturen vermieden, nur neue Felder hinzugefügt

