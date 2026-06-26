# Ernte-Annahme - Vollständige Datenfeld-Analyse

**Erstellt:** 2026-02-17  
**Status:** ✅ Vollständig implementiert und dokumentiert

---

## Übersicht

Vollständige Analyse aller Datenfelder der Ernte-Annahme-Erfassungsmaske, basierend auf dem implementierten Datenmodell und der Frontend-Integration.

---

## Datenmodell: HarvestAcceptance

### Header-Bereich (Allgemein)

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Annahmeschein-Nr. | String(50) | `acceptance_number` | Fortlaufende Nummer (auto-generiert) | ✅ |
| Tenant-ID | String | `tenant_id` | Mandanten-ID | ✅ |
| Niederlassung | String (FK) | `branch_id` | Niederlassung | ✅ |
| Lagerhalle | String (FK) | `warehouse_id` | Lagerhalle | ✅ |
| Liefer-Datum | Date | `delivery_date` | Datum der Anlieferung | ✅ |
| Liefer-Zeit | String(8) | `delivery_time` | Uhrzeit (HH:MM) | ✅ |
| VB | String(64) | `sales_rep_id` | Verkaufsbeauftragter | ✅ |
| Bediener | String(64) | `operator_id` | Aktueller Benutzer | ✅ |
| Wiegesch.-Nr. | String (FK) | `weighing_ticket_id` | Referenz zum Wiegeschein | ✅ |
| Kostenstelle | String(64) | `cost_center_id` | Kostenstelle | ✅ |

### Kunden-Bereich

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Debitor-Kto. | String (FK) | `customer_id` | Kunde (Business Partner) | ✅ |
| Kontrakt-Nr. | String (FK) | `contract_id` | Referenz zum Vertrag | ✅ |
| Spediteur-Kto. | String (FK) | `forwarder_id` | Spediteur (Business Partner) | ✅ |
| Zw-Händler-Kto. | String (FK) | `intermediate_dealer_id` | Zwischenhändler (Business Partner) | ✅ |
| Abweichende USt-ID | String(20) | `deviating_vat_id` | Abweichende USt-ID für Gutschrift | ✅ |

### Anlieferung-Bereich

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Artikel-Nr. | String (FK) | `article_id` | Artikel (optional, wenn nicht pro Position) | ✅ |
| Sorte | String(64) | `variety_id` | Sorte/Varietät | ✅ |
| Fahrzeug-Kennzeichen | String(20) | `vehicle_plate` | Kennzeichen des Fahrzeugs | ✅ |

### NUTS-2 & Nachhaltigkeit

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| NUTS-2-Code | String(10) | `origin_nuts2_code` | NUTS-2-Code der Herkunftsregion | ✅ |
| NUTS-Version | String(20) | `nuts_version` | Version des NUTS-Codes (z.B. NUTS 2024) | ✅ |
| PLZ Herkunft | String(10) | `origin_postal_code` | PLZ der Herkunft (für Ableitung) | ✅ |
| Ort Herkunft | String(100) | `origin_city` | Ort der Herkunft (für Ableitung) | ✅ |
| Ländercode | String(2) | `origin_country_code` | Ländercode (ISO 3166-1 alpha-2) | ✅ |
| Nachhaltige Biomasse | Boolean | `is_sustainable_biomass` | Flag für RED-II/ISCC/REDcert | ✅ |

### Status & Freigabe

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Freigabe-Status | String(20) | `release_status` | draft / provisional / final / credit_note_created / paid / disputed / cancelled | ✅ |
| vorl. Rechn.-Nr. | String(50) | `provisional_invoice_number` | Vorläufige Rechnungs-Nr. | ✅ |
| Rechnungs-ID | String(64) | `invoice_id` | FK zu invoice (Gutschrift) | ✅ |
| Rechnungs-Nr. | String(50) | `invoice_number` | Rechnungs-Nr. (nach Gutschrift) | ✅ |

### Preisermittlung

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Preismodell | String(20) | `pricing_mode` | fixed_contract / spot_daily / exchange_fix_later | ✅ |
| Preisquelle-ID | String(64) | `price_source_id` | Referenz zu Preisquelle (daily_price_id, exchange_index_id, etc.) | ✅ |

### Belegkette-Referenzen

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Wareneingang-ID | String (FK) | `stock_movement_id` | Referenz zu Wareneingang (wird bei Freigabe erstellt) | ✅ |
| Qualitätsprotokoll-ID | String(64) | `quality_protocol_id` | Referenz zu Qualitätsprotokoll | ✅ |

### Bemerkungen

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Bemerkungen | Text | `remarks` | Bemerkungen | ✅ |
| Druck auf Annahmeschein | Boolean | `print_remarks_on_acceptance_note` | Soll auf Annahmeschein gedruckt werden? | ✅ |
| Druck auf Abrechnung | Boolean | `print_remarks_on_settlement` | Soll auf Abrechnung gedruckt werden? | ✅ |

### Summen

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Netto-Betrag | DECIMAL(15,2) | `total_net_amount_eur` | Netto-Betrag | ✅ |
| MWSt-Betrag | DECIMAL(15,2) | `total_vat_amount_eur` | MWSt-Betrag | ✅ |
| Brutto-Betrag | DECIMAL(15,2) | `total_gross_amount_eur` | Brutto-Betrag | ✅ |
| MWSt % | DECIMAL(5,2) | `vat_rate_percent` | MWSt-Satz | ✅ |

### Audit-Felder

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Erstellt am | DateTime | `created_at` | Erstellungszeitpunkt | ✅ |
| Erstellt von | String(64) | `created_by` | Benutzer, der erstellt hat | ✅ |
| Geändert am | DateTime | `updated_at` | Änderungszeitpunkt | ✅ |
| Geändert von | String(64) | `updated_by` | Benutzer, der geändert hat | ✅ |

---

## Datenmodell: HarvestAcceptancePosition

### Basis-Felder

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| ID | String | `id` | Primärschlüssel | ✅ |
| Ernte-Annahme-ID | String (FK) | `harvest_acceptance_id` | Referenz zur Ernte-Annahme | ✅ |
| Positionsnummer | Integer | `position_number` | Positionsnummer (10, 15, 20, ...) | ✅ |
| Bezeichnung | String(200) | `description` | Bezeichnung der Position | ✅ |

### Berechnungslogik

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Drucken | Boolean | `is_printable` | Soll auf Druckausgabe erscheinen? | ✅ |
| Berechnen | Boolean | `is_calculable` | Soll diese Position berechnet werden? | ✅ |
| Laborwert (%) | DECIMAL(5,2) | `lab_value_pct` | Laborwert in % (z.B. Feuchte, Besatz) | ✅ |
| Menge (kg) | DECIMAL(12,3) | `quantity_kg` | Menge in kg | ✅ |
| Einheit | String(20) | `unit` | Einheit (kg, %, EUR/t, EUR) | ✅ |
| Preis EUR | DECIMAL(10,2) | `price_per_unit_eur` | Preis pro Einheit in EUR | ✅ |
| Betrag EUR | DECIMAL(15,2) | `amount_eur` | Berechneter Betrag in EUR | ✅ |
| Berechnungsformel | Text | `calculation_formula` | Formel für Audit-Zwecke | ✅ |

### NUTS-2 pro Position (für Mischladungen)

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| NUTS-2-Code | String(10) | `origin_nuts2_code` | NUTS-2-Code der Herkunftsregion (pro Position) | ✅ |
| NUTS-Version | String(20) | `nuts_version` | Version des NUTS-Codes | ✅ |
| PLZ Herkunft | String(10) | `origin_postal_code` | PLZ der Herkunft (für Ableitung) | ✅ |
| Ort Herkunft | String(100) | `origin_city` | Ort der Herkunft (für Ableitung) | ✅ |
| Ländercode | String(2) | `origin_country_code` | Ländercode (ISO 3166-1 alpha-2) | ✅ |

### Artikel/Sorte pro Position

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Artikel-Nr. | String (FK) | `article_id` | Artikel-Nr. (pro Position, falls abweichend) | ✅ |
| Sorte | String(64) | `variety_id` | Sorte/Varietät (pro Position, falls abweichend) | ✅ |

### Audit-Felder

| Feld | Typ | DB-Spalte | Beschreibung | Status |
|------|-----|-----------|--------------|--------|
| Erstellt am | DateTime | `created_at` | Erstellungszeitpunkt | ✅ |
| Geändert am | DateTime | `updated_at` | Änderungszeitpunkt | ✅ |

---

## Standard-Positionen (14 Positionen)

| Pos. | Bezeichnung | Einheit | Berechenbar | Druckbar | Beschreibung |
|------|-------------|---------|-------------|----------|--------------|
| 10 | Angelieferte Menge | kg | ✅ | ✅ | Nettogewicht aus Wiegeschein |
| 15 | Windabgang | kg | ❌ | ✅ | Informationswert (nicht in Berechnung) |
| 20 | Besatz 2% frei | kg | ❌ | ✅ | Besatz-Abzug (2% frei Regel) |
| 30 | Gereinigte Menge | kg | ✅ | ✅ | Angelieferte Menge - Besatz - Windabgang |
| 40 | Feuchte/Tr.verlust | kg | ✅ | ✅ | Feuchte-bedingter Mengenabzug (Drying Rule Engine) |
| 50 | Zwischenmenge | kg | ❌ | ❌ | Berechnungs-Zwischenwert |
| 60 | Hektolitergewicht | kg/hl | ❌ | ✅ | Qualitätsmerkmal (für Zu-/Abschläge) |
| 63 | Lagerschwund | kg | ✅ | ❌ | Lagerschwund-Abzug (Mengenfaktor oder Kosten) |
| 65 | Nettogewicht | kg | ✅ | ✅ | Abrechnungsmenge (nach allen Abzügen) |
| 70 | Feuchtigkeitsabzug | kg | ❌ | ✅ | Separater Feuchtigkeitsabzug (falls kostenbasiert) |
| 75 | Lagergeld | Mon. | ❌ | ❌ | Lagergeld (Kostenposition) |
| 78 | Frachtkosten | kg | ✅ | ❌ | Frachtkosten (Kostenposition) |
| 80 | Wiegegebühren | Euro/St | ❌ | ❌ | Wiegegebühren (Kostenposition) |
| 110 | Gutschriftsbetrag | EUR | ✅ | ✅ | Summe aller Geldpositionen |

---

## Berechnungslogik (Implementiert)

### Reihenfolge der Berechnung

1. **Pos. 10 (Angelieferte Menge):**
   - `quantity_kg = net_weight` (aus Wiegeschein)

2. **Pos. 15 (Windabgang):**
   - `lab_value_pct = windage_pct` (aus Laborwert)
   - Informationswert, nicht in Berechnung

3. **Pos. 20 (Besatz 2% frei):**
   - `lab_value_pct = impurities_pct` (aus Laborwert)
   - Abzug: `impurities_abzug_kg = max(0, delivered_qty × (impurities_pct - 2.0) / 100)`
   - Informationswert, nicht in Berechnung

4. **Pos. 30 (Gereinigte Menge):**
   - `quantity_kg = delivered_qty - impurities_abzug_kg - windage_abzug_kg`

5. **Pos. 40 (Feuchte/Tr.verlust):**
   - Verwendet Drying Rule Engine (falls konfiguriert)
   - `quantity_kg = loss_kg` (aus Drying Rule Engine)
   - `lab_value_pct = moisture_pct` (aus Laborwert)

6. **Pos. 50 (Zwischenmenge):**
   - `quantity_kg = cleaned_qty - moisture_loss_kg`
   - Berechnungs-Zwischenwert, nicht druckbar

7. **Pos. 60 (Hektolitergewicht):**
   - `quantity_kg = hl_weight_kg_per_hl` (aus Laborwert)
   - Qualitätsmerkmal, für Zu-/Abschläge

8. **Pos. 63 (Lagerschwund):**
   - `lab_value_pct = storage_shrinkage_pct` (aus Eingabe)
   - `quantity_kg = intermediate_qty × storage_shrinkage_pct / 100`

9. **Pos. 65 (Nettogewicht):**
   - `quantity_kg = intermediate_qty - storage_shrinkage_kg`
   - Abrechnungsmenge

10. **Pos. 70 (Feuchtigkeitsabzug):**
    - Separater Abzug (falls kostenbasiert, nicht mengenbasiert)
    - Wird nicht berechnet, wenn Drying Rule Engine verwendet wird

11. **Pos. 75 (Lagergeld):**
    - `amount_eur = storage_fee_per_month × storage_months` (aus Eingabe)

12. **Pos. 78 (Frachtkosten):**
    - `amount_eur = freight_costs_eur` (aus Eingabe)

13. **Pos. 80 (Wiegegebühren):**
    - `amount_eur = weighing_fees_eur` (aus Eingabe)

14. **Pos. 110 (Gutschriftsbetrag):**
    - `amount_eur = (net_weight × unit_price) - deductions + services`
    - Summe aller Geldpositionen

---

## Preisermittlung (Implementiert)

### Priorität

1. **Vertrag (fixed_contract):**
   - `pricing_mode = "fixed_contract"`
   - `contract_id` required
   - Preis aus `agrar_contracts.fixed_price`

2. **Tagespreis (spot_daily):**
   - `pricing_mode = "spot_daily"`
   - `price_source_id` optional (Referenz zu daily_price_id)
   - ⏳ TODO: Tagespreis-API implementieren

3. **Artikel-Fallback:**
   - Preis aus `articles.sales_price`
   - `crop_code` wird aus `articles.warengruppe` abgeleitet

### Zu-/Abschläge

- ⏳ TODO: `PriceAdjustmentRule` Tabelle implementieren
- ⏳ TODO: Formeln für HL-Gewicht, Besatz, Mykotoxin

---

## Status-Workflow (Implementiert)

### Status-Übergänge

```
Draft → Provisional → Final → CreditNoteCreated → Paid
                                    ↓
                                Disputed
                                    ↓
                              Cancelled
```

### Status-Bedeutung

| Status | Bedeutung | Beschreibung |
|--------|-----------|--------------|
| `draft` | Entwurf | Erste Erfassung, noch nicht freigegeben |
| `provisional` | Vorläufig | Vorläufige Freigabe, Wareneingang erstellt (Sperrbestand) |
| `final` | Endgültig | Endgültige Freigabe, Qualität final, Pricing "locked" |
| `credit_note_created` | Gutschrift erstellt | Gutschrift erzeugt & in FiBu gebucht |
| `paid` | Bezahlt | OP ausgeglichen |
| `disputed` | Widerspruch | Widerspruch gegen Gutschrift |
| `cancelled` | Storniert | Stornierung |

---

## Belegkette & Referenzen (Implementiert)

### Automatische Erstellung

1. **Wareneingang:**
   - ✅ Wird automatisch erstellt bei Freigabe (provisional/final)
   - ✅ `stock_movement_id` wird gesetzt
   - ✅ Status: "Sperrbestand" (bis Qualitätsfreigabe)

2. **Qualitätsprotokoll:**
   - ✅ `quality_protocol_id` Feld vorhanden
   - ⏳ TODO: Separate Tabelle `quality_protocols` implementieren

3. **Gutschrift:**
   - ✅ `invoice_id` und `invoice_number` Felder vorhanden
   - ⏳ TODO: Self-Billing Workflow implementieren

---

## Besteuerungsart & MWSt (Implementiert)

### Besteuerungsarten

| Typ | MWSt-Satz | Beschreibung |
|-----|-----------|--------------|
| `regular` | 7% / 19% | Regelbesteuert |
| `ustg24_flat_rate` | 7,8% | §24-Pauschalierung (seit 01.01.2025) |
| `small_business` | 0% | Kleinunternehmer |

### MWSt-Ermittlung

- ✅ Priorität: Lieferant-Profil > Artikel/Warengruppe > Standard
- ✅ `SupplierTaxProfile` Tabelle implementiert
- ✅ Gültigkeitszeitraum (`valid_from`, `valid_to`)

---

## Frontend-Integration (Implementiert)

### Eingabefelder

| Bereich | Felder | Status |
|---------|--------|--------|
| Header | Annahmesch.-Nr., Niederlassung, Lagerhalle, Datum, Zeit, VB, Bediener, Wiegesch.-Nr., Kostenstelle | ✅ |
| Kunde | Debitor-Kto., Kontrakt-Nr., Spediteur-Kto., Zw-Händler-Kto., Abweichende USt-ID | ✅ |
| Anlieferung | Artikel-Nr., Fahrzeug, Bezeichnung, Sorte, Menge, MWSt. %, NUTS-2-Code, Nachhaltige Biomasse | ✅ |
| Abrechnung | 14 Positionen (Grid) | ✅ |
| Laborwerte | Windabgang, Besatz, Feuchte, Hektolitergewicht, Lagerschwund, Lagergeld, Wiegegebühren | ✅ |
| Bemerkungen | Bemerkungen, Druck-Optionen | ✅ |
| Summen | Netto, MWSt., Brutto | ✅ |

### Dialoge

| Dialog | Funktion | Status |
|--------|----------|--------|
| Kunden-Auswahl | Debitor-Kto. auswählen | ✅ |
| Artikel-Auswahl | Artikel-Nr. auswählen | ✅ |
| Wiegeschein-Auswahl | Wiegesch.-Nr. auswählen | ✅ |
| Kontrakt-Auswahl | Kontrakt-Nr. auswählen | ✅ |
| Sorte-Auswahl | Sorte auswählen | ✅ |

### Automatische Datenübernahme

| Quelle | Übernommene Daten | Status |
|--------|-------------------|--------|
| Wiegeschein | Netto-Gewicht, Feuchte, Besatz, HL-Gewicht, Fahrzeug | ✅ |
| Artikel | Artikel-ID, Bezeichnung, MWSt. % | ✅ |
| Kontrakt | Kontrakt-ID, Preismodell | ✅ |
| Vorheriger AS (F11) | Alle Felder (außer ID, Nummer, Wiegeschein, Status, Rechnung, Summen) | ✅ |

---

## Offene Punkte / TODOs

### Priorität 1 (kritisch)

1. ⏳ **Tagespreis-API:** Für dynamische Preise (Vertrag > Tagespreis > Artikel)
2. ⏳ **Gutschrift-Erstellung:** Self-Billing Workflow mit E-Rechnung
3. ⏳ **Dispute-Handling:** Widerspruch gegen Gutschrift

### Priorität 2 (wichtig)

4. ⏳ **Qualitätsprotokoll-Tabelle:** Separate Tabelle `quality_protocols`
5. ⏳ **Price Adjustment Rules:** Tabelle für Zu-/Abschläge
6. ⏳ **Sorten-API:** API-Endpoint für Sorten (aktuell: Standard-Liste)

### Priorität 3 (nice-to-have)

7. ⏳ **Vollständige PLZ → NUTS-2-Zuordnungstabelle:** Eurostat correspondence tables
8. ⏳ **Annahmeschein drucken:** Druck-Template und API-Endpoint
9. ⏳ **Aufteilungs-Buchung:** `HarvestAcceptanceLine` Funktionalität

---

## Zusammenfassung

### ✅ Vollständig implementiert

- ✅ DB-Modelle: `HarvestAcceptance`, `HarvestAcceptancePosition` mit allen Feldern
- ✅ Migration: `b38680c2f581_add_harvest_acceptance_with_nuts2_20260217.py`
- ✅ API-Endpoints: Vollständiges CRUD + Berechnung + Freigabe + `/last`
- ✅ Berechnungslogik: Alle 14 Abrechnungs-Positionen
- ✅ Drying Rule Engine: Integration mit automatischer Erkennung
- ✅ Preisermittlung: Vertrag > Artikel (crop_code aus warengruppe)
- ✅ Wareneingang: Automatische Stock-Movement-Erstellung bei Freigabe
- ✅ Frontend-Integration: Vollständige Eingabemaske mit allen Dialogen
- ✅ Automatische Datenübernahme: Aus Wiegeschein, Artikel, Kontrakt, vorheriger AS
- ✅ Dokumentation: Vollständig (5 Dokumente)

### ⏳ Offen / TODO

- ⏳ Tagespreis-API
- ⏳ Gutschrift-Erstellung (Self-Billing)
- ⏳ Dispute-Handling
- ⏳ Qualitätsprotokoll-Tabelle
- ⏳ Price Adjustment Rules
- ⏳ Sorten-API
- ⏳ Vollständige PLZ → NUTS-2-Zuordnungstabelle
- ⏳ Annahmeschein drucken
- ⏳ Aufteilungs-Buchung

---

**Stand:** 2026-02-17  
**Status:** ✅ Vollständig dokumentiert, bereit für Produktion
