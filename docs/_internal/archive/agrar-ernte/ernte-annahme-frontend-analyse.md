# Ernte-Annahme - Frontend-Integration Analyse

**Datum:** 2026-02-17  
**Basis:** Screenshots "Ernte - Abrechnung.png" und "Ernte Anlieferung.png" (zvoove ERP)

---

## Übersicht

Analyse der Screenshots für die Frontend-Integration der Ernte-Annahme-Eingabemaske. Die Maske folgt dem gleichen Layout-Prinzip wie die Lieferschein-Erfassung (Gewohnheits-Prinzip).

---

## Layout-Struktur (basierend auf Screenshots)

### Hauptbereich (Links)

#### 1. Header-Bereich (Allgemein / Ernte-Abrechnung)

| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Annahmesch.-Nr. | Input + Navigation | Annahmeschein-Nummer (2500274) | `acceptance_number` |
| Niederlassung | Input | Niederlassung (5) | `branch_id` |
| Lagerhalle | Input | Lagerhalle (0) | `warehouse_id` |
| Liefer-Datum | Date + Time | 16.08.2025 11:04 | `delivery_date`, `delivery_time` |
| VB | Input | Verkaufsbeauftragter (TBK) | `sales_rep_id` |
| Bediener | Input | Operator (IS) | `operator_id` |
| Wiegesch.-Nr. | Input + Suche | Wiegeschein-Nummer (5353) | `weighing_ticket_id` |
| Kostenstelle | Input | Kostenstelle | `cost_center_id` |

#### 2. Tabs-Bereich (KUNDE / RECHNUNG / KONTRAKT / SPEDITEUR / NAWARO / ZW-HÄNDLER)

**Tab: KUNDE**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Debitor-Kto. | Input + Suche | Debitor-Konto (160290) | `customer_id` |
| >> wie vorheriger AS (F11) | Checkbox | Wie vorheriger Annahmeschein | (Shortcut F11) |
| Kunden-Stamm | Checkbox | Kunden-Stammdaten öffnen | (Info-Link) |
| Abweichende USTID | Checkbox | Abweichende USt-ID | `deviating_vat_id` |
| Adresse | Text (read-only) | Kundenadresse (aus Stammdaten) | (aus Customer geladen) |

**Tab: RECHNUNG**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| vorl. Rechn.-Nr. | Input | Vorläufige Rechnungs-Nr. | `provisional_invoice_number` |
| Rechnungs-Nr. | Input (read-only) | Rechnungs-Nr. (nach Gutschrift) | `invoice_number` |

**Tab: KONTRAKT**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Kontrakt-Nr. | Input + Suche | Kontrakt-Nummer | `contract_id` |

**Tab: SPEDITEUR**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Spediteur-Kto. | Input + Suche | Spediteur-Konto | `forwarder_id` |

**Tab: NAWARO**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| (Details aus Screenshot nicht vollständig sichtbar) | | | |

**Tab: ZW-HÄNDLER**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Zw-Händler-Kto. | Input + Suche | Zwischenhändler-Konto | `intermediate_dealer_id` |

#### 3. Status-Bereich

| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| vorl. Rechn.-Nr. | Input | Vorläufige Rechnungs-Nr. | `provisional_invoice_number` |
| Rechnungs-Nr. | Input (read-only) | Rechnungs-Nr. (nach Gutschrift) | `invoice_number` |

#### 4. Angaben zur Anlieferung / Abrechnung

**Tab: ANLIEFERUNG**
| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Artikel-Nr. | Input + Suche | Artikel-Nummer (111800) | `article_id` |
| Fahrzeug | Input | Fahrzeug-Kennzeichen (AUR-TK-515) | `vehicle_plate` |
| Bezeichnung | Input (read-only) | Artikel-Bezeichnung | (aus Article geladen) |
| Sorte | Input + Suche | Sorte (245 - Weizen) | `variety_id` |
| Menge | Input + Info | Menge (16.300 kg) | (aus Wiegeschein) |
| MWSt. % | Input (read-only) | 7,00 % MWSt. | `vat_rate_percent` |
| NUTS-2-Code | Input | NUTS-2-Code | `origin_nuts2_code` |
| Nachhaltige Biomasse | Checkbox | Nachhaltige Biomasse | `is_sustainable_biomass` |

**Tab: ABRECHNUNG**
| Spalte | Typ | Beschreibung | Backend-Feld |
|--------|-----|--------------|--------------|
| Pos. | Number | Positionsnummer (10, 15, 20, ...) | `position_number` |
| Bezeichnung | Text | Bezeichnung | `description` |
| drucken | Checkbox | Soll gedruckt werden? | `is_printable` |
| berechnen | Checkbox | Soll berechnet werden? | `is_calculable` |
| Laborwert | Input | Laborwert (%) | `lab_value_pct` |
| Einheit | Text | Einheit (kg, %, kg/hl, etc.) | `unit` |
| Menge | Input | Menge (kg) | `quantity_kg` |
| Preis EUR | Input | Preis EUR | `price_per_unit_eur` |
| Betrag EUR | Input (read-only) | Betrag EUR | `amount_eur` |

**14 Positionen:**
1. **10 - Angelieferte Menge** (16.300 kg, 19,00 EUR, 3.097,00 EUR)
2. **15 - Windabgang** (0,20 %, kg)
3. **20 - Besatz 2% frei** (0,40 %, kg)
4. **30 - Gereinigte Menge** (kg, berechnet)
5. **40 - Feuchte/Tr.verlust** (14,10 %, kg, berechnet)
6. **50 - Zwischenmenge** (kg)
7. **60 - Hektolitergewicht** (78,80 kg/hl)
8. **63 - Lagerschwund** (%, kg, nicht drucken)
9. **65 - Nettogewicht** (kg, berechnet)
10. **70 - Feuchtigkeitsabzug** (14,10 %, kg)
11. **75 - Lagergeld** (Mon., kg, nicht drucken)
12. **78 - Frachtkosten** (kg, berechnet, nicht drucken)
13. **80 - Wiegegebühren** (Euro/St, kg, nicht drucken)
14. **110 - Gutschriftsbetrag** (kg, berechnet)

### Rechter Bereich

#### 1. Labor-Werte Tabelle

| Bezeichnung | Laborwert | Einheit |
|-------------|-----------|---------|
| ► Windabgang | 0,20 | % |
| Besatz | 0,40 | % |
| Feuchte/Tr.verlust | 14,10 | % |
| Hektolitergewicht | 78,80 | kg/hl |
| Lagerschwund | (leer) | % |
| Lagergeld | (leer) | Mon. |
| Wiegegebühren | (leer) | Euro/... |

**Button:** "Import Analysegerät" (Import Analyzer)

#### 2. Bemerkungen

| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Bemerkungen | Textarea | Große Textarea für Bemerkungen | `remarks` |
| Druck Bemerkungen auf: | | | |
| - Annahmeschein | Checkbox | Auf Annahmeschein drucken | `print_remarks_on_acceptance_note` |
| - Abrechnung | Checkbox | Auf Abrechnung drucken | `print_remarks_on_settlement` |

**Button:** "OK"

### Unterer Bereich (Footer)

#### Action Buttons

| Button | Beschreibung | Funktion |
|--------|--------------|----------|
| → Berechnung neu | Berechnung neu durchführen | `POST /{id}/calculate` |
| Abschlagrechnung | Abschlagrechnung erstellen | (TODO) |
| Endabrechnung | Endabrechnung / Gutschrift erstellen | (TODO) |
| Sorte bearbeiten | Sorte bearbeiten | (TODO) |

#### Weitere Actions

| Button | Beschreibung | Funktion |
|--------|--------------|----------|
| Annahmeschein löschen | Löschen (nur Draft) | `DELETE /{id}` |
| Aufteilungs-Buchung | Aufteilungs-Buchung | (TODO: HarvestAcceptanceLine) |
| Unterlagen | Dokumente | (TODO) |
| Dateien | Dateien | (TODO) |
| Zus. Felder | Zusätzliche Felder | (TODO) |

#### Freigabe-Bereich

| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Freigabe | Radio | nein / vorläufig / endgültig | `release_status` |
| Annahmeschein drucken | Link | Annahmeschein drucken | (TODO) |
| Berechnung und Freigabe | Link | Berechnung + Freigabe | `POST /{id}/calculate` + `POST /{id}/release` |

### Rechte Sidebar (Summen)

| Feld | Typ | Beschreibung | Backend-Feld |
|------|-----|--------------|--------------|
| Netto-Betrag | Input (read-only) | Netto-Betrag (EUR) | `total_net_amount_eur` |
| MWSt. % | Input (read-only) | MWSt. % (EUR) | `total_vat_amount_eur` |
| Brutto-Betrag | Input (read-only) | Brutto-Betrag (EUR) | `total_gross_amount_eur` |

**Button:** "OK"

---

## Frontend-Komponenten (basierend auf Lieferschein-Erfassung)

### Layout-Struktur

```tsx
<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
  {/* Linke Spalte (Hauptbereich) */}
  <div className="lg:col-span-2 space-y-4">
    {/* Header-Bereich */}
    <Card>
      <CardHeader>Ernte-Abrechnung</CardHeader>
      <CardContent>
        {/* Annahmesch.-Nr., Niederlassung, etc. */}
      </CardContent>
    </Card>
    
    {/* Tabs: KUNDE, RECHNUNG, KONTRAKT, etc. */}
    <Tabs>
      <TabsList>
        <TabsTrigger value="kunde">KUNDE</TabsTrigger>
        <TabsTrigger value="rechnung">RECHNUNG</TabsTrigger>
        <TabsTrigger value="kontrakt">KONTRAKT</TabsTrigger>
        <TabsTrigger value="spediteur">SPEDITEUR</TabsTrigger>
        <TabsTrigger value="nawaro">NAWARO</TabsTrigger>
        <TabsTrigger value="zw-haendler">ZW-HÄNDLER</TabsTrigger>
      </TabsList>
      <TabsContent value="kunde">
        {/* Kunden-Auswahl */}
      </TabsContent>
      {/* ... weitere Tabs */}
    </Tabs>
    
    {/* ANLIEFERUNG / ABRECHNUNG Tabs */}
    <Tabs>
      <TabsList>
        <TabsTrigger value="anlieferung">ANLIEFERUNG</TabsTrigger>
        <TabsTrigger value="abrechnung">ABRECHNUNG</TabsTrigger>
      </TabsList>
      <TabsContent value="anlieferung">
        {/* Artikel, Fahrzeug, Sorte, etc. */}
      </TabsContent>
      <TabsContent value="abrechnung">
        {/* 14 Positionen Tabelle */}
        <Table>
          {/* Positionen */}
        </Table>
      </TabsContent>
    </Tabs>
  </div>
  
  {/* Rechte Spalte */}
  <div className="space-y-4">
    {/* Labor-Werte */}
    <Card>
      <CardHeader>Labor-Werte</CardHeader>
      <CardContent>
        <Table>
          {/* Laborwerte */}
        </Table>
        <Button>Import Analysegerät</Button>
      </CardContent>
    </Card>
    
    {/* Bemerkungen */}
    <Card>
      <CardHeader>Bemerkungen</CardHeader>
      <CardContent>
        <Textarea />
        <Checkbox>Annahmeschein</Checkbox>
        <Checkbox>Abrechnung</Checkbox>
        <Button>OK</Button>
      </CardContent>
    </Card>
    
    {/* Summen */}
    <Card>
      <CardHeader>Summen</CardHeader>
      <CardContent>
        <Input readOnly>Netto-Betrag</Input>
        <Input readOnly>MWSt. %</Input>
        <Input readOnly>Brutto-Betrag</Input>
        <Button>OK</Button>
      </CardContent>
    </Card>
  </div>
</div>
```

---

## API-Integration

### Endpoints

| Aktion | Endpoint | Method |
|--------|----------|--------|
| Laden | `/api/v1/agrar/harvest-acceptance/{id}` | GET |
| Erstellen | `/api/v1/agrar/harvest-acceptance` | POST |
| Aktualisieren | `/api/v1/agrar/harvest-acceptance/{id}` | PUT |
| Löschen | `/api/v1/agrar/harvest-acceptance/{id}` | DELETE |
| Berechnen | `/api/v1/agrar/harvest-acceptance/{id}/calculate` | POST |
| Freigeben | `/api/v1/agrar/harvest-acceptance/{id}/release` | POST |
| NUTS-2 ableiten | `/api/v1/agrar/harvest-acceptance/{id}/derive-nuts2` | POST |

### Daten-Mapping

**HarvestAcceptanceCreate:**
```typescript
{
  acceptance_number?: string
  branch_id?: string
  warehouse_id?: string
  delivery_date: string // ISO date
  delivery_time?: string // HH:MM
  sales_rep_id?: string
  operator_id: string
  weighing_ticket_id?: string
  cost_center_id?: string
  customer_id: string
  contract_id?: string
  forwarder_id?: string
  intermediate_dealer_id?: string
  deviating_vat_id?: string
  article_id?: string
  variety_id?: string
  vehicle_plate?: string
  origin_nuts2_code?: string
  is_sustainable_biomass: boolean
  pricing_mode: "fixed_contract" | "spot_daily" | "exchange_fix_later"
  price_source_id?: string
  remarks?: string
  print_remarks_on_acceptance_note: boolean
  print_remarks_on_settlement: boolean
  positions?: Array<HarvestAcceptancePositionIn>
}
```

---

## Keyboard Shortcuts (Gewohnheits-Prinzip)

Basierend auf Lieferschein-Erfassung:

| Shortcut | Funktion | Beschreibung |
|----------|----------|-------------|
| `F11` | Wie vorheriger AS | Letzten Annahmeschein übernehmen |
| `Strg+F8` | Wie vorheriger AS (alternativ) | (wie F11) |
| `Strg+S` | Speichern | Ernte-Annahme speichern |
| `Strg+P` | Drucken | Annahmeschein drucken |
| `Strg+B` | Sidebar umschalten | Sidebar ein/ausblenden |
| `Strg+N` | Shortcuts anzeigen | Shortcut-Hilfe |

---

## Dialoge

### 1. Kunden-Auswahl (wie Lieferschein)

- Komponente: `CustomerSelectionDialog` (wiederverwenden)
- API: `/api/v1/crm/customers` (mit Filter)
- Felder: Debitor-Kto., Name, Adresse, Vertreter

### 2. Artikel-Auswahl

- Komponente: `ArtikelSuchDialog` (wiederverwenden)
- API: `/api/v1/inventory/articles` (mit Filter)
- Felder: Artikel-Nr., Bezeichnung, MWSt. %

### 3. Wiegeschein-Auswahl (NEU)

- Komponente: `WeighingTicketSelectionDialog` (neu erstellen)
- API: `/api/v1/agrar/weighing-tickets` (mit Filter)
- Felder: Wiegesch.-Nr., Datum, Netto-Gewicht, Feuchte, Besatz

### 4. Sorte-Auswahl (NEU)

- Komponente: `VarietySelectionDialog` (neu erstellen)
- API: `/api/v1/agrar/varieties` (mit Filter)
- Felder: Sorte-Nr., Bezeichnung

### 5. Kontrakt-Auswahl (NEU)

- Komponente: `ContractSelectionDialog` (neu erstellen)
- API: `/api/v1/agrar/contracts` (mit Filter: customer_id)
- Felder: Kontrakt-Nr., Artikel, Preis, Restmenge

---

## Berechnungslogik

### Automatische Berechnung

1. **Bei Änderung von Laborwerten:**
   - Windabgang, Besatz, Feuchte → Positionen 15, 20, 40 aktualisieren
   - Berechnung neu auslösen

2. **Bei Änderung von Wiegeschein:**
   - Netto-Gewicht → Position 10 (Angelieferte Menge)
   - Feuchte, Besatz → Labor-Werte Tabelle

3. **Bei Klick auf "→ Berechnung neu":**
   - `POST /api/v1/agrar/harvest-acceptance/{id}/calculate`
   - Alle 14 Positionen neu berechnen
   - Summen aktualisieren

### Manuelle Eingabe

- Positionen können manuell bearbeitet werden (falls `is_calculable = false`)
- Laborwerte können manuell eingegeben werden
- Gebühren (Frachtkosten, Wiegegebühren) können manuell eingegeben werden

---

## Validierung

### Client-Side

- `pricing_mode == "fixed_contract"` ⇒ `contract_id` required
- `delivery_date` required
- `customer_id` required
- `weighing_ticket_id` required (für Berechnung)
- `article_id` required (für Berechnung)

### Server-Side

- API-Validierung (Pydantic Models)
- Berechnungsvalidierung (Drying Rule Engine)

---

## Status-Workflow

### Status-Übergänge

```
Draft
  ↓ (Berechnung + Freigabe)
Provisional
  ↓ (Qualitätsfreigabe)
Final
  ↓ (Gutschrift-Erstellung)
Credit Note Created
  ↓ (Zahlung)
Paid
```

### UI-Änderungen je Status

- **Draft:** Alle Felder editierbar, Löschen möglich
- **Provisional:** Felder editierbar, Löschen nicht möglich
- **Final:** Felder read-only (außer Admin)
- **Credit Note Created:** Felder read-only
- **Paid:** Felder read-only

---

## Nächste Schritte

1. **Frontend-Komponente erstellen:**
   - `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`
   - Basierend auf `lieferschein-erfassung.tsx` Struktur

2. **Dialoge erstellen:**
   - `WeighingTicketSelectionDialog`
   - `VarietySelectionDialog`
   - `ContractSelectionDialog`

3. **Routing hinzufügen:**
   - Route: `/agrar/ernte-annahme-erfassung`
   - Route: `/agrar/ernte-annahme-erfassung/:id`

4. **Integration testen:**
   - Erstellen, Bearbeiten, Berechnen, Freigeben

---

**Stand:** 2026-02-17  
**Nächster Schritt:** Frontend-Komponente erstellen


