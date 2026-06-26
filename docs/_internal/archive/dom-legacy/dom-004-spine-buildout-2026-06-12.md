# DOM-*-004 Spine-Ausbau — Gesamtübersicht (2026-06-11/12)

Konsolidierte Dokumentation der `DOM-*-004`-Welle: **alle fünf Domänen-Spines auf
voller Tiefe** (Slices `.2`–`.5`), aufbauend auf den `.1`-Spines vom 2026-06-10.
Aufteilung der parallelen Arbeit:

- **Claude:** CON, SALES, FIN, DOC (je `.2`–`.5`)
- **Cursor:** PROC (`.2`–`.5`) + PROC-RFQ + COMPAT-GOV/INV-STOCK-Governance

Stand: gepusht auf `origin/main` und `origin/develop` (FF), HEAD `119f7b14c`,
ein Alembic-Head `merge_doc_proc_20260612`, Backend `healthy`.

## Arbeitsmuster (je Slice)
Reine, testbare Kernlogik → DB-Service → fail-closed-Endpoints (HTTP 422) → idempotenter
Seed → Frontend (Picker/Arbeitsraum, Mutation-Guard + Toast) → Nav + Route-Alias +
`routes:generate` → Unit-Tests → **Live-Verifikation gegen den Dev-Stack mit DB-Restore**
→ Domänen-Doku → Workboard-Block → fokussierter Commit. Durchgehend `tsc 0`, ESLint
clean. `.5` je mit Playwright-`@smoke` + Live-UAT-Skript (`--execute`, mit Cleanup).

## Spines im Überblick

### CON — Kontrakte (`docs/dom-con-004-*`, UAT `dom-con-004-uat-2026-06-11.md`)
| Slice | Inhalt | Kern |
|---|---|---|
| 004.2 | Fixierungs-Arbeitsraum + MATIF-Bewertung | `kon_contract_fixing`, `matif_quote`; Mark-to-Market |
| 004.3 | Engagement-Sicht + Kontraktmahnung | Netto-Position je Artikel/Partei; `kon_contract_reminder` |
| 004.4 | Settlement-Übergabe + Storno | Bewegung→Abrechnung; Fixierungs-/Bewegungs-Storno |
| 004.5 | E2E-Smoke + Lifecycle-UAT | Fixierung→Engagement→Settlement→Storno |
Services: `contract_{fixing,engagement,settlement}_service.py`. API-Prefix `/contracts`.

### SALES — Order-to-Cash (`docs/dom-sales-004-*`, UAT `dom-sales-004-uat-2026-06-11.md`)
| Slice | Inhalt | Kern |
|---|---|---|
| 004.2 | Positions-Match Auftrag↔Lieferschein | reuse `match_position`; Teil-/Überlieferung |
| 004.3 | Kreditlimit-Prüfung + Billing-Status | Limit vs. offene Exposure, Ampel |
| 004.4 | Storno/Gutschrift durchgängig | Lieferungs-Storno fließt in den Match zurück |
| 004.5 | O2C-Smoke + Lifecycle-UAT | Match→Kreditampel→Storno-Rückfluss |
Services: `sales_{match,credit,storno}_service.py`. API-Prefix `/sales`.

### FIN — Offene Posten / FIBU (`docs/dom-fin-004-*`, UAT `dom-fin-004-uat-2026-06-11.md`)
| Slice | Inhalt | Kern |
|---|---|---|
| 004.2 | Mahnlauf + Mahnstufen-Eskalation | `dunning_notices`; Default-Regeln |
| 004.3 | Zahlungseingang / OP-Auszifferung | reduziert `offene_posten.offen`; Skonto |
| 004.4 | Periodenabschluss + Storno-Konsistenz | `finance_accounting_periods`; Reife-Gate |
| 004.5 | DATEV-Export + E2E/UAT | Buchungsstapel-CSV (vereinfacht) |
Services: `finance_{dunning,clearing,period,datev}_service.py`. API-Prefix `/finance`.

### DOC — GoBD-Nachweisraum (`docs/dom-doc-004-*`, UAT `dom-doc-004-uat-2026-06-11.md`)
| Slice | Inhalt | Kern |
|---|---|---|
| 004.2 | Artefakt-Upload + Versionierung + Freigabe | SHA-256; entwurf→freigegeben→archiviert |
| 004.3 | Bescheid/Rückmeldung + Wiedervorlage | `document_followups`; Worklist überfällig |
| 004.4 | GoBD-Exportpaket + Paperless-Liveprobe | Manifest + Prüfsumme; DMS-Probe |
| 004.5 | E2E-Smoke + Lifecycle-UAT | Upload→Freigabe→Wiedervorlage→GoBD-Manifest |
Services: `docflow_{artifact,followup,gobd}_service.py`. API-Prefix `/docflow/evidence`.

### PROC — Beschaffung / 3-Wege-Match (Cursor; `docs/dom-proc-004-*`, UAT `dom-proc-004-uat-2026-06-11.md`)
3-Wege-Match (Rechnungsstufe), Folgeaktionen/Reklamation, ERS (Gutschriftsverfahren),
PROC-RFQ-001 (RFQ produktionsreif). Migrationen `proc_three_way_invoice`,
`proc_follow_up`, `proc_ers_credit`, `proc_rfq`.

## Querschnitt
- **Backend-Crash-Loop behoben (2026-06-11):** zwei offene Abend-Heads brachten
  `init_db.py upgrade head` (Singular) zum Scheitern → Backend-Crash-Loop; per
  Merge-Migration behoben.
- **Alembic Single-Head:** parallele DOC- (Claude) und PROC- (Cursor) Branches
  zweigten bei `con_settlement_storno_20260611` ab → zwei Heads; `merge_doc_proc_20260612`
  führt sie zusammen → genau ein Head, `init_db` läuft durch (verifiziert per Neustart).
- **Governance (Cursor):** Release-Kompatibilitätsmatrix, Toolchain-Pins,
  `stock_movements` kanonisch (`articles.py`/`pos_retoure.py` → `inventory_stock_movements`).

## Ehrlich offen / extern gegated
- **Externe Gates** (nicht im Repo abschließbar, ehrlich ausgewiesen, kein Schein-OK):
  zertifizierter DATEV-EXTF + Steuerberater-Cutover (FIN); DMS-/Paperless-Liveprobe
  (DEV ohne `PAPERLESS_URL`).
- **Tiefe FIBU-Buchung:** Auszifferung/Settlement führen Konten-/Beleg-Verträge, die
  finale Journal-Gegenbuchung bleibt Folgeschritt (`finance_invoices`/`credit_limits`
  fehlen in DEV → SALES-004.3 self-contained gebaut).
- **Playwright-`@smoke` lokal:** gemeinsame Login-Fixture greift nur gegen den
  CI-Preview-Build (:4173), nicht den Vite-Dev-Server (:3000) — gilt für alle Specs;
  fachlicher Nachweis daher je über die grünen Live-UATs.

## Verifikation
- ~90 neue Backend-Unit-Tests (reine Logik) grün; Frontend `tsc 0`, ESLint clean.
- Vier Live-UAT-Skripte mit `--execute` + DB-Restore: `scripts/uat/{con_contract_lifecycle,
  sales_o2c_lifecycle,fin_op_lifecycle,doc_nachweisraum_lifecycle}_uat.py` (+ PROC `proc_match_lifecycle_uat.py`).
- Robustheits-Fund vom DOC-UAT behoben: Fremd-`artifactType` → 500 (DB-CHECK) →
  Vorab-Validierung → 422.
