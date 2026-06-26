# Ernte-Annahme - "Wie vorheriger AS" (F11) Implementierung

**Datum:** 2026-02-17  
**Status:** ✅ Implementiert

---

## Übersicht

Die "Wie vorheriger AS" Funktionalität ermöglicht es, alle Daten vom letzten Annahmeschein zu übernehmen, um eine neue Ernte-Annahme schnell zu erstellen.

---

## Backend-Implementierung

### Endpoint

**GET** `/api/v1/agrar/harvest-acceptance/last`

**Query-Parameter:**
- `operator_id` (optional): Filter nach Operator-ID (Benutzer, der die Ernte-Annahme erstellt hat)
- `customer_id` (optional): Filter nach Kunde

**Response:**
- `HarvestAcceptanceOut | null`: Die letzte Ernte-Annahme oder `null`, wenn keine gefunden wurde

**Implementierung:**
```python
@router.get("/last", response_model=Optional[HarvestAcceptanceOut])
async def get_last_harvest_acceptance(
    operator_id: Optional[str] = Query(None, description="Filter nach Operator-ID"),
    customer_id: Optional[str] = Query(None, description="Filter nach Kunde"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Holt die letzte Ernte-Annahme für einen Benutzer/Kunde."""
    query = db.query(HarvestAcceptance).filter(HarvestAcceptance.tenant_id == tenant_id)
    
    if operator_id:
        query = query.filter(HarvestAcceptance.operator_id == operator_id)
    
    if customer_id:
        query = query.filter(HarvestAcceptance.customer_id == customer_id)
    
    acceptance = query.order_by(HarvestAcceptance.created_at.desc()).first()
    
    if not acceptance:
        return None
    
    return _harvest_acceptance_to_dict_with_positions(acceptance, db)
```

**Datei:** `app/api/v1/endpoints/harvest_acceptance.py`

---

## Frontend-Implementierung

### Keyboard Shortcuts

- **F11**: Wie vorheriger Annahmeschein
- **Strg+F8**: Wie vorheriger Annahmeschein (alternativ)

### Funktion

**`handleCopyPreviousFull()`**

**Ablauf:**
1. GET Request zu `/api/v1/agrar/harvest-acceptance/last` mit `operator_id` und optional `customer_id`
2. Wenn keine Ernte-Annahme gefunden: Fehlermeldung
3. Kunde separat laden (falls vorhanden)
4. Alle Daten übernehmen:
   - Header-Felder (Niederlassung, Lagerhalle, Datum, Zeit, etc.)
   - Kunde
   - Kontrakt, Spediteur, Zwischenhändler
   - Artikel, Sorte, Fahrzeug
   - NUTS-2 Daten
   - Bemerkungen
   - Positionen (alle 14 Positionen)
   - Laborwerte (aus Positionen extrahiert)
5. **NICHT übernommen:**
   - `id` → `null` (neue Ernte-Annahme)
   - `acceptance_number` → `''` (wird vom Backend generiert)
   - `weighing_ticket_id` → `null` (muss neu ausgewählt werden)
   - `release_status` → `'draft'` (immer Draft für neue Ernte-Annahme)
   - `provisional_invoice_number` → `''`
   - `invoice_number` → `''`
   - Summen → `null` (werden neu berechnet)

**Datei:** `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`

---

## Verhalten

### Übernommene Daten

✅ **Header:**
- Niederlassung (`branch_id`)
- Lagerhalle (`warehouse_id`)
- Liefer-Datum (`delivery_date`) - aktuelles Datum
- Liefer-Zeit (`delivery_time`) - aktuelle Zeit
- Verkaufsbeauftragter (`sales_rep_id`)
- Kostenstelle (`cost_center_id`)

✅ **Kunde:**
- Vollständige Kundendaten (wird separat geladen)

✅ **Vertrag & Partner:**
- Kontrakt (`contract_id`)
- Spediteur (`forwarder_id`)
- Zwischenhändler (`intermediate_dealer_id`)
- Abweichende USt-ID (`deviating_vat_id`)

✅ **Anlieferung:**
- Artikel (`article_id`)
- Sorte (`variety_id`)
- Fahrzeug-Kennzeichen (`vehicle_plate`)
- NUTS-2 Daten (`origin_nuts2_code`, `origin_postal_code`, etc.)
- Nachhaltige Biomasse (`is_sustainable_biomass`)

✅ **Preisermittlung:**
- Preismodell (`pricing_mode`)
- Preisquelle (`price_source_id`)

✅ **Bemerkungen:**
- Bemerkungen (`remarks`)
- Druck-Optionen (`print_remarks_on_acceptance_note`, `print_remarks_on_settlement`)

✅ **Positionen:**
- Alle 14 Positionen mit Werten

✅ **Laborwerte:**
- Windabgang (aus Position 15)
- Besatz (aus Position 20)
- Feuchte (aus Position 40)
- Hektolitergewicht (aus Position 60)
- Lagerschwund (aus Position 63)
- Lagergeld (aus Position 75)
- Wiegegebühren (aus Position 80)

### Nicht übernommene Daten

❌ **ID & Nummer:**
- `id` → `null` (neue Ernte-Annahme)
- `acceptance_number` → `''` (wird generiert)

❌ **Wiegeschein:**
- `weighing_ticket_id` → `null` (muss neu ausgewählt werden)

❌ **Status:**
- `release_status` → `'draft'` (immer Draft)

❌ **Rechnung:**
- `provisional_invoice_number` → `''`
- `invoice_number` → `''`

❌ **Summen:**
- `total_net_amount_eur` → `null`
- `total_vat_amount_eur` → `null`
- `total_gross_amount_eur` → `null`
- (werden bei Berechnung neu berechnet)

---

## Test-Szenario

1. **Vorbereitung:**
   - Erstelle eine Ernte-Annahme mit allen Feldern
   - Speichere sie

2. **Test:**
   - Öffne neue Ernte-Annahme (`/agrar/ernte-annahme-erfassung`)
   - Drücke **F11** oder **Strg+F8**
   - ✅ Erwartung: Alle Daten werden übernommen (außer ID, Nummer, Wiegeschein, Status, Rechnung, Summen)

3. **Verifikation:**
   - Prüfe, dass alle Felder korrekt gefüllt sind
   - Prüfe, dass Positionen übernommen wurden
   - Prüfe, dass Laborwerte korrekt extrahiert wurden
   - Prüfe, dass `id` und `acceptance_number` leer sind
   - Prüfe, dass `release_status` auf `'draft'` steht

---

## Bekannte Einschränkungen

1. **Artikel-Bezeichnung:**
   - `articleName` wird nicht automatisch geladen
   - TODO: Aus Artikel-Stammdaten laden

2. **Wiegeschein:**
   - Muss manuell neu ausgewählt werden
   - Dies ist beabsichtigt, da jeder Annahmeschein einen eigenen Wiegeschein hat

---

**Stand:** 2026-02-17  
**Status:** ✅ Vollständig implementiert


