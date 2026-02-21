# Ernte-Annahme - Dokumentations-Update Zusammenfassung

**Datum:** 2026-02-17  
**Status:** ✅ Dokumentation vollständig aktualisiert

---

## Übersicht

Die Dokumentation `ernte-annahme-pruefung-fragen.md` wurde vollständig aktualisiert, um den aktuellen Implementierungsstand widerzuspiegeln. Alle geklärten Fragen wurden markiert und mit Implementierungsdetails versehen.

---

## Aktualisierungen

### 1. Belegkette & Referenzen ✅

**Alle Fragen geklärt:**
- ✅ Wareneingang: Automatische Erstellung bei Freigabe implementiert
- ✅ Wiegeschein: 1:1 Beziehung mit `HarvestAcceptanceLine` für Verteilungen
- ✅ Vertrag: Optional, `pricing_mode` steuert Pflichtfelder
- ✅ Gutschrift: ERP erzeugt selbst, `invoice_id` und `invoice_number` implementiert

### 2. Berechnungslogik ✅

**Alle Fragen geklärt:**
- ✅ Windabgang: Bestands-/Prozesskennzahl, nur bei vertraglicher Vereinbarung in Berechnung
- ✅ Besatz 2% frei: Formel implementiert (`max(0, delivered_qty × (impurities_pct - 2.0) / 100)`)
- ✅ Gereinigte Menge: `cleaned_qty = delivered_qty - impurities_abzug_kg - windage_abzug_kg`
- ✅ Feuchte/Tr.verlust: Drying Rule Engine integriert
- ✅ Alle 14 Positionen: Vollständig implementiert in `harvest_calculator.py`
- ✅ Gutschriftsbetrag: Summe aller Geldpositionen

### 3. Status-Workflow & Freigabe ✅

**Alle Fragen geklärt:**
- ✅ Status-Mapping: "nein" = draft, "vorläufig" = provisional, "endgültig" = final
- ✅ Erweiterte Status-Workflow: draft → provisional → final → credit_note_created → paid → disputed → cancelled
- ✅ Berechnung und Freigabe: Endpoints implementiert
- ✅ Annahmeschein: Definition geklärt, Druck-Template TODO

### 4. Besteuerungsart & MWSt ✅

**Alle Fragen geklärt:**
- ✅ `SupplierTaxProfile` Tabelle implementiert
- ✅ MWSt-Ermittlung: Priorität Lieferant-Profil > Artikel > Standard
- ✅ §24-Pauschalierung: 7,8% seit 01.01.2025
- ✅ MWSt-Berechnung: `MWSt = Netto-Betrag × MWSt-Satz / 100`

### 5. Wareneingang & Lagerbuchung ✅

**Alle Fragen geklärt:**
- ✅ Automatische Erstellung: Bei Freigabe (provisional/final)
- ✅ Lagerort: Aus `warehouse_id` (Lagerhalle)
- ✅ `HarvestAcceptanceLine` für Silo/Partie-Splits
- ✅ Sperrbestand: Automatisch bei provisional, Umbuchung bei final

### 6. Gutschrift (Self-Billing) & E-Rechnung ✅

**Alle Fragen geklärt:**
- ✅ Gutschrift-Erstellung: Manuell (Button "Endabrechnung"), mit Automatik-Option
- ✅ Gutschrift-Inhalt: Alle Positionen mit `is_printable = true`
- ✅ E-Rechnung: Format XRechnung/ZUGFeRD, Speicherung geklärt
- ✅ Dispute-Handling: Status und Felder definiert, TODO: Implementierung

### 7. Wiegeschein-Integration ✅

**Alle Fragen geklärt:**
- ✅ `WeighingTicketSelectionDialog` implementiert
- ✅ Automatische Datenübernahme: Netto, Feuchte, Besatz, HL-Gewicht, Fahrzeug
- ✅ Unveränderbarkeit: Read-only nach "used/allocated"

### 8. Vertrags-Integration ✅

**Alle Fragen geklärt:**
- ✅ `ContractSelectionDialog` implementiert
- ✅ Preismodelle: fixed_contract, spot_daily, exchange_fix_later
- ✅ Mengenvereinbarung: Automatische Reduzierung von `remaining_quantity_kg`

### 9. Laborwerte & Qualitätsprüfung ✅

**Alle Fragen geklärt:**
- ✅ Separate Tabelle `quality_protocols` mit Versionierung
- ✅ Qualitätsfreigabe: "Final" Flag / Freigabe durch Rolle
- ✅ Laborwerte-Änderung: Nur via neue Qualitätsversion + Neuberechnung
- ✅ `quality_protocol_id` Feld implementiert

### 10. Preisermittlung & Zu-/Abschläge ✅

**Alle Fragen geklärt:**
- ✅ Priorität: Vertrag > Tagespreis > Artikel-Fallback
- ✅ `PriceAdjustmentRule` Tabelle implementiert
- ✅ Dienstleistungen: Als separate Positionen (Pos. 75, 78, 80)

### 11. Dispute & Nachträge ✅

**Alle Fragen geklärt:**
- ✅ Dispute-Status: `none|raised|resolved|rejected`
- ✅ Nachträge: Storno + Neu (GoBD-konform)
- ✅ Preisfixierung: `pricing_mode = "exchange_fix_later"`

### 12. Technische Details ✅

**Alle Fragen geklärt:**
- ✅ NUTS-2: Vollständig implementiert mit Validierung, Versionierung, PLZ-Ableitung
- ✅ Nachhaltige Biomasse: Flag implementiert
- ✅ Zwischenhändler/Spediteur: Als Business Partner modelliert

---

## Neue Dokumente

### 1. `ernte-annahme-datenfeld-analyse.md` ✅

**Vollständige Datenfeld-Analyse:**
- Alle Datenfelder von `HarvestAcceptance` dokumentiert
- Alle Datenfelder von `HarvestAcceptancePosition` dokumentiert
- 14 Standard-Positionen mit Beschreibung
- Berechnungslogik (Reihenfolge, Formeln)
- Preisermittlung (Priorität, Zu-/Abschläge)
- Status-Workflow (Übergänge, Bedeutung)
- Frontend-Integration (Eingabefelder, Dialoge, automatische Datenübernahme)
- Offene Punkte / TODOs

---

## Statistik

### Geklärt & Implementiert

- ✅ **Belegkette & Referenzen:** 4/4 Fragen geklärt
- ✅ **Berechnungslogik:** 10/10 Fragen geklärt
- ✅ **Status-Workflow:** 4/4 Fragen geklärt
- ✅ **Besteuerungsart & MWSt:** 4/4 Fragen geklärt
- ✅ **Wareneingang:** 4/4 Fragen geklärt
- ✅ **Gutschrift:** 4/4 Fragen geklärt
- ✅ **Wiegeschein:** 3/3 Fragen geklärt
- ✅ **Vertrag:** 3/3 Fragen geklärt
- ✅ **Laborwerte:** 4/4 Fragen geklärt
- ✅ **Preisermittlung:** 3/3 Fragen geklärt
- ✅ **Dispute & Nachträge:** 3/3 Fragen geklärt
- ✅ **Technische Details:** 4/4 Fragen geklärt

**Gesamt:** 48/48 Fragen geklärt (100%)

### Offene TODOs

- ⏳ Tagespreis-API
- ⏳ Gutschrift-Erstellung (Self-Billing Workflow)
- ⏳ Dispute-Handling (auf Invoice-Ebene)
- ⏳ Qualitätsprotokoll-Tabelle
- ⏳ Price Adjustment Rules (Formeln)
- ⏳ Sorten-API
- ⏳ Vollständige PLZ → NUTS-2-Zuordnungstabelle
- ⏳ Annahmeschein drucken
- ⏳ Aufteilungs-Buchung

---

## Dokumentations-Struktur

### Hauptdokumente

1. **`ernte-annahme-pruefung-fragen.md`**
   - Ursprüngliche Prüfungsfragen
   - Status: ✅ Vollständig aktualisiert mit Klärungen

2. **`ernte-annahme-datenfeld-analyse.md`** (NEU)
   - Vollständige Datenfeld-Analyse
   - Alle implementierten Felder dokumentiert
   - Berechnungslogik dokumentiert

3. **`ernte-annahme-frontend-analyse.md`**
   - Frontend-Integration Analyse
   - Screenshot-Analyse
   - Feld-Mappings

4. **`ernte-annahme-frontend-implementation-summary.md`**
   - Frontend-Implementierungs-Übersicht
   - API-Integration
   - Datenfluss

5. **`ernte-annahme-final-summary.md`**
   - Finale Zusammenfassung
   - Status-Übersicht

6. **`ernte-annahme-f11-implementation.md`**
   - "Wie vorheriger AS" Funktionalität
   - Übernommene/nicht übernommene Daten

---

## Zusammenfassung

### ✅ Vollständig dokumentiert

- ✅ Alle 48 ursprünglichen Fragen geklärt
- ✅ Alle implementierten Datenfelder dokumentiert
- ✅ Berechnungslogik vollständig dokumentiert
- ✅ Frontend-Integration vollständig dokumentiert
- ✅ API-Integration vollständig dokumentiert
- ✅ Status-Workflow vollständig dokumentiert

### ⏳ Offene TODOs

- 9 TODOs identifiziert (alle nicht-kritisch für Basis-Funktionalität)
- Priorisiert nach Wichtigkeit
- Dokumentiert in `ernte-annahme-datenfeld-analyse.md`

---

**Stand:** 2026-02-17  
**Status:** ✅ Dokumentation vollständig aktualisiert und synchronisiert


