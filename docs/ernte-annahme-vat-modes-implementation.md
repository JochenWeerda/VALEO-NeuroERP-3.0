# Ernte-Annahme - VAT/Steuer-Modi Implementierung

**Datum:** 2026-02-17  
**Status:** ✅ Implementiert

---

## Übersicht

Erweiterte VAT/Steuer-Modi für Ernte-Annahme, um verschiedene Geschäftsmodelle und Vorsteuerabzug-Logik sauber abzubilden.

---

## Geschäftsmodelle (Acceptance Modes)

### 1. STORAGE_ONLY (Fremdware, keine Vorsteuer)

**Beschreibung:**
- Ware bleibt im Eigentum des Landwirts (Konsignations-/Einlagerlogik)
- Keine Ankaufgutschrift (und damit i. d. R. kein Vorsteuerabzug)
- Später bei "Vereinnahmung/Ankauf": dann erst Abrechnung + Gutschrift + Vorsteuer

**ERP-Abbildung:**
- `ownership_type = "THIRD_PARTY_STOCK"`
- `vat_event = "NO_INVOICE"`
- Wareneingang als **Fremdware** → Subledger **STORAGE**

**Vorsteuerabzug:**
- ❌ Nicht möglich (keine Lieferung an euch)

---

### 2. PURCHASE_AT_DELIVERY_PTBF (Ankauf jetzt, Preis später, Vorsteuer möglich)

**Beschreibung:**
- Bei der Ernteannahme geht **wirtschaftliches Eigentum/Verfügungsmacht** (umsatzsteuerlich: Lieferung) schon auf euch über
- Der Preis kann **später** fixiert werden (PTBF / Preisvereinbarung später)
- Ihr erstellt eine **(vorläufige) Self-Billing-Gutschrift** direkt zur Anlieferung

**ERP-Abbildung:**
- `ownership_type = "OWN_STOCK"`
- `vat_event = "PROVISIONAL_CREDIT_NOTE_CREATED"` → später `"FINAL_CREDIT_NOTE_CREATED"`
- Wareneingang als **Eigene Ware** → Subledger **AP / PRODUCER_CLEARING**

**Vorsteuerabzug:**
- ✅ Möglich (Leistungsbezug + ordnungsgemäße Rechnung/Gutschrift)
- Vorläufige Gutschrift mit geschätztem Preis möglich
- Spätere Korrektur als **Korrekturbeleg** (nicht stilles Überschreiben)

---

### 3. ADVANCE_ON_STORAGE (Einlagerung + Abschlag/Anzahlung)

**Beschreibung:**
- Echte Einlagerung (Fremdware), aber mit **Anzahlung** (z. B. Ernteabschlag)
- Anzahlungsrechnung/-gutschrift wird erstellt
- Vorsteuerabzug aus der Anzahlung grundsätzlich **erst nach Zahlung** möglich

**ERP-Abbildung:**
- `ownership_type = "THIRD_PARTY_STOCK"`
- `vat_event = "PROVISIONAL_CREDIT_NOTE_CREATED"` (nach Zahlung)
- Wareneingang als **Fremdware** → Subledger **STORAGE**
- Anzahlung → Subledger **AP / ADVANCE_PAYMENTS**

**Vorsteuerabzug:**
- ✅ Möglich, aber **nur nach Zahlung** der Anzahlung
- Anzahlungsgutschrift wird erstellt, aber Vorsteuerabzug erst nach Zahlung

---

## Datenbank-Erweiterungen

### Neue Felder in `harvest_acceptances`

- `acceptance_mode` (String, 30): Geschäftsmodell
- `ownership_type` (String, 20): Eigentumsverhältnis
- `vat_event` (String, 40): VAT-Ereignis
- `advance_payment_amount_eur` (DECIMAL): Anzahlungsbetrag
- `advance_payment_date` (Date): Anzahlungsdatum
- `advance_invoice_id` (String, FK): Referenz auf Anzahlungsgutschrift

### Indizes

- `ix_harvest_acceptances_acceptance_mode`
- `ix_harvest_acceptances_vat_event`

---

## VAT Service

**Datei:** `modules/agrar/services/vat_service.py`

### Funktionen

1. **`determine_ownership_type()`**
   - Bestimmt `ownership_type` basierend auf `acceptance_mode`

2. **`can_create_credit_note_for_vat()`**
   - Prüft, ob eine Gutschrift für Vorsteuerabzug erstellt werden kann

3. **`create_provisional_credit_note()`**
   - Erstellt vorläufige Self-Billing Gutschrift (für PURCHASE_AT_DELIVERY_PTBF)

4. **`create_advance_payment_credit_note()`**
   - Erstellt Anzahlungsgutschrift (für ADVANCE_ON_STORAGE)

5. **`create_correction_credit_note()`**
   - Erstellt Korrekturgutschrift (für Preisänderungen)

---

## §24-Pauschalierung

**Durchschnittssatz seit 01.01.2025: 7,8%**

- Automatische Erkennung über `SupplierTaxProfile.taxation_type = "ustg24_flat_rate"`
- MWSt-Satz wird automatisch auf 7,8% gesetzt
- Versionierte Steuerregel (jährlich änderbar)

---

## API-Änderungen

### Harvest Acceptance API

#### POST `/` (Erstellen)

- Neue Felder in `HarvestAcceptanceCreate`:
  - `acceptance_mode` (optional, default: `PURCHASE_AT_DELIVERY_PTBF`)
  - `ownership_type` (optional, wird automatisch bestimmt)
  - `vat_event` (optional, default: `NO_INVOICE`)
  - `advance_payment_amount_eur` (optional)
  - `advance_payment_date` (optional)

#### POST `/{acceptance_id}/release` (Freigabe)

- Automatische Logik basierend auf `acceptance_mode`:
  - `STORAGE_ONLY`: Keine Gutschrift
  - `PURCHASE_AT_DELIVERY_PTBF`: Vorläufige oder finale Gutschrift
  - `ADVANCE_ON_STORAGE`: Anzahlungsgutschrift (nur nach Zahlung)

---

## Workflow-Beispiele

### Beispiel 1: PURCHASE_AT_DELIVERY_PTBF

1. Ernte-Annahme erstellen (`acceptance_mode = "PURCHASE_AT_DELIVERY_PTBF"`)
2. Qualitätsprotokoll erfassen
3. Berechnung durchführen (vorläufiger Preis)
4. Freigabe mit `create_credit_note=true`
   - → Vorläufige Gutschrift wird erstellt
   - → `vat_event = "PROVISIONAL_CREDIT_NOTE_CREATED"`
   - → Vorsteuerabzug möglich
5. Später: Preis fixiert
6. Korrekturgutschrift erstellen (falls Preisänderung)
   - → `vat_event = "CORRECTION_ISSUED"`

### Beispiel 2: ADVANCE_ON_STORAGE

1. Ernte-Annahme erstellen (`acceptance_mode = "ADVANCE_ON_STORAGE"`)
2. Anzahlungsbetrag und -datum setzen
3. Anzahlung zahlen
4. Freigabe mit `create_credit_note=true`
   - → Anzahlungsgutschrift wird erstellt
   - → `vat_event = "PROVISIONAL_CREDIT_NOTE_CREATED"`
   - → Vorsteuerabzug **erst nach Zahlung** möglich

### Beispiel 3: STORAGE_ONLY

1. Ernte-Annahme erstellen (`acceptance_mode = "STORAGE_ONLY"`)
2. Wareneingang als Fremdware
3. Keine Gutschrift (keine Vorsteuer)
4. Später: Bei "Vereinnahmung/Ankauf" → dann erst Gutschrift

---

## Migration

**Datei:** `alembic/versions/add_harvest_acceptance_vat_modes_20260217.py`

```bash
alembic upgrade head
```

---

## Nächste Schritte

1. ⏳ **Subledger-Integration:**
   - AP / PRODUCER_CLEARING
   - SETTLEMENT/VERRECHNUNG
   - STORAGE (Fremdware)
   - ADVANCE_PAYMENTS

2. ⏳ **Korrekturbeleg-Logik:**
   - Automatische Erstellung bei Preisänderungen
   - Storno + Neu vs. Korrekturgutschrift

3. ⏳ **Zahlungs-Integration:**
   - Verknüpfung Zahlung → Vorsteuerabzug (für ADVANCE_ON_STORAGE)

---

## Dateien

### Migration

- ✅ `alembic/versions/add_harvest_acceptance_vat_modes_20260217.py`

### Services

- ✅ `modules/agrar/services/vat_service.py`

### Modelle

- ✅ `app/infrastructure/models/l3c_models.py` (HarvestAcceptance erweitert)

### API

- ✅ `app/api/v1/endpoints/harvest_acceptance.py` (erweitert)

### Dokumentation

- ✅ `docs/ernte-annahme-vat-modes-implementation.md` (dieses Dokument)

---

**Stand:** 2026-02-17  
**Status:** ✅ VAT/Steuer-Modi implementiert, bereit für Migration


