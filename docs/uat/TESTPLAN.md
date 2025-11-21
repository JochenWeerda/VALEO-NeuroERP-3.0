# VALEO-NeuroERP - UAT Testplan

## Überblick

**Ziel:** Vollständiger User Acceptance Test (UAT) der VALEO-NeuroERP Suite zur Verifikation der Production Readiness.

**Scope:** 188 Seiten inkl. 3-Ebenen-Fallback-System (PoC: 5 Domains / ~33 Seiten)

**Datum:** 2025-10-16  
**Version:** 1.0  
**Status:** In Vorbereitung

---

## Testumfang

### Funktional
- **CRUD-Operationen:** Create, Read, Update, Delete (4-10 Datensätze je Maske)
- **Workflow/Status:** Erlaubte Statusübergänge, unzulässige Aktionen blockiert
- **Print/Export:** PDF-Render, CSV/XLS/DATEV/SEPA/Label-Export
- **Navigation:** Tabs vor/zurück, Breadcrumb, Dirty-Guard
- **Validierung:** Zod-Fehler, Blocker vs. Warnung

### Technisch
- **3-Ebenen-Fallback:**
  - Level 1: Seitenspezifischer onClick-Handler
  - Level 2: useListActions-Hook
  - Level 3: GlobalButtonHandler
- **RBAC:** admin, power-user, readonly Rollen
- **Stabilität:** Keine Crashes, keine 500er, Timeout < 2s (P95)
- **Logs:** Console, Network (HAR), Backend-Logs

### PoC-Domains (Initial)
1. **Sales:** Angebote, Order, Delivery, Invoice
2. **Agrar/PSM:** PSM-Liste, Saatgut, Dünger
3. **CRM:** Kontakte, Leads, Aktivitäten
4. **Finance:** Buchungsjournal, Debitoren, OP
5. **Inventory:** Artikel, Lager, Charge

---

## Testdaten & Umgebung

### Test-Mandant
- **Tenant-ID:** `QA-UAT-01`
- **Datenbank:** Eigene SQLite/PostgreSQL-Instanz (isoliert)
- **Seed-Daten:** 4-10 Datensätze pro Domain (automatisch via API)

### Test-Rollen
| Rolle        | E-Mail                   | Rechte                          |
|--------------|--------------------------|----------------------------------|
| admin        | admin@example.com        | Alle Rechte, alle Domains       |
| power-user   | power@example.com        | Domänen-spezifisch write        |
| readonly     | readonly@example.com     | View + Export only              |

### Randfälle (pro Maske)
- Fehlende Pflichtfelder
- Doppelte Schlüssel (z. B. Artikelnummer)
- Über-/Unter-Mengen
- Falsche Einheiten
- Statusverletzungen (z. B. Rechnung vor Lieferschein)
- Netzwerk-Delay (simuliert: 300-800ms RTT)

---

## Testablauf

### A) Sichtprüfung & Fallback-Verifikation
1. **Button-Wirkung:** Click wirkt genau einmal (keine Doppel-Auslösung)
2. **Fallback-Kette:**
   - Seitenskript vorhanden? → Level 1 (Console: `FB:LEVEL=1`)
   - Sonst useListActions? → Level 2 (`FB:LEVEL=2`)
   - Sonst GlobalButtonHandler → Level 3 (`FB:LEVEL=3`)
3. **Toasts/Bestätigungen:** Konsistent, korrekte Texte

### B) CRUD & Validierung
4. **Create:** 4–10 neue Datensätze (Happy Path + Randfälle)
5. **Read/List:** Filter, Suche, Paging; leere & große Listen
6. **Update:** Pflichtfelder, Optimistic Locking (2. Fenster)
7. **Delete/Restore:** Bestätigung, Soft-Delete, Audit-Log
8. **Validierung:** Zod-Fehler sichtbar, Blocker vs. Warnung

### C) Workflow/Status
9. **Statuspfade:** Erlaubte Übergänge ok, unzulässige blockiert (klarer Fehlertext)

### D) Druck/Export
10. **Print:** PDF korrekt, Nummernkreis, Journal-Eintrag
11. **Export:** CSV/XLS/EDI/SEPA/DATEV/Label – Datei ok, Download, Encoding

### E) Navigation/UX
12. **Tabs vor/zurück:** State-Erhalt, Dirty-Guard greift
13. **Breadcrumb/Zurück:** Keine Loops, keine 404
14. **A11y-Basics:** Fokus, Tastatur, ARIA-Label

### F) RBAC/Permissions
15. **readonly:** Keine Schreibaktionen (403 + Toast)
16. **power-user:** Nur erlaubte Domains schreibbar
17. **admin:** Alles sichtbar & ausführbar

---

## Fehlererfassung

**Pflicht-Schema (JSON):**

```json
{
  "id": "UAT-<AUTO-ID>",
  "seite": "<Domain/Submodule/PageName>",
  "rolle": "<admin|power-user|readonly>",
  "schritt": "<Create|Update|Delete|Print|Export|Workflow|Nav|RBAC|Fallback>",
  "schweregrad": "<S1-Blocker|S2-Hoch|S3-Mittel|S4-Niedrig>",
  "kurztitel": "…",
  "beschreibung": "Erwartet: … / Ergebnis: …",
  "reproduktion": ["Schritt 1", "Schritt 2", "…"],
  "umgebung": {
    "browser": "Chrome 141",
    "url": "…",
    "zeit": "2025-10-16T14:30:00Z",
    "tenant": "QA-UAT-01",
    "build": "<git-commit>"
  },
  "artefakte": {
    "screenshot": "playwright-tests/artifacts/…/UAT-xxxx.png",
    "har": "playwright-tests/artifacts/…/UAT-xxxx.har",
    "console": "playwright-tests/artifacts/…/UAT-xxxx.log"
  }
}
```

### Schweregrade
- **S1 Blocker:** Crash, Data-Loss, 500/Backend down, Workflows gestoppt
- **S2 Hoch:** Kernfunktion fehlerhaft (Speichern/Print/Export)
- **S3 Mittel:** Fehllogik, falsche Meldung, UI-Glitches mit Workaround
- **S4 Niedrig:** Kosmetisch, Text/Abstand, nicht-blockierender Edge-Case

---

## Abnahmekriterien (Exit-Criteria)

- **0× S1** (Blocker) offen
- **0× S2** (Hoch) offen
- Alle **S3/S4** dokumentiert, priorisiert, haben Workarounds
- **Coverage ≥ 95 %** der Matrix grün (siehe `COVERAGE-MATRIX.csv`)
- **Print/Export** fehlerfrei auf allen Seiten (wo vorgesehen)
- **Fallback-System:** Mind. 1 Seite pro Level (1/2/3) erfolgreich getestet

---

## Abschluss-Artefakte

1. **UAT-Summary:** `docs/uat/UAT-SUMMARY.md` (KPI, Tests gesamt, grün/rot, nach Domain)
2. **Bug-List:** `docs/uat/BUGLIST.json` (alle Fehler, normiert)
3. **Coverage-Matrix:** `docs/uat/COVERAGE-MATRIX.csv` (Seite × Rolle × CRUD × Workflow × Print × Export × Nav × FallbackLevel)
4. **Top-5 Crash-Ursachen:** + Handlungsempfehlungen
5. **Langsame Endpoints:** > 2s P95 mit Pfad & Payload-Hinweis

---

## Ausführung

### Automatisiert (Playwright)
```bash
# Smoke-Tests (schnell)
pnpm test:e2e:smoke

# Full UAT
pnpm test:e2e:full

# Fallback-Verifikation
pnpm test:e2e:fallback

# Report anzeigen
pnpm test:e2e:report
```

### Manuell
1. Checklisten verwenden: `docs/uat/checklisten/<DOMAIN>.md`
2. Fehler in `BUGLIST.json` eintragen
3. Coverage-Matrix aktualisieren

---

## Kontakt & Review

**Test-Leitung:** QA-Team  
**Review-Zyklus:** Täglich (während UAT-Phase)  
**Eskalation:** S1/S2 sofort an Dev-Team

---

**Status:** ✅ Bereit für UAT-Start

