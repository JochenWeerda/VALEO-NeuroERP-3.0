# Button- & UX-Audit: Diskrepanzen, Workflow-Lücken, Mock-Daten

**Zuletzt aktualisiert:** 2025-03-01

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
| E2 | `einkauf/bestellungen-liste.tsx` | Import | Import | Toast „Import kommt in Kürze“ (onImport) | Niedrig |
| E3 | `einkauf/lieferschein-erfassung.tsx` | wie vorh. LS (F11) | Vorherigen Lieferschein laden | **Erledigt:** onClick lädt letzten LS per API und übernimmt Daten | – |
| E4 | `einkauf/lieferschein-erfassung.tsx` | → Bestellung(en) importieren | Bestellpositionen übernehmen | **Teilweise:** onClick mit Hinweis; Import-Logik in Planung | Mittel |
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
| A6 | `agrar/saatgut-liste.tsx` | Auge vs. Stift (Zeile) | Anzeigen vs. Bearbeiten | Beide navigieren zu Stamm – kein Unterschied | Mittel |
| A7 | `agrar/psm/sachkunde-register.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick | – |
| A8 | `agrar/psm/wasserschutz.tsx` | Lupe (Adresse) | Geocoding | **Erledigt:** Nominatim (OpenStreetMap) Geocoding; Adresse → Koordinaten, Toast bei Erfolg/Fehler | – |
| A9 | `agrar/ernte/liste.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick | – |
| A10 | `agrar/ernte-annahme-erfassung.tsx` | Abschlagrechnung, Endabrechnung, Sorte bearbeiten, Zus. Felder, Import Analysegerät | Erwartete Aktionen | **Erledigt:** Abschlag/Endabrechnung → calculate-API; Sorte → VarietySelectionDialog; Zus. Felder → Dialog Bemerkungen/Druckoptionen; Import → CSV-Upload (Parameter;Wert) | – |
| A11 | `agrar/bodenproben/liste.tsx`, `kulturpflanzen/liste.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick (beide Seiten) | – |
| A12 | `agrar/biostimulanzien-liste.tsx` | Export CSV / Auge vs. Stift | Export / Anzeigen vs. Bearbeiten | **Erledigt (Export):** overflowActions Export CSV; Auge/Stift weiterhin beide zu Stamm | Mittel |

### Modul Fibu / Finance / Lager / Admin / POS / Annahme

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| F1 | `fibu/kontenplan.tsx`, `fibu/offene-posten.tsx`, `fibu/bilanz.tsx`, `fibu/kreditoren.tsx` | Export, Mahnlauf starten | Export / Mahnlauf | **Erledigt:** Kontenplan, Offene Posten, Bilanz mit exportToCSV/Export CSV; Kreditoren DATEV-Export mit Toast „in Planung“ | Mittel |
| F2 | `fibu/zahlungseingaenge.tsx` | Bank-Import | Bankdaten importieren | Kein `onClick` im Header | Mittel |
| F3 | `fibu/kreditlinien.tsx`, `fibu/sicherheiten.tsx` | Nur Überzogene / Nur Bonität C/D; Nur Aktive / Nur Überlastet | Filter | Kein `onClick` | Niedrig |
| F4 | `fibu/zahlungsvorschlaege.tsx` | Freigeben (o. ä.) | Aktion für Auswahl | `disabled` wenn keine Auswahl, kein Handler | Mittel |
| F5 | `fibu/verbindlichkeiten.tsx` | Zahlungslauf planen | Zahlungslauf starten | Kein `onClick` | Mittel |
| F6 | `finance/kontenplan.tsx` | Validieren, Speichern, DATEV Export | Aktionen | **Erledigt:** useMaskActions mit validate/save/export (DATEV API) | – |
| F7 | `finance/op-debitoren.tsx`, … | Toolbar-Aktionen | Aktionen ausführen | Teilweise: Einzelne Seiten ggf. noch leere Handler | Mittel |
| F8 | `finance/debitoren-liste.tsx` | Export / Reminder / Dunning / Block | Aktionen | **Erledigt:** debitorenListConfig überschreibt bulkActions mit onExportBulk, onReminder, onDunning, onBlock | – |
| F9 | `lager/einlagerung.tsx`, `lager/auslagerung.tsx` | Abschliessen / Buchen | Ein-/Auslagerung buchen | **Erledigt:** POST /api/v1/lager/einlagerung bzw. /auslagerung (compat) | – |
| F10 | `admin/benutzer-liste.tsx`, `admin/audit-log.tsx` | Export | Export | **Erledigt:** handleExport + Button onClick (beide Seiten) | – |
| F11 | `admin/compliance-dashboard.tsx` | Compliance-Report (PDF), Details | PDF erzeugen / Detailansicht | Kein `onClick` | Hoch |
| F12 | `admin/setup/dms-integration.tsx` | Jetzt einrichten | DMS einrichten | Kein `onClick` am Button | Mittel |
| F13 | `pos/tse-journal.tsx` | DSFinV-K Export, Nur Offene | Export / Filter | **Erledigt:** handleDSFinVExport + „Nur Offene“-Toggle mit onClick | – |
| F14 | `pos/rabatte.tsx` | Nur Aktive, Nur Prozent-Rabatte | Filter | Kein `onClick` | Niedrig |
| F15 | `pos/suspended-sales.tsx` | Fortsetzen, Löschen | Verkauf fortsetzen / löschen | Fortsetzen: nur `alert` + lokales Entfernen; Löschen: nur lokaler State | Hoch |
| F16 | `annahme/warteschlange.tsx` | Bearbeiten | Eintrag bearbeiten | **Erledigt:** `onClick` → Navigate zu Qualitäts-Check mit `eintragId`; LKW-Daten werden geladen und vorausgefüllt | – |
| F17 | `annahme/lkw-registrierung.tsx` | Abschliessen | LKW registrieren | **Erledigt:** `handleSubmit` ruft `POST /api/v1/annahme/lkw-registrierung` auf, danach Navigate zur Warteschlange | – |
| F18 | `annahme/lkw-registrierung.tsx` | Scan (Kennzeichen/Lieferschein) | Kamera/Scan | **Teilweise:** `handleScan` zeigt Toast; Upload-Bereiche für Fotos (Kennzeichen/Lieferschein) implementiert; optional später echter Barcode-Scanner | Mittel |
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
| W10 | Maßnahmen, Schlagkartei, Sortenregister, Ernte, Bodenproben, Kulturpflanzen | Kein **Löschen/Bearbeiten** pro Zeile in Tabellen | jew. `agrar/…/liste.tsx` bzw. `schlagkartei.tsx`, `massnahmen.tsx` |
| W11 | Dünger-Mischungen | Komponenten-Zeilen: Verschieben (Reihenfolge) | **Erledigt:** moveKomponenteUp/Down, ChevronUp/ChevronDown pro Zeile | `agrar/duenger/mischungen.tsx` |
| W12 | Ernte-Liste | Suchbegriff an Tabelle/Filter | **Erledigt:** `filteredErnten` aus searchTerm, DataTable erhält filteredErnten; Suchfeld filtert Schlag/Kultur/Status | `agrar/ernte/liste.tsx` |
| W13 | Bedarfsrechner | „Ergebnis speichern“ / „Als Düngeplan übernehmen“ | **Erledigt (Toast):** Buttons im Empfehlungsschritt mit onClick + Hinweis „in Planung“ | `agrar/duenger/bedarfsrechner.tsx` |

### Lager

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W14 | Inventur | Kein Abbrechen/Löschen pro Position, kein „Stornieren“ | `lager/inventur.tsx` |
| W15 | Einlagerung / Auslagerung | **Kein Backend-Aufruf** bei „Buchen“/„Abschliessen“ – keine echte Buchung | `lager/einlagerung.tsx`, `lager/auslagerung.tsx` |

---

## 3. Mock-Daten / Platzhalter-Seiten / TODO

### Verkauf

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M1 | `verkauf/lieferschein-erfassung.tsx` 468–469, 527 | TODO | `branch_id`/`sales_rep_id`: „Map niederlassung to branch_id“ |
| M2 | `verkauf/lieferschein-erfassung.tsx` 767–768 | Nicht implementiert | Attestation „modify“: Toast „Korrektur noch nicht implementiert“ |
| M3 | `sales/order-editor.tsx` 656–657 | Platzhalter | Bei Auftrag-Auswahl: Kunde nur als `{ id: '', name: auftrag.kunde }` – nicht per ID geladen |
| M4 | `sales/invoice-editor.tsx` 49–62 | Default-State | Feste Nummer „INV-2025-0001“, Default-Zeile – echte Daten bei Edit per API |

### Einkauf

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M5 | `einkauf/bestellung-stamm.tsx` | TODO | `user_id`, `user_email`, `tenant_id` fest – aus Auth/Tenant-Kontext holen |
| M6 | `einkauf/lieferanten-stamm.tsx` | Mock | Bei API-Fehler: Fallback Mock-Daten („Saatgut AG“, Adresse, Bank) – explizit kommentiert |
| M7 | `einkauf/gutschriften-belastungen.tsx` | TODO | `openAmount: inv.totalGross \|\| … // TODO: Calculate from open items` |

### Agrar

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M8 | `agrar/feldbuch/schlag/neu.tsx` | Mock | `BODENARTEN` fest codiert (Sand, Lehm, Ton, …) |
| M9 | `agrar/saatgut/bestellung.tsx` | Mock | Initiale Bestellung mit festen IDs (KUN-001, SCH-001, Musterhof GmbH) |
| M10 | `agrar/saatgut-stamm.tsx`, `agrar/duenger-stamm.tsx` | TODO | `tenant_id: '…' // TODO: Get from auth context` |
| M11 | `agrar/psm/abgabedokumentation.tsx` | Mock | Kompletter Initial-State (PSM-ABG-001, Roundup, Musterhof, Max Mustermann, …) |
| M12 | `agrar/psm/wasserschutz.tsx` | Demo | Adress-Suche nur „Berlin“ |
| M13 | `agrar/psm/beratung.tsx` | Mock | Feste PSM-Empfehlungen (Amistar Opti, Folicur Solo, Nativo) |
| M14 | `agrar/ernte-annahme-erfassung.tsx` | TODO | `articleName` / `windabgang` „Aus Artikel/Positionen laden“; USt-ID-Dialog |
| M15 | `agrar/duenger/bedarfsrechner.tsx` | Fallback | Optionen Weizen/Gerste/Raps/Mais wenn `kulturenListe` leer |

### Finance / Lager / POS / Annahme

| # | Fundstelle | Art | Beschreibung |
|---|------------|-----|--------------|
| M16 | `finance/chart-of-accounts.tsx`, `debitoren-stamm.tsx` | TODO | `tenant_id` fest; „Get from context“ |
| M17 | `finance/op-kreditoren.tsx` | TODO | `// TODO: API call to save OP-Kreditor` |
| M18 | `finance/invoice-form.tsx` | TODO | `// TODO: Echte Kunden-Suche` |
| M19 | `lager/bestandsuebersicht.tsx` | Fallback | „€ 2.450.000“, „32 Tage“, „0“ Bewegungen, PSM 0 hardcodiert |
| M20 | `lager/lagerplaetze.tsx` | Mock | Komplett hardcodierte Daten (plaetze, belegt, bereiche) |
| M21 | `lager/auslagerung.tsx` | Dummy | FIFO setzt `chargenId` auf „251001-WEI-001 (älteste)“ (Dummy-Text) |
| M22 | `pos/terminal.tsx` | TODO | `// TODO: await saveTSETransaction(...)`, `// TODO: Offline-Queue` |
| M23 | `pos/suspended-sales.tsx` | Unvollständig | Fortsetzen/Löschen nur lokal, kein Backend |

---

## 4. Kurz-Zusammenfassung

- **Diskrepanzen:** Über alle Module hinweg viele **Export**-Buttons ohne Funktion, **Toolbar-/Filter-Buttons** mit leerem `onClick` oder nur `console.log`, sowie zentrale Aktionen (Sofort-Rechnung, Prüfen/Freigeben/Verbuchen Rechnungseingang, Finance-Toolbars, Ein-/Auslagerung buchen, POS Fortsetzen/Löschen) nicht oder nur Platzhalter umgesetzt. **Annahme (F16–F18):** F16/F17 erledigt; F18 teilweise (Scan Toast + Upload-Fotos, optional später Barcode-Scanner).
- **Workflow-Lücken:** **Lieferschein/Auftrag/Angebot:** Position löschen & Verschieben fehlen; Lieferschein: Zeile zur Bearbeitung auswählen fehlt. **Einkauf:** Kein Zeilen-Löschen/Verschieben in LS/Rechnung. **Agrar:** Viele Listen ohne Zeilen-Löschen/Bearbeiten; Ernte-Liste Suche ohne Filterwirkung. **Lager:** Ein-/Auslagerung ohne echte Buchung.
- **Mock/TODO:** Tenant/Auth-Kontext in mehreren Stamm-Masken; Lieferanten-Stamm Mock-Fallback; Agrar (PSM-Abgabe, Saatgut-Bestellung, Beratung, Wasserschutz); Lager (Bestandsübersicht, Lagerplätze, Auslagerung Charge); POS/Annahme (TSE, Offline, LKW-Registrierung).

---

## 5. Status & priorisierte Nächste Schritte

| Status    | Einträge | Anmerkung |
|-----------|----------|-----------|
| Erledigt  | F16, F17 | Annahme: Bearbeiten → Qualitäts-Check; Abschliessen → POST LKW-Registrierung |
| Teilweise | F18      | Scan: Toast + Upload-Fotos; optional später Barcode-Scanner |
| Offen     | Alle übrigen | Siehe Tabellen in Abschnitt 1–3 |

**Empfohlene Reihenfolge für die Abarbeitung:**

1. **Lieferschein (Verkauf):** Position löschen, Verschieben (Hoch/Runter), Zeile zur Bearbeitung auswählen (W1–W3).
2. **Sofort-Rechnung:** V6 (Lieferschein), V8 (Auftrag) – Rechnung aus Beleg erzeugen.
3. **Auftrag/Angebot:** Position löschen & Verschieben (W4–W7); V9 Buttons (Speichern, In Auftrag wandeln, Löschen, Beenden).
4. **Einkauf:** Rechnungseingang Prüfen/Freigeben/Verbuchen (E6, E7, E9), Beleg drucken und buchen; ggf. Position löschen/verschieben (W8).
5. **Export-Buttons:** Einheitlicher Export (CSV/PDF) wo „Export“ angeboten wird (Verkauf, Einkauf, Agrar, Fibu, Admin).
6. **Finance-Toolbars:** F6, F7, F8 – Validieren, Speichern, DATEV, OP-Debitoren, Kasse, Mahnwesen etc. mit echten Handlern.
7. **Lager:** Ein-/Auslagerung Buchen mit Backend-Anbindung (F9, W15).
8. **Mock/TODO:** Tenant/Auth aus Kontext; echte APIs statt Fallback-Daten (nach Bedarf).

---

*Ende der Audit-Liste. Bei Abarbeitung: Eintrag in Tabelle auf „Erledigt“ setzen bzw. Priorität auf „–“ und kurze Anmerkung ergänzen.*
