# Analyse: Kundenstamm-Felder - Überlappung mit bestehender Struktur

## Problem
Es existieren bereits über 250 definierte Kundenstammdatenfelder. Die neu hinzugefügten Sales-Felder könnten Doppelstrukturen erzeugen.

## Bestehende Strukturen

### 1. Feld-Registry: `packages/frontend-web/src/config/l3-customer-field-registry.ts`
- **250+ Felder** definiert
- Strukturiert nach Tabs und Sections
- Beispiele:
  - `customer.group` - Kunden-Gruppe
  - `customer.abc_status` - ABC-/Umsatzstatus
  - `profile.industry_code` - Branche (mit Schlüssel)
  - `analytics.segment` - Segment (im Potential-Tab)

### 2. Mask-Builder Config: `packages/frontend-web/src/config/mask-builder-customer.json`
- Vollständige UI-Konfiguration
- Tabs: masterdata, address, system, tax, quality_compliance, finance, bank, marketing, cooperative, output, interfaces, potential, contacts
- **Bereits vorhanden:**
  - `analytics.segment` (Zeile 1483) - Segment
  - `customer.sales_rep` (Zeile 181) - VB (Außendienst)
  - `profile.industry_code` (Zeile 1046) - Branche (mit Schlüssel)

### 3. Andere Configs
- `mask-builder-valeo-modern.json`: `customer.price_list_id` (Zeile 702) - Preisliste
- `customer_reference.schema.json`: `industry`, `region` bereits vorhanden

## Neu hinzugefügte Felder (SALES-CRM-02)

### In `kunden-stamm.tsx` hinzugefügt:
1. `preisgruppe` → **Mögliche Überlappung:** `customer.group` oder `finance.global.price_determination_mode`
2. `kundenpreisliste` → **Mögliche Überlappung:** `customer.price_list_id` (in valeo-modern.json)
3. `steuerkategorie` → **Neu** (sollte in `tax` Tab)
4. `kundensegment` → **Überlappung:** `analytics.segment` existiert bereits!
5. `branche` → **Überlappung:** `profile.industry_code` existiert bereits!
6. `region` → **Überlappung:** `region` existiert bereits in customer_reference.schema.json

## Empfehlung

### Felder, die bereits existieren (verwenden statt neu erstellen):
1. ✅ **Segment:** `analytics.segment` statt `kundensegment`
2. ✅ **Branche:** `profile.industry_code` statt `branche`
3. ✅ **Region:** `region` (bereits in Schema)
4. ✅ **Preisliste:** `customer.price_list_id` statt `kundenpreisliste`

### Felder, die neu sind (korrekt hinzufügen):
1. ✅ **Preisgruppe:** `sales.price_group` - NEU, sollte in `sales` Tab
2. ✅ **Steuerkategorie:** `tax.category` - NEU, sollte in `tax` Tab

### Integration in bestehende Struktur

**Option A: Bestehende Felder verwenden**
- `analytics.segment` für Kundensegment
- `profile.industry_code` für Branche
- `region` für Region
- `customer.price_list_id` für Preisliste

**Option B: Neue Sales-Felder in bestehende Struktur integrieren**
- `sales.price_group` → Neuer Tab "Sales" oder Section in "finance"
- `tax.category` → Tab "tax", Section "tax_flags"

## Nächste Schritte

1. ✅ Prüfen, welche Felder bereits im Backend existieren
2. ✅ Mapping erstellen: Neue Felder → Bestehende Felder
3. ✅ Code anpassen, um bestehende Felder zu verwenden
4. ✅ Nur wirklich neue Felder hinzufügen
5. ✅ Integration in `mask-builder-customer.json` statt direkter Tab-Erstellung

## Konkrete Aktion

**Statt neue Felder in `kunden-stamm.tsx` zu erstellen:**
- Bestehende Feld-Struktur aus `mask-builder-customer.json` verwenden
- Neue Felder in die JSON-Config integrieren
- Oder: Bestehende Felder verwenden, wenn sie existieren

