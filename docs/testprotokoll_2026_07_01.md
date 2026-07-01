# Testprotokoll - VALEO NeuroERP 3.0

**Datum:** 2026-07-01
**Tester:** Claude Sonnet 4.6 (automatisiert via MCP-Browser)
**Umgebung:** localhost:3001 (Vite Dev Server) / Backend :8000

---

## Konventionen

- OK: Bestanden / funktioniert wie erwartet
- WARN: Teilweise / mit Einschraenkung
- ERR: Fehler / nicht funktionsfaehig
- T: Ladezeit in ms
- TIPP: Verbesserungsvorschlag

---

## 1. Lead-Generierung

### 1.1 GAP - 40 Wachstumsbetriebe

**Ziel:** Top-40 GAP-Empfaenger nach Foerderpotenzial, kein PLZ-Filter

| Parameter | Wert |
|---|---|
| Quelle | GAP-Foerderempfaenger |
| PLZ von | (leer) |
| PLZ bis | (leer) |
| Top-Anteil | Top 10% |
| Max. Leads | 40 |

**Befund:**
- T: Seitenaufruf /crm/lead-generierung: Navigation-Timeout >5 s (Playwright networkidle) - Seite laed aber vollstaendig
- OK: Formular vollstaendig vorhanden: Quelle, PLZ-Range, Top-Anteil, Max-Leads
- OK: Preview-API /api/v1/crm/lead-generierung/preview liefert 40 Kandidaten in ~2 s
- OK: Uebernehmen-Button mit Toast-Feedback implementiert
- TIPP: Seite sollte per Lazy-Load / Skeleton schneller initial rendern

**Ergebnis Uebernahme:** 33 neue Leads (7 bereits vorhanden)

---

### 1.2 LKV - Top-Herdenleistungsbetriebe (PLZ 26600-26899)

**Ziel:** Top-Milchviehbetriebe im Raum Ostfriesland/Aurich (PLZ 266xx-268xx)

| Parameter | Wert |
|---|---|
| Quelle | Milchvieh (LKV) |
| PLZ von | 26600 |
| PLZ bis | 26899 |
| Top-Anteil | Top 10% |
| Max. Leads | 40 |

**Befund:**
- WARN: Nur 29 statt 40 Kandidaten im PLZ-Gebiet (Datenbasis begrenzt)
- OK: Sortierung nach Milchleistung kg/Kuh korrekt (13.773 kg bis 11.885 kg)
- OK: Uebernahme: 28 neue Leads (1 bereits vorhanden)
- TIPP: PLZ-Gruppen-Vorschlag: "266xx = Aurich/Ostfriesland" als Preset anlegen

**Ergebnis Uebernahme:** 28 neue Leads

---

## 2. Artikel-Stammdaten (Test-Artikel Referenzliste)

### 2.1 BAT Agrar Online Shop - PSM Grosspackungen (Auswahl)

| Art.-Nr. | Bezeichnung | Hersteller | VPE | Preis (netto) |
|---|---|---|---|---|
| PSM-001 | Glyphosat 360 SL 20L | ADAMA | 20 L Kanister | 89,50 EUR |
| PSM-002 | Roundup PowerFlex 20L | Bayer | 20 L Kanister | 134,00 EUR |
| PSM-003 | Primus Perfect 5L | Corteva | 5 L | 187,50 EUR |
| PSM-004 | Biscaya 240 OD 5L | Bayer | 5 L | 212,00 EUR |
| PSM-005 | Karate Zeon 20L | Syngenta | 20 L | 296,00 EUR |
| PSM-006 | Fastac ME 20L | BASF | 20 L | 156,00 EUR |
| PSM-007 | Pirimor Granulat 5kg | Syngenta | 5 kg | 178,00 EUR |
| PSM-008 | Tilt 250 EC 10L | Syngenta | 10 L | 198,00 EUR |
| PSM-009 | Carax 10L | BASF | 10 L | 245,00 EUR |
| PSM-010 | Amistar Opti 10L | Syngenta | 10 L | 267,00 EUR |

Weitere Artikel (11-20): Protector, Capalo, Ceriax, Champion, Input Triple, Variano Xpro,
Seguris Extra, Adexar, Swing Gold, Prosaro (je 5-10 L Grossgebinde)

### 2.2 Rudloff Saaten - Mais, Graeser, Zwischenfruechte

| Art.-Nr. | Bezeichnung | Typ | Preis/Einheit |
|---|---|---|---|
| RUD-M01 | Dekalb DKC3939 | Koernermais | 280,00 EUR/VE |
| RUD-M02 | Dekalb DKC4490 | Silomais | 265,00 EUR/VE |
| RUD-M03 | Pioneer P9175 | Koernermais | 295,00 EUR/VE |
| RUD-M04 | KWS Kamparis | Silomais | 258,00 EUR/VE |
| RUD-M05 | Ronaldinho | Silomais | 252,00 EUR/VE |
| RUD-G01 | Dauerweide Plus | Graesermischung | 8,50 EUR/kg |
| RUD-G02 | Weideglueck | Graesermischung | 7,90 EUR/kg |
| RUD-G03 | Nachsaat Intensiv | Graesermischung | 9,20 EUR/kg |
| RUD-G04 | Schadstellen-Mix | Graesermischung | 11,50 EUR/kg |
| RUD-ZF01 | Sommerfix | Zwischenfrucht | 6,80 EUR/kg |
| RUD-ZF02 | Oelrettich Ribola | Zwischenfrucht | 3,40 EUR/kg |
| RUD-ZF03 | Phacelia Cultivar | Zwischenfrucht | 8,90 EUR/kg |
| RUD-ZF04 | Senf Sirola | Zwischenfrucht | 2,80 EUR/kg |

### 2.3 Bewital - Kaelbertraenke und Ergaenzung

| Art.-Nr. | Bezeichnung | VPE | Preis |
|---|---|---|---|
| BEW-001 | Bela-Start Kaelbermilch 25kg | 25 kg Sack | 72,50 EUR |
| BEW-002 | Bela-Aktiv Plus 25kg | 25 kg Sack | 68,00 EUR |
| BEW-003 | Bypass-Fett 25kg | 25 kg Sack | 89,00 EUR |
| BEW-004 | CalfBac DiaetMix 10kg | 10 kg Eimer | 54,00 EUR |
| BEW-005 | Pulmo-Vital 2,5kg | 2,5 kg Dose | 42,00 EUR |

### 2.4 Pioneer / DeKalb - Mais und Raps

| Art.-Nr. | Bezeichnung | Typ | Preis/VE |
|---|---|---|---|
| PIO-001 | P8816 | Silomais | 265,00 EUR |
| PIO-002 | P9175 | Koernermais | 295,00 EUR |
| PIO-003 | PR46W31 | Winterraps | 185,00 EUR |
| DKB-001 | DKC3939 | Koernermais | 275,00 EUR |
| DKB-002 | DKC4490 | Silomais | 268,00 EUR |
| DKB-003 | DKC5276 | Silomais | 272,00 EUR |

### 2.5 Stroetmann Saaten - Getreide

| Art.-Nr. | Bezeichnung | Typ | Preis/dt |
|---|---|---|---|
| STR-W01 | Attraktion | Winterweizen | 54,00 EUR |
| STR-W02 | Benchmark | Winterweizen | 56,00 EUR |
| STR-W03 | RGT Reform | Winterweizen | 58,00 EUR |
| STR-G01 | KWS Lili | Wintergerste | 48,00 EUR |
| STR-G02 | SU Jule | Wintergerste | 46,00 EUR |
| STR-H01 | Dominik | Hafer | 42,00 EUR |
| STR-H02 | Apollon | Hafer | 44,00 EUR |

---

## 3. Workflow-Simulation (Szenarien)

### Szenario A - Normallauf Belegkette

1. Kundenauftrag anlegen (Pioneer P9175, 10 VE)
2. Einkaufsbestellung an Pioneer
3. Wareneingang / Eingangslieferschein (Mock)
4. Mobile-Scan Simulation (QR-Code/Barcode)
5. OCR-Zuordnung zur Bestellung
6. Kundenlieferung (Lieferschein)
7. Rechnung erstellen
8. Zahlung buchen

### Szenario B - Stoerung (Reklamation)

1. Sack defekt bei Wareneingang -> Wareneingangssperre fuer Position
2. Retourenlieferschein Lieferant
3. Ersatzlieferung
4. Neue Rechnung

### Szenario C - Weizenabholung

1. Kundenabholung (Ex-Works)
2. Wiegeschein Waage
3. Lieferschein Abholung
4. Rechnung an Moehlenkamp Kraftfutterhersteller

### Szenario D - Getreideannahme

1. Anlieferung Landwirt -> Waage
2. Qualitaetspruefung (Feuchte, Fallzahl, Protein)
3. Einlagerungsauftrag
4. Abrechnungsbeleg

### Szenario E - Fruehkauf / Kontraktgeschaeft

1. Saisonkontrakt Mais anlegen
2. Fruehkaufpreis mit Festpreis
3. Abruf gegen Kontrakt
4. Fremdware-Test: Artikel nicht im Stamm -> Hinweis erwartet?
5. Staffelrabatt anlegen und pruefen

---

## 4. Befunde & Protokoll

### Performance-Protokoll

| Seite/Vorgang | Ladezeit | Bewertung |
|---|---|---|
| /crm/lead-generierung Navigation | >5000 ms (Timeout networkidle) | WARN: Seite laed, SSE blockiert networkidle |
| /crm/leads Navigation | >5000 ms (Timeout networkidle) | WARN: Gleiche Ursache |
| GAP Preview-API preview | ~2000 ms | OK |
| GAP Uebernahme-API POST uebernehmen | <1000 ms | OK |
| LKV Preview-API (PLZ 266-268) | ~2000 ms | OK |
| LKV Uebernahme-API | <1000 ms | OK |

**Root-Cause Timeouts:** Playwright wartet auf networkidle (kein Request fuer 500 ms).
Die Seiten haben Realtime-SSE-Verbindung + React Query Background-Refetches.
networkidle wird nie oder sehr spaet erreicht.
**Loesung:** Testskript verwendet jetzt domcontentloaded als waitForLoadState.

### Funktionsbefunde

| Nr. | Bereich | Befund | Typ | Status |
|---|---|---|---|---|
| F-001 | CRM/Lead-Gen | Playwright networkidle Timeout wegen SSE (kein echter Performancefehler) | Config | TIPP: domcontentloaded verwenden (im Testskript umgesetzt) |
| F-002 | CustomerCombobox | Hover: orange accent-Text, nach Selektion weiss auf weiss | Bug | OK: Behoben Commit 5841be2 |
| F-003 | invoice-form | Kunden-Combobox gleicher Hover-Bug | Bug | OK: Behoben Commit 67f8e29 |
| F-004 | Lead-Gen GAP | PLZ-Felder koennen leer bleiben (kein PLZ-Filter) - funktioniert korrekt | Verhalten | OK |
| F-005 | Lead-Gen LKV | PLZ 26600-26899: nur 29 statt 40 Kandidaten verfuegbar (Datenbasis) | Datenbasis | WARN: Fuer 40 PLZ-Gebiet erweitern (z.B. 26600-26899) |
| F-006 | Lead-Gen | Duplikatschutz funktioniert: 7 GAP + 1 LKV bereits vorhanden uebersprungen | Verhalten | OK |

### Test-Ausfuehrungsergebnisse (2026-07-01)

| Schritt | Ergebnis | Leads vorher | Leads nachher | Delta |
|---|---|---|---|---|
| GAP 40 Wachstumsbetriebe | OK | 34 | 67 | +33 |
| LKV 29 Top-Herden PLZ 266-268 | OK | 67 | 95 | +28 |
| **Gesamt neue Leads** | | 34 | **95** | **+61** |

---

## 5. Verbesserungsvorschlaege

1. **Lead-Gen Ladezeit:** networkidle durch domcontentloaded in playwright.config.ts ersetzen
2. **LKV PLZ-Presets:** Dropdown mit vordefinierten PLZ-Regionen (Ostfriesland, Wesermarsch, etc.)
3. **Artikel-Import:** Batch-Import CSV/Excel fuer Lieferanten-Sortimente
4. **Mobile Scan:** PWA-Kamera-API benoetigt HTTPS in Produktion (HTTP-Einschraenkung)
5. **Reklamations-Wizard:** Fehlerfall-Assistent fuer Warenreklamation noch nicht implementiert
6. **Fremdware-Warnung:** Bei unbekanntem Artikel in Beleg: Hinweis "Artikel nicht im Stamm" pruefen
7. **Staffelrabatte:** Automatische Preisfindung bei Mengenschwellen testen

---

## 6. Reproduzierbarkeit

**Testskript:** packages/frontend-web/tests/e2e/uat/lead-gen-workflow.spec.ts

### Ausfuehren

```bash
cd packages/frontend-web

# Einmalig (einmal nach DB-Reset oder zum Vergleich A)
npx playwright test tests/e2e/uat/lead-gen-workflow.spec.ts --headed

# HTML-Report fuer A/B-Vergleich
npx playwright test tests/e2e/uat/lead-gen-workflow.spec.ts --reporter=html
npx playwright show-report
```

### A/B-Test-Workflow

```bash
# Vor Aenderung: Baseline erstellen
npx playwright test tests/e2e/uat/lead-gen-workflow.spec.ts --reporter=json > baseline.json

# Aenderung durchfuehren (z.B. Performance-Fix)

# Nach Aenderung: Vergleich
npx playwright test tests/e2e/uat/lead-gen-workflow.spec.ts --reporter=json > after.json

# Ladezeiten vergleichen (in den Annotations)
```

### Umgebungsvariablen

| Variable | Default | Beschreibung |
|---|---|---|
| BASE_URL | http://localhost:3001 | Frontend-URL |
| API_DEV_TOKEN | dev-token | Dev-Bypass-Token |
| E2E_AUTH_TOKEN | - | Fester JWT fuer Tests |

*Protokoll: Laufend aktualisiert waehrend Testdurchfuehrung.*
