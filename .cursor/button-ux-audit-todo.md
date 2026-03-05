# Button- & UX-Audit: Diskrepanzen, Workflow-Lücken, Mock-Daten

**Zuletzt aktualisiert:** 2025-03-05 (Alle offenen Punkte: M9, M11–M15 als erledigt; E4 Bestellung→Lieferschein, F18 Scan-Dialog, F1 Priorität; A6/A12 Auge/Stift; siehe docs/GAP-UND-TODO-INDEX.md)

Erstellt aus paralleler Code-Analyse der Module Verkauf, Einkauf, Agrar, Fibu/Finance/Lager/Admin/POS/Annahme.
**Hinweis:** Laufzeitprüfung (tatsächliches Klicken) wurde nicht durchgeführt; Angaben basieren auf Code-Analyse.

---

## 1. Diskrepanzen: Button-Beschriftung vs. tatsächliche Reaktion

### Modul Verkauf

| # | Fundstelle | Button/Label | Erwartung (Beschriftung) | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|---------------------------|------------------------|-----------|
| V1 | `verkauf/lieferschein-erfassung.tsx` ~1256,1259,1262 | MoreHorizontal, ChevronLeft, ChevronRight (Lieferschein-Nr.) | Lieferschein wechseln/suchen, vor/zurück | **Erledigt:** Dialog „Lieferschein suchen“, Prev/Next laden Liste und navigieren | – |
| V2 | `verkauf/lieferschein-erfassung.tsx` ~1356,1363 | MoreHorizontal (Niederlassung, Vertreter) | Auswahl Niederlassung/Vertreter | **Erledigt:** Niederlassung aus Branches-API, Vertreter-Dialog mit Eingabe | – |
| V3 | `verkauf/lieferschein-erfassung.tsx` | PopUp, Details (Position) | Zusatzinfos/Details zur Position | **Erledigt:** Dialoge mit Positions-Zusatzinfos bzw. erweiterte Felder | – |
| V4 | `verkauf/lieferschein-erfassung.tsx` ~1976 | Kontrakte | Kontrakte anzeigen/verknüpfen | **Erledigt:** navigate zu /contracts?customerId=… | – |
| V5 | `verkauf/lieferschein-erfassung.tsx` ~1980 | Connect Anwendungen | Schnittstelle (z. B. Waage) | **Erledigt:** navigate zu /waage + Toast | – |
| V6 | `verkauf/lieferschein-erfassung.tsx` ~1984,1192 | Sofort-Rechnung | Rechnung aus Lieferschein erzeugen | **Erledigt:** `handleCreateInvoice` ruft Docflow convert auf; Button ~2183 | – |
| V7 | `sales/order-editor.tsx` ~480,524 | ChevronLeft/Right, MoreHorizontal (Niederlassung/Vertreter) | Vor/Zurück, Auswahl | **Erledigt:** Auftrag-Auswahl navigiert zu Beleg; Prev/Next; Niederlassung/Vertreter-Dialoge wie Lieferschein | – |
| V8 | `sales/order-editor.tsx` ~897,906 | Kontrakte, Sofort-Rechnung | Kontrakte / Rechnung aus Auftrag | **Erledigt (Toast):** Kontrakte + Sofort-Rechnung mit onClick und Hinweis/Anleitung | – |
| V9 | `sales/angebot-erstellen.tsx` ~326,428,436,438,444 | Chevron; Speichern; In Auftrag wandeln; Löschen; Beenden | Navigation; Speichern; Auftrag erzeugen; Löschen; Schließen | **Erledigt:** handleSave, handleConvertToOrder, handleDelete, handleBeenden an Buttons gebunden | – |
| V10 | `sales/angebot-erstellen.tsx` | Zeile bearbeiten (bei aktivem Index) | Position ersetzen | **Erledigt:** handlePositionOK ersetzt bei aktivePositionIndex die Zeile in der Liste | – |

### Modul Einkauf

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| E1 | `einkauf/bestellungen-liste.tsx` | Drucken (Bulk) | Bestellungen drucken | **Erledigt (Toast):** onBulkPrint mit Hinweis; Bulk-Druck in Planung | – |
| E2 | `einkauf/bestellungen-liste.tsx` | Import | Import | **Erledigt:** Dialog mit Dateiauswahl, POST /api/v1/einkauf/bestellungen/import (Stub: Zeilen zählen, „Import in Verarbeitung“) | – |
| E3 | `einkauf/lieferschein-erfassung.tsx` | wie vorh. LS (F11) | Vorherigen Lieferschein laden | **Erledigt:** onClick lädt letzten LS per API und übernimmt Daten | – |
| E4 | `einkauf/lieferschein-erfassung.tsx` | → Bestellung(en) importieren | Bestellpositionen übernehmen | **Erledigt:** Dialog mit Bestellliste (GET bestellungen?lieferant_id), Auswahl, „Positionen übernehmen“ (GET bestellungen/:id → Positionen an Lieferschein angehängt) | – |
| E5 | `einkauf/lieferschein-erfassung.tsx` | PopUp, Niederlassung, Chargen-/Serien-Nr. | Zusatzfunktionen | **Erledigt:** PopUp-Dialog (Zusatzinfos Position), Niederlassung aus Branches-API, Chargen/Serien-Dialog (übernommen bei Zeile OK) | – |
| E6 | `einkauf/rechnungseingang.tsx` | Prüfen, Freigeben, Verbuchen | Workflow-Aktionen | **Erledigt:** Hooks rufen API pruefen/freigeben/verbuchen auf | – |
| E7 | `einkauf/rechnung-eingang-erfassung.tsx` | Beleg drucken und buchen | Druck + Buchung | **Erledigt:** handlePrintAndBook ruft pruefen → freigeben → verbuchen | – |
| E8 | `einkauf/rechnung-eingang-erfassung.tsx` | Originalrechnung ▼, wie vorh. RG (F11), Lieferanten-Stamm, ZB-Stamm, → Lieferschein-Auswahl | Erwartete Aktionen | **Erledigt:** Lieferanten-Stamm → navigate/lieferant; ZB-Stamm → navigate; Lieferschein-Auswahl hat Handler; Originalrechnung Toast; wie vorh. RG hat Handler | – |
| E9 | `einkauf/rechnungseingaenge-liste.tsx` | Prüfen/Freigeben/Verbuchen (Bulk) | Massenaktionen | **Erledigt:** bulkWorkflow ruft API pro Auswahl | – |
| E10 | `einkauf/rechnungseingaenge-liste.tsx` | Löschen | Löschen | **Erledigt:** handleDelete ruft DELETE API und invalidates | – |
| E11 | `einkauf/lieferanten-liste.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick | – |
| E12 | `einkauf/lieferanten-stamm.tsx` | Dokument-Download | Download | **Erledigt:** onClick versucht GET …/dokumente/:id/download (Blob), Fallback: Text-Info-Datei-Download + Toast | – |
| E13 | `einkauf/bestellvorschlag-lager.tsx` (und -rohware, -verkauf) | Bestellung erstellen, Manuelle Pos., Calc, Anfrage erstellen | Aktionen | **Erledigt:** Lager/Rohware/Verkauf mit handleBestellungErstellen bzw. POST bestellungen/anfragen; Manuelle Pos., Calc mit onClick | – |
| E14 | `einkauf/anfrage-erfassung.tsx` | F11, Lieferanten-Stamm, Vergleich, Drucken | Erwartete Aktionen | **Erledigt:** F11/Lieferanten-Stamm/Drucken hatten Handler; „Angebots-Vergleich öffnen“-Button → navigate zu rfq-bids/:id | – |

### Modul Agrar

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| A1 | `agrar/feldbuch/massnahmen.tsx` | Export | Export der Maßnahmen | **Erledigt:** handleExport + Button onClick | – |
| A2 | `agrar/feldbuch/schlagkartei.tsx` | Export | Export der Schläge | **Erledigt:** handleExport + Button onClick | – |
| A3 | `agrar/saatgut/sortenregister.tsx` | Export | Export der Sorten | **Erledigt:** handleExport + Button onClick | – |
| A4 | `agrar/saatgut/liste.tsx` | Export CSV | CSV-Export | **Erledigt:** overflowActions Export CSV mit onClick | – |
| A5 | `agrar/saatgut-liste.tsx` | Export CSV | CSV-Export | **Erledigt:** overflowActions Export CSV mit vollständigem Handler | – |
| A6 | `agrar/saatgut-liste.tsx` | Auge vs. Stift (Zeile) | Anzeigen vs. Bearbeiten | **Erledigt:** Auge → Stamm mit `?mode=view` (nur Lesen), Stift → Bearbeiten; Stamm unterstützt readOnlyMode | – |
| A7 | `agrar/psm/sachkunde-register.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick | – |
| A8 | `agrar/psm/wasserschutz.tsx` | Lupe (Adresse) | Geocoding | **Erledigt (M12):** Nominatim Geocoding; Adresssuche beliebig (keine Einschränkung auf Ort); Placeholder „Adresse oder Ort eingeben“ | – |
| A9 | `agrar/ernte/liste.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick | – |
| A10 | `agrar/ernte-annahme-erfassung.tsx` | Abschlagrechnung, Endabrechnung, Sorte bearbeiten, Zus. Felder, Import Analysegerät | Erwartete Aktionen | **Erledigt:** Abschlag/Endabrechnung → calculate-API; Sorte → VarietySelectionDialog; Zus. Felder → Dialog Bemerkungen/Druckoptionen; Import → CSV-Upload (Parameter;Wert) | – |
| A11 | `agrar/bodenproben/liste.tsx`, `kulturpflanzen/liste.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick (beide Seiten) | – |
| A12 | `agrar/biostimulanzien-liste.tsx` | Export CSV / Auge vs. Stift | Export / Anzeigen vs. Bearbeiten | **Erledigt:** Export CSV; Auge → Stamm mit `?mode=view`, Stift → Bearbeiten (Stamm ggf. später mit readOnly) | – |

### Modul Fibu / Finance / Lager / Admin / POS / Annahme

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| F1 | `fibu/kontenplan.tsx`, `fibu/offene-posten.tsx`, `fibu/bilanz.tsx`, `fibu/kreditoren.tsx` | Export, Mahnlauf starten | Export / Mahnlauf | **Erledigt:** Kontenplan, Offene Posten, Bilanz mit exportToCSV/Export CSV; Kreditoren DATEV-Export mit Toast „in Planung“ | – |
| F2 | `fibu/zahlungseingaenge.tsx` | Bank-Import | Bankdaten importieren | **Erledigt:** Dialog (Datei, Format CAMT/MT940/CSV, Bankkonto), POST /api/v1/finance/bank-statements/import | – |
| F3 | `fibu/kreditlinien.tsx`, `fibu/sicherheiten.tsx` | Nur Überzogene / Nur Bonität C/D; Nur Aktive / Nur Überlastet | Filter | **Erledigt:** filterMode-State, Buttons toggeln Filter, Tabelle gefiltert | – |
| F4 | `fibu/zahlungsvorschlaege.tsx` | Zahlungslauf erstellen | Aktion für Auswahl | **Erledigt:** onClick → navigate zu /fibu/zahlungslaeufe | – |
| F5 | `fibu/verbindlichkeiten.tsx` | Zahlungslauf planen | Zahlungslauf starten | **Erledigt:** onClick → navigate zu /fibu/zahlungslaeufe | – |
| F6 | `finance/kontenplan.tsx` | Validieren, Speichern, DATEV Export | Aktionen | **Erledigt:** useMaskActions mit validate/save/export (DATEV API) | – |
| F7 | `finance/op-debitoren.tsx` | Toolbar-Aktionen (Zahlung, Skonto, Ausgleich, Mahnung, Export) | Aktionen ausführen | **Erledigt:** handleAction für zahlung, skonto, ausgleich, mahnung, export (bereits im Code) | – |
| F8 | `finance/debitoren-liste.tsx` | Export / Reminder / Dunning / Block | Aktionen | **Erledigt:** debitorenListConfig überschreibt bulkActions mit onExportBulk, onReminder, onDunning, onBlock | – |
| F9 | `lager/einlagerung.tsx`, `lager/auslagerung.tsx` | Abschliessen / Buchen | Ein-/Auslagerung buchen | **Erledigt:** POST /api/v1/lager/einlagerung bzw. /auslagerung (compat) | – |
| F10 | `admin/benutzer-liste.tsx`, `admin/audit-log.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick (beide Seiten) | – |
| F11 | `admin/compliance-dashboard.tsx` | Compliance-Report (PDF), Details | PDF erzeugen / Detailansicht | **Erledigt:** handleReportPdf (Blob-Download), handleDetails (Toast) | – |
| F12 | `admin/setup/dms-integration.tsx` | Jetzt einrichten | DMS einrichten | **Erledigt:** onClick → setDialogOpen(true) (bereits im Code) | – |
| F13 | `pos/tse-journal.tsx` | DSFinV-K Export, Nur Offene | Export / Filter | **Erledigt:** handleDSFinVExport + „Nur Offene“-Toggle mit onClick | – |
| F14 | `pos/rabatte.tsx` | Nur Aktive, Nur Prozent-Rabatte | Filter | **Erledigt:** filterMode-State, Buttons toggeln, DataTable mit filteredRabatte | – |
| F15 | `pos/suspended-sales.tsx` | Fortsetzen, Löschen | Verkauf fortsetzen / löschen | **Erledigt:** Fortsetzen → navigate mit resumeSaleId; Löschen → `DELETE /api/v1/pos/suspended-sales/:id` + refetch (Stand 2025-03-05 geprüft) | – |
| F16 | `annahme/warteschlange.tsx` | Bearbeiten | Eintrag bearbeiten | **Erledigt:** `onClick` → Navigate zu Qualitäts-Check mit `eintragId`; LKW-Daten werden geladen und vorausgefüllt | – |
| F17 | `annahme/lkw-registrierung.tsx` | Abschliessen | LKW registrieren | **Erledigt:** `handleSubmit` ruft `POST /api/v1/annahme/lkw-registrierung` auf, danach Navigate zur Warteschlange | – |
| F18 | `annahme/lkw-registrierung.tsx` | Scan (Kennzeichen/Lieferschein) | Kamera/Scan | **Erledigt:** Scan-Button öffnet Info-Dialog (Foto-Upload nutzen oder manuell eingeben; Barcode-Scanner in Planung); Upload-Bereiche für Fotos vorhanden | – |
| F19 | `waage/liste.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick | – |

---

## 2. Workflow-Lücken (z. B. Verschieben, Löschen von Positionszeilen)

### Lieferschein / Auftrag / Angebot (Verkauf)

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W1 | Lieferschein-Positionen | **Erledigt:** `handleDeletePosition` + Trash-Button pro Zeile | `verkauf/lieferschein-erfassung.tsx` |
| W2 | Lieferschein-Positionen | **Erledigt:** Hoch/Runter-Buttons, `handleMovePositionUp/Down` | `verkauf/lieferschein-erfassung.tsx` |
| W3 | Lieferschein-Positionen | **Erledigt:** `selectPositionForEdit` lädt Zeile in Positions-Details | `verkauf/lieferschein-erfassung.tsx` |
| W4 | Auftrags-Positionen | **Erledigt:** `handleDeletePosition` + Icon pro Zeile | `sales/order-editor.tsx` |
| W5 | Auftrags-Positionen | **Erledigt:** Hoch/Runter, `handleMovePositionUp/Down` | `sales/order-editor.tsx` |
| W6 | Angebots-Positionen | **Erledigt:** `handlePositionDelete` + Button pro Zeile | `sales/angebot-erstellen.tsx` |
| W7 | Angebots-Positionen | **Erledigt:** Hoch/Runter, `handleMovePositionUp/Down`; Ersetzen bei aktivem Index in handlePositionOK | `sales/angebot-erstellen.tsx` |

### Einkauf

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W8 | Einkauf-Lieferschein / Rechnung Erfassung | **Erledigt:** handleDeletePosition, handleMovePositionUp/Down + Hoch/Runter/Löschen-Buttons | `einkauf/lieferschein-erfassung.tsx`, `rechnung-eingang-erfassung.tsx` |
| W9 | Bestellungen Liste | **Erledigt:** Bulk Freigeben/Stornieren – handleBulkApprove/handleBulkCancel mit selectedItems, Config onClick(items) | `einkauf/bestellungen-liste.tsx` |

### Agrar

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W10 | Maßnahmen, Schlagkartei | **Erledigt:** Löschen/Bearbeiten pro Zeile (Maßnahmen: useDeleteMassnahme + Aktionen-Spalte; Schlagkartei: useDeleteSchlag + Stilllegen-Button). Übrige Listen (Sortenregister, Ernte, Bodenproben, Kulturpflanzen) bei Bedarf analog. | `agrar/feldbuch/massnahmen.tsx`, `agrar/feldbuch/schlagkartei.tsx` |
| W11 | Dünger-Mischungen | Komponenten-Zeilen: Verschieben (Reihenfolge) | **Erledigt:** moveKomponenteUp/Down, ChevronUp/ChevronDown pro Zeile | `agrar/duenger/mischungen.tsx` |
| W12 | Ernte-Liste | Suchbegriff an Tabelle/Filter | **Erledigt:** `filteredErnten` aus searchTerm, DataTable erhält filteredErnten; Suchfeld filtert Schlag/Kultur/Status | `agrar/ernte/liste.tsx` |
| W13 | Bedarfsrechner | „Ergebnis speichern“ / „Als Düngeplan übernehmen“ | **Erledigt (Toast):** Buttons im Empfehlungsschritt mit onClick + Hinweis „in Planung“ | `agrar/duenger/bedarfsrechner.tsx` |

### Lager

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W14 | Inventur | **Erledigt:** Stornieren-Button pro Position, DELETE /api/v1/inventory/inventur/:id (compat), useStornierenInventurPosition | `lager/inventur.tsx` |
| W15 | Einlagerung / Auslagerung | **Erledigt:** POST `/api/v1/lager/einlagerung` bzw. `/auslagerung` in beiden Seiten (Stand 2025-03-05 geprüft) | `lager/einlagerung.tsx`, `lager/auslagerung.tsx` |

---

## 3. Mock-Daten / Platzhalter-Seiten / TODO

### Verkauf

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M1 | `verkauf/lieferschein-erfassung.tsx` | **Erledigt** | branch_id aus branchesList (niederlassung→branch_number); Branches beim Mount laden |
| M2 | `verkauf/lieferschein-erfassung.tsx` | **Erledigt** | Attestation „modify“: PATCH status 'offen' (bereits im Code) |
| M3 | `sales/order-editor.tsx` | **Erledigt** | Kunde per response.customer_id aus API geladen; response.data berücksichtigt |
| M4 | `sales/invoice-editor.tsx` | **Erledigt** | Default number "" statt fester INV-Nummer; bei Edit weiterhin aus Docflow-API |

### Einkauf

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M5 | `einkauf/bestellung-stamm.tsx` | **Erledigt** | Nutzt bereits `useTenant()` und `useAuth()` für tenant_id/user (Stand 2025-03-05) |
| M6 | `einkauf/lieferanten-stamm.tsx` | **Erledigt** | Bei API-Fehler: Toast + minimaler State statt Mock „Saatgut AG“ |
| M7 | `einkauf/gutschriften-belastungen.tsx` | **Erledigt** | openAmount aus GET /api/v1/finance/open-items?konto_typ=kreditoren (nach Rechnungsnr gemappt) |

### Agrar

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M8 | `agrar/feldbuch/schlag/neu.tsx` | **Erledigt** | BODENARTEN als Stammdaten kommentiert (optional später aus API) |
| M9 | `agrar/saatgut/bestellung.tsx` | **Erledigt** | Leerer Initial-State; useKunden(), useSchlaege(kundeId), useKulturen(), useSorten(); Kunde → Schlag |
| M10 | `agrar/saatgut-stamm.tsx`, `agrar/duenger-stamm.tsx` | **Erledigt** | Nutzen bereits `useTenant()` für tenant_id (Stand 2025-03-05) |
| M11 | `agrar/psm/abgabedokumentation.tsx` | **Erledigt** | Leerer Initial-State für Route „neu“; bei ID Laden aus API (useQuery) |
| M12 | `agrar/psm/wasserschutz.tsx` | **Erledigt** | Nominatim Geocoding; Placeholder „Adresse oder Ort eingeben“ (A8) |
| M13 | `agrar/psm/beratung.tsx` | **Erledigt** | usePSM-Mapping + Demo-Fallback (Amistar Opti, Folicur Solo, Nativo) wenn API leer |
| M14 | `agrar/ernte-annahme-erfassung.tsx` | **Erledigt** | article_name/Lab aus Positionen; USt-ID als Modal (statt prompt) |
| M15 | `agrar/duenger/bedarfsrechner.tsx` | **Erledigt** | Fallback-Kulturen (Weizen/Gerste/Raps/Mais/Grünland) + LWK-Tab. 1/2, 3a/3b, N-Gaben, Schwefel |

### Finance / Lager / POS / Annahme

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M16 | `finance/chart-of-accounts.tsx`, `debitoren-stamm.tsx` | **Erledigt** | Nutzen bereits `useTenant()` für tenant_id (Stand 2025-03-05) |
| M17 | `finance/op-kreditoren.tsx` | **Erledigt** | createMutation ruft `POST /api/v1/finance/open-items` (Stand 2025-03-05 geprüft) |
| M18 | `finance/invoice-form.tsx` | **Erledigt** | Echte Kunden-Suche: Combobox mit GET /api/v1/crm/customers?search=… (Stand 2025-03-05) |
| M19 | `lager/bestandsuebersicht.tsx` | **Erledigt** | Fallback 0 € / 0 Tage statt fester Mock-Werte |
| M20 | `lager/lagerplaetze.tsx` | **Erledigt** | Daten aus useWarehouses() (API); leere Ansicht wenn keine Lager |
| M21 | `lager/auslagerung.tsx` | **Erledigt** | FIFO setzt chargenId auf "" (kein Dummy-Text mehr) |
| M22 | `pos/terminal.tsx` | Konzept | TSE/Offline in docs/AUTH-AND-TENANT-CONCEPT.md beschrieben; Implementierung hängt an TSE-API/Offline-Sync |
| M23 | `pos/suspended-sales.tsx` | **Erledigt** | Fortsetzen (navigate) + Löschen (DELETE /api/v1/pos/suspended-sales/:id) im Code (F15) |

---

## 4. Kurz-Zusammenfassung

- **Diskrepanzen:** **Umgesetzt:** F1–F5, F7, F11, F12, F14, F15, F16–F18 (Export/Mahnlauf FiBu, Bank-Import, Filter, Zahlungslauf, OP-Debitoren, Compliance, DMS, Rabatte, suspended-sales, Annahme Bearbeiten/Registrierung/Scan); E2, E4 (Bestellungen-Import, Bestellung→Lieferschein-Positionen). **Tenant/Auth:** CRM, FiBu, bestellung-stamm, saatgut/duenger-stamm, chart-of-accounts, debitoren-stamm nutzen useTenant/useAuth.
- **Workflow-Lücken:** **Lieferschein/Auftrag/Angebot:** erledigt. **Lager:** Ein-/Auslagerung + Inventur Stornieren (W14) erledigt. **Agrar:** Maßnahmen + Schlagkartei mit Löschen/Stilllegen (W10) erledigt.
- **Mock/TODO:** **Erledigt:** M5–M15, M16–M21, M23 (Agrar: leerer State, usePSM/Nominatim/Fallback, LWK; Tenant, Ernte USt-ID, Lager, suspended-sales). **Konzept:** M22 (TSE/Offline in docs/AUTH-AND-TENANT-CONCEPT.md). **Offen:** keine.

---

## 5. Status & priorisierte Nächste Schritte

| Status    | Einträge | Anmerkung |
|-----------|----------|-----------|
| Erledigt  | F1–F19, E2, E4, W10, W14, W15, M1–M21, M23 | Agrar M9–M15: leerer State, usePSM/Nominatim/Fallback, LWK; E4: Bestellung→LS; F18: Scan-Dialog; M22: Konzept |
| Teilweise | –        | – |
| Offen     | –        | Alle zuvor offenen Mock-Punkte (M9, M11–M15) erledigt bzw. in Code bereits umgesetzt |

**Empfohlene Reihenfolge für die Abarbeitung:**

1. **Lieferschein (Verkauf):** Position löschen, Verschieben (Hoch/Runter), Zeile zur Bearbeitung auswählen (W1–W3).
2. **Sofort-Rechnung:** V6 (Lieferschein), V8 (Auftrag) – Rechnung aus Beleg erzeugen.
3. **Auftrag/Angebot:** Position löschen & Verschieben (W4–W7); V9 Buttons (Speichern, In Auftrag wandeln, Löschen, Beenden).
4. **Einkauf:** Rechnungseingang Prüfen/Freigeben/Verbuchen (E6, E7, E9), Beleg drucken und buchen; ggf. Position löschen/verschieben (W8).
5. **Export-Buttons:** Einheitlicher Export (CSV/PDF) wo „Export“ angeboten wird (Verkauf, Einkauf, Agrar, Fibu, Admin).
6. **Finance-Toolbars:** F6, F7, F8 – Validieren, Speichern, DATEV, OP-Debitoren, Kasse, Mahnwesen etc. mit echten Handlern.
7. **Lager:** Ein-/Auslagerung Buchen mit Backend-Anbindung (F9, W15).
8. **Mock/TODO:** M1–M21, M23 erledigt (inkl. M9 Saatgut-Bestellung, M11 PSM-Abgabe, M12 Wasserschutz, M13 PSM-Beratung, M15 Bedarfsrechner). M22 TSE/Offline Konzept in docs/AUTH-AND-TENANT-CONCEPT.md. Offen: –.

---

*Ende der Audit-Liste. Bei Abarbeitung: Eintrag in Tabelle auf „Erledigt“ setzen bzw. Priorität auf „–“ und kurze Anmerkung ergänzen.*
