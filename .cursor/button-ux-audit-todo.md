# Button- & UX-Audit: Diskrepanzen, Workflow-Lücken, Mock-Daten

Erstellt aus paralleler Code-Analyse der Module Verkauf, Einkauf, Agrar, Fibu/Finance/Lager/Admin/POS/Annahme.
**Hinweis:** Laufzeitprüfung (tatsächliches Klicken) wurde nicht durchgeführt; Angaben basieren auf Code-Analyse.

---

## 1. Diskrepanzen: Button-Beschriftung vs. tatsächliche Reaktion

### Modul Verkauf

| # | Fundstelle | Button/Label | Erwartung (Beschriftung) | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|---------------------------|------------------------|-----------|
| V1 | `verkauf/lieferschein-erfassung.tsx` ~1256,1259,1262 | MoreHorizontal, ChevronLeft, ChevronRight (Lieferschein-Nr.) | Lieferschein wechseln/suchen, vor/zurück | Kein `onClick` | Hoch |
| V2 | `verkauf/lieferschein-erfassung.tsx` ~1356,1363 | MoreHorizontal (Niederlassung, Vertreter) | Auswahl Niederlassung/Vertreter | Kein `onClick` | Hoch |
| V3 | `verkauf/lieferschein-erfassung.tsx` ~1848,1757 | PopUp, Details (Position) | Zusatzinfos/Details zur Position | Kein `onClick` | Mittel |
| V4 | `verkauf/lieferschein-erfassung.tsx` ~1976 | Kontrakte | Kontrakte anzeigen/verknüpfen | Kein `onClick` | Mittel |
| V5 | `verkauf/lieferschein-erfassung.tsx` ~1980 | Connect Anwendungen | Schnittstelle (z. B. Waage) | Kein `onClick` | Mittel |
| V6 | `verkauf/lieferschein-erfassung.tsx` ~1984,1192 | Sofort-Rechnung | Rechnung aus Lieferschein erzeugen | Toast „Sofort-Rechnung noch nicht implementiert“ | Hoch |
| V7 | `sales/order-editor.tsx` ~480,524 | ChevronLeft/Right, MoreHorizontal (Niederlassung/Vertreter) | Vor/Zurück, Auswahl | Kein `onClick` | Hoch |
| V8 | `sales/order-editor.tsx` ~897,906 | Kontrakte, Sofort-Rechnung | Kontrakte / Rechnung aus Auftrag | Kein Handler / nur Toast | Mittel |
| V9 | `sales/angebot-erstellen.tsx` ~326,428,436,438,444 | Chevron; Speichern; In Auftrag wandeln; Löschen; Beenden | Navigation; Speichern; Auftrag erzeugen; Löschen; Schließen | Kein `onClick` für alle | Hoch |
| V10 | `sales/angebot-erstellen.tsx` | Zeile bearbeiten (bei aktivem Index) | Position ersetzen | Nur Hinzufügen, kein Ersetzen in Liste | Mittel |

### Modul Einkauf

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| E1 | `einkauf/bestellungen-liste.tsx` | Drucken (Bulk) | Bestellungen drucken | `/* noch nicht implementiert */` | Mittel |
| E2 | `einkauf/bestellungen-liste.tsx` | Import | Import | Toast „Import kommt in Kürze“ | Niedrig |
| E3 | `einkauf/lieferschein-erfassung.tsx` | wie vorh. LS (F11) | Vorherigen Lieferschein laden | Toast „noch nicht implementiert“ | Mittel |
| E4 | `einkauf/lieferschein-erfassung.tsx` | → Bestellung(en) importieren | Bestellpositionen übernehmen | Toast „noch nicht implementiert“ | Hoch |
| E5 | `einkauf/lieferschein-erfassung.tsx` | PopUp, Niederlassung, Chargen-/Serien-Nr. | Zusatzfunktionen | Keine Handler | Mittel |
| E6 | `einkauf/rechnungseingang.tsx` | Prüfen, Freigeben, Verbuchen | Workflow-Aktionen | Nur `console.log('… clicked')` | Hoch |
| E7 | `einkauf/rechnung-eingang-erfassung.tsx` | Beleg drucken und buchen | Druck + Buchung | Nur `handleSave()` + Toast, kein Druck/Buchungs-API | Hoch |
| E8 | `einkauf/rechnung-eingang-erfassung.tsx` | Originalrechnung ▼, wie vorh. RG (F11), Lieferanten-Stamm, Auswahl ZB-Stamm, → Lieferschein-Auswahl | Erwartete Aktionen | Nicht implementiert (Toast/kein Handler) | Mittel |
| E9 | `einkauf/rechnungseingaenge-liste.tsx` | Prüfen/Freigeben/Verbuchen (Bulk) | Massenaktionen | Nur `console.log` | Hoch |
| E10 | `einkauf/rechnungseingaenge-liste.tsx` | Löschen | Löschen | Toast „Löschen wird in dieser Ansicht noch nicht unterstützt“ | Mittel |
| E11 | `einkauf/lieferanten-liste.tsx` | Export | Export | Button ohne `onClick` | Mittel |
| E12 | `einkauf/lieferanten-stamm.tsx` | Dokument-Download | Download | Toast „Download kommt in Kürze“ | Niedrig |
| E13 | `einkauf/bestellvorschlag-lager.tsx` (und -rohware, -verkauf) | Bestellung erstellen, Manuelle Pos., Calc, Anfrage erstellen | Aktionen | `push('… nicht implementiert')` | Hoch |
| E14 | `einkauf/anfrage-erfassung.tsx` | Diverse (F11, Lieferanten-Stamm, Vergleich, Drucken …) | Erwartete Aktionen | `push('… nicht implementiert')` | Mittel |

### Modul Agrar

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| A1 | `agrar/feldbuch/massnahmen.tsx` | Export | Export der Maßnahmen | Kein `onClick` | Mittel |
| A2 | `agrar/feldbuch/schlagkartei.tsx` | Export | Export der Schläge | Kein `onClick` | Mittel |
| A3 | `agrar/saatgut/sortenregister.tsx` | Export | Export der Sorten | Kein `onClick` | Mittel |
| A4 | `agrar/saatgut/liste.tsx` | Export CSV | CSV-Export | `// placeholder for future export` | Mittel |
| A5 | `agrar/saatgut-liste.tsx` | Export CSV | CSV-Export | Leerer Handler `onClick: () => { }` | Mittel |
| A6 | `agrar/saatgut-liste.tsx` | Auge vs. Stift (Zeile) | Anzeigen vs. Bearbeiten | Beide navigieren zu Stamm – kein Unterschied | Mittel |
| A7 | `agrar/psm/sachkunde-register.tsx` | Export | Export | Kein `onClick` | Mittel |
| A8 | `agrar/psm/wasserschutz.tsx` | Lupe (Adresse) | Geocoding | Nur „Berlin“ wird erkannt, sonst Toast „nicht gefunden“ | Hoch |
| A9 | `agrar/ernte/liste.tsx` | Export | Export | Kein `onClick` | Mittel |
| A10 | `agrar/ernte-annahme-erfassung.tsx` | Abschlagrechnung, Endabrechnung, Sorte bearbeiten, Zus. Felder, Download | Erwartete Aktionen | Kein `onClick` | Hoch |
| A11 | `agrar/bodenproben/liste.tsx`, `kulturpflanzen/liste.tsx` | Export | Export | Kein `onClick` | Mittel |
| A12 | `agrar/biostimulanzien-liste.tsx` | Export CSV / Auge vs. Stift | Export / Anzeigen vs. Bearbeiten | Placeholder; beide zu Stamm identisch | Mittel |

### Modul Fibu / Finance / Lager / Admin / POS / Annahme

| # | Fundstelle | Button/Label | Erwartung | Tatsächliche Reaktion | Priorität |
|---|------------|--------------|-----------|------------------------|-----------|
| F1 | `fibu/kontenplan.tsx`, `fibu/offene-posten.tsx`, `fibu/bilanz.tsx`, `fibu/kreditoren.tsx` | Export, Mahnlauf starten | Export / Mahnlauf | Kein `onClick` | Mittel |
| F2 | `fibu/zahlungseingaenge.tsx` | Bank-Import | Bankdaten importieren | Kein `onClick` im Header | Mittel |
| F3 | `fibu/kreditlinien.tsx`, `fibu/sicherheiten.tsx` | Nur Überzogene / Nur Bonität C/D; Nur Aktive / Nur Überlastet | Filter | Kein `onClick` | Niedrig |
| F4 | `fibu/zahlungsvorschlaege.tsx` | Freigeben (o. ä.) | Aktion für Auswahl | `disabled` wenn keine Auswahl, kein Handler | Mittel |
| F5 | `fibu/verbindlichkeiten.tsx` | Zahlungslauf planen | Zahlungslauf starten | Kein `onClick` | Mittel |
| F6 | `finance/kontenplan.tsx` | Validieren, Speichern, DATEV Export | Aktionen | `onClick: () => {}` | Hoch |
| F7 | `finance/op-debitoren.tsx`, `kreditoren-stamm.tsx`, `kasse.tsx`, `lastschriften-debitoren.tsx`, `buchungserfassung.tsx`, `bank-abgleich.tsx`, `mahnwesen.tsx`, `abschluss.tsx`, `ustva.tsx`, `dunning-editor.tsx`, `bankkonten-stamm.tsx` | Toolbar-Aktionen | Aktionen ausführen | `onClick: () => {}` (leer) | Hoch |
| F8 | `finance/debitoren-liste.tsx` | Export / Reminder / Dunning / Block | Aktionen | Nur `console.log('… clicked')` | Hoch |
| F9 | `lager/einlagerung.tsx`, `lager/auslagerung.tsx` | Abschliessen / Buchen | Ein-/Auslagerung buchen | Nur `console.log` + `navigate`; kein API-Call | Hoch |
| F10 | `admin/benutzer-liste.tsx`, `admin/audit-log.tsx` | Export | Export | Kein `onClick` | Mittel |
| F11 | `admin/compliance-dashboard.tsx` | Compliance-Report (PDF), Details | PDF erzeugen / Detailansicht | Kein `onClick` | Hoch |
| F12 | `admin/setup/dms-integration.tsx` | Jetzt einrichten | DMS einrichten | Kein `onClick` am Button | Mittel |
| F13 | `pos/tse-journal.tsx` | DSFinV-K Export, Nur Offene | Export / Filter | Kein `onClick` | Mittel |
| F14 | `pos/rabatte.tsx` | Nur Aktive, Nur Prozent-Rabatte | Filter | Kein `onClick` | Niedrig |
| F15 | `pos/suspended-sales.tsx` | Fortsetzen, Löschen | Verkauf fortsetzen / löschen | Fortsetzen: nur `alert` + lokales Entfernen; Löschen: nur lokaler State | Hoch |
| F16 | `annahme/warteschlange.tsx` | Bearbeiten | Eintrag bearbeiten | Kein `onClick` | Mittel |
| F17 | `annahme/lkw-registrierung.tsx` | Abschliessen | LKW registrieren | Nur Toast + `navigate`, kein API-Call | Hoch |
| F18 | `annahme/lkw-registrierung.tsx` | Scan (Kennzeichen/Lieferschein) | Kamera/Scan | Kein Handler | Mittel |
| F19 | `waage/liste.tsx` | Export | Export | Kein `onClick` | Niedrig |

---

## 2. Workflow-Lücken (z. B. Verschieben, Löschen von Positionszeilen)

### Lieferschein / Auftrag / Angebot (Verkauf)

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W1 | Lieferschein-Positionen | **Löschen einer Position** nicht implementiert – kein Button/Aktion pro Zeile | `verkauf/lieferschein-erfassung.tsx` |
| W2 | Lieferschein-Positionen | **Reihenfolge ändern (Verschieben)** nicht implementiert – kein Drag & Drop, keine Hoch/Runter-Buttons | `verkauf/lieferschein-erfassung.tsx` |
| W3 | Lieferschein-Positionen | **Zeile zur Bearbeitung auswählen** – Klick auf Position lädt sie nicht in die Positions-Details | `verkauf/lieferschein-erfassung.tsx` |
| W4 | Auftrags-Positionen | **Löschen einer Position** – kein Button „Position löschen“; Abbrechen bricht nur Bearbeitung ab | `sales/order-editor.tsx` |
| W5 | Auftrags-Positionen | **Reihenfolge ändern** nicht implementiert | `sales/order-editor.tsx` |
| W6 | Angebots-Positionen | **Löschen einer Position** nicht implementiert | `sales/angebot-erstellen.tsx` |
| W7 | Angebots-Positionen | **Reihenfolge ändern** nicht implementiert; **Bearbeiten (Ersetzen)** bei aktivem Index fehlt in Liste | `sales/angebot-erstellen.tsx` |

### Einkauf

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W8 | Einkauf-Lieferschein / Rechnung Erfassung | Positionen: **Kein Verschieben**, **kein Löschen** von Zeilen | `einkauf/lieferschein-erfassung.tsx`, `rechnung-eingang-erfassung.tsx` |
| W9 | Bestellungen Liste | Bulk **Freigeben/Stornieren** nur pro Zeile, keine echte Bulk-Logik | `einkauf/bestellungen-liste.tsx` |

### Agrar

| # | Kontext | Lücke | Fundstelle |
|---|---------|--------|------------|
| W10 | Maßnahmen, Schlagkartei, Sortenregister, Ernte, Bodenproben, Kulturpflanzen | Kein **Löschen/Bearbeiten** pro Zeile in Tabellen | jew. `agrar/…/liste.tsx` bzw. `schlagkartei.tsx`, `massnahmen.tsx` |
| W11 | Dünger-Mischungen | Komponenten-Zeilen: **Kein Verschieben** (Reihenfolge) | `agrar/duenger/mischungen.tsx` |
| W12 | Ernte-Liste | **Suchbegriff** wird nicht an Tabelle/Filter übergeben – Suchfeld ohne Filterwirkung | `agrar/ernte/liste.tsx` |
| W13 | Bedarfsrechner | Kein „Ergebnis speichern“ / „Als Düngeplan übernehmen“ | `agrar/duenger/bedarfsrechner.tsx` |

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

- **Diskrepanzen:** Über alle Module hinweg viele **Export**-Buttons ohne Funktion, **Toolbar-/Filter-Buttons** mit leerem `onClick` oder nur `console.log`, sowie zentrale Aktionen (Sofort-Rechnung, Prüfen/Freigeben/Verbuchen Rechnungseingang, Finance-Toolbars, LKW-Registrierung, Ein-/Auslagerung buchen, POS Fortsetzen/Löschen) nicht oder nur Platzhalter umgesetzt.
- **Workflow-Lücken:** **Lieferschein/Auftrag/Angebot:** Position löschen & Verschieben fehlen; Lieferschein: Zeile zur Bearbeitung auswählen fehlt. **Einkauf:** Kein Zeilen-Löschen/Verschieben in LS/Rechnung. **Agrar:** Viele Listen ohne Zeilen-Löschen/Bearbeiten; Ernte-Liste Suche ohne Filterwirkung. **Lager:** Ein-/Auslagerung ohne echte Buchung.
- **Mock/TODO:** Tenant/Auth-Kontext in mehreren Stamm-Masken; Lieferanten-Stamm Mock-Fallback; Agrar (PSM-Abgabe, Saatgut-Bestellung, Beratung, Wasserschutz); Lager (Bestandsübersicht, Lagerplätze, Auslagerung Charge); POS/Annahme (TSE, Offline, LKW-Registrierung).

---

*Ende der Audit-Liste. Nächster Schritt: Priorisierte Abarbeitung (z. B. zuerst Lieferschein Position löschen/verschieben, dann Sofort-Rechnung, dann Export-Buttons und Finance-Toolbars).*
