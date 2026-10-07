---
title: Executive Summary Gap-Stand VALEO NeuroERP 2026-10
type: reference
audience: [management, produkt, agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
description: Aktualisierte Gap-/Reife-Übersicht — ersetzt docs/_internal/archive/gap/executive-summary.md (2025-01, ~38 Prozent).
---

# Executive Summary — Gap-Stand 2026-10-07

**Ersetzt:** [`docs/_internal/archive/gap/executive-summary.md`](../_internal/archive/gap/executive-summary.md) (2025-01-27, „~38 % Maturity“) und die zugehörigen Domain-Gaps derselben Welle.

**Quellen dieses Stands:**

- [Open Gaps](../project-context/open-gaps-and-known-issues.md) (laufend)
- [L3-Vollinventur](../design/l3-full-mask-functional-gap-inventory.md) (kein P0-Funktionsgap zur erreichbaren L3-Referenz)
- [Domain-Depth Closure](../project-context/domain-depth-plan-2026-05-17.md) (Welle 2026-05/06)
- [Usability-Dossier](../quality-assurance/usability-erp-vergleichsdossier-20261007.md) (Stufe-1 Audit 2026-10-07)
- Workboard-Abnahmen Oktober 2026 (Lead/PDF, Maskenaktionen, Mandanten-Finance-Teil, Logistik-Deklarationen)

---

## 1. Kernbotschaft

Die 2025er Aussage „~38 % funktional vs. Enterprise-ERP“ ist **überholt**.

VALEO ist 2026 als **Landhandel-Vollsuite** mit breiter Domänenabdeckung, ~99 nativen ScreenDefinitions, leerer `BEKANNTE_LUECKEN`-Liste für Maskenaktionen und repo-seitig geschlossener L3-Kernkette zu bewerten — **nicht** als frühes Skeleton gegen SAP-100 %.

Was 2025 als P0 fehlte (Payment-Match, AP-Rechnungen, Wareneingang, Periodensteuerung …), ist in großen Teilen **vorhanden oder teilreif**. Die kritischen offenen Themen verschieben sich zu:

1. **Integrität & Wahrheit** (Journal/Close/Bank/Agent-Guards, keine Scheinbuchungen)
2. **Kanonisierung** (Router-Doppelgruppen, Framework-Doppelung Masken)
3. **AI-native Zukunft** (agentic Finance, MCP-Schreibparität, lokale OCR, Tax-Skills)
4. **Externe Gates** (UAT, TSE, DATEV-Cutover, Hardware-Waage, Zertifikate)

---

## 2. Domänenreife (Landhandel-SoR)

Skala: **hoch** = produktionsnah nutzbar mit bekannten Restgaps · **mittel** = Kern da, Integrität/UX/IA unvollständig · **dünn** = Stub/Fragment oder starke externe Abhängigkeit.

| Domain | Reife 2025-01 (Archiv) | Reife 2026-10 | Kommentar |
|---|---|---|---|
| Verkauf / O2C | ~40 % Partial | **hoch** | Belegkette, Kreditlimit, Sammelbelege; Framework-Konsistenz Rest |
| Einkauf / S2P | 35 % / viele No | **hoch–mittel** | 3-Wege, RFQ, Avis/WE; Router-/Compat-Rest, Mandantenfixes 10/2026 |
| Finance / FiBu | 48 %, viele P0 No | **mittel** | Module da; Close/Journal/Bank/Agentik = Top-Risiko |
| CRM / Marketing | ~30 % | **hoch** | KIM-360, Lead kanonisch (ADR-078), Pipeline; MCP-Schreiben Rest |
| Lager / WMS | (Archiv schwach) | **hoch** | Bestand, Inventur, FEFO, Fremdware laut L3-Inventur |
| Agrar / Ernte / Waage | Archiv separat | **hoch** | Branchenstärke; Hardware-/Voice-Gates |
| Logistik / Fuhrpark | — | **hoch** | Tour/Fracht/Capture-Aktionen deklariert |
| Personal / Bewerbung | — | **hoch–mittel** | Rollen/DSGVO; UI-Rollen Rest |
| Compliance / Meldewesen | — | **mittel** | DE-Pfade stark; kein Tax-Skill-MCP |
| POS / Portal | — | **mittel** | Vorhanden; Channel-UX / TSE extern |
| KI / Agent / MCP | — | **mittel–dünn** | Voice+~78 Actions; unter ERPClaw/Light-Agentik |

Detailzeilen: [domain-maturity-matrix-20261007.csv](domain-maturity-matrix-20261007.csv).

---

## 3. Was aus der 2025er P0-Liste geworden ist

| 2025 P0 (Archiv) | Stand 2026-10 |
|---|---|
| FIBU-AR-03 Zahlungseingänge & Matching | **Vorhanden** (Payment-Matching-UI/Services); Bank-Reconciliation-Proof noch in Arbeit |
| FIBU-AP-02 Eingangsrechnungen | **Vorhanden**; Mandanten-/Rollenreparatur 10/2026 |
| FIBU-GL-05 Periodensteuerung | **Teilweise/hoch** — Perioden-Guard im Journal-Service; weitere Schreiber offen |
| FIBU-COMP-01 GoBD / Audit UI | **Teilweise** — Audit/Docflow vorhanden; globale GoBD-Abnahme offen |
| PROC-GR-01 Wareneingang | **Vorhanden** (Avis→WE u. a.) |
| PROC-IV-02 2/3-Wege-Abgleich | **Vorhanden** (Repo Closure-Welle) |
| PROC-PO-02 PO-Änderung/Storno | **Teilweise–vorhanden** |
| PROC-REQ-01 Bedarfsmeldung | **Teilweise–vorhanden** |

Fazit: Die alten P0-„fehlt komplett“-Zeilen sind als aktuelle Wahrheit **ungültig**.

---

## 4. Aktuelle Top-Gaps (ersetzt 2025er P0)

### P0 — Wahrheit / GoBD-nah

| ID | Gap | Tracker |
|---|---|---|
| FIN-CLOSE | Echter Kassen-/Tagesabschluss ohne Scheinbuchung | Open Gaps CASH-CLOSE |
| FIN-JOURNAL | Consumer-Atomizität, Hash/Schema, fremde Journal-Schreiber | Open Gaps JOURNAL-* |
| FIN-BANK | Bank-Reconciliation Proof / Migrations-Merge | Workboard BANK-RECONCILIATION |
| FIN-AGENT | Agentic Finance unter Policy + immutable Agent-Ledger-Muster | Usability U-C06-01/02 |

### P1 — Kanon / UX / Agent

| ID | Gap | Tracker |
|---|---|---|
| API-DUP | ~30 Router-Doppelgruppen Rest | CI-RUN / OpenAPI |
| MASK-FW | Parallele Masken-Frameworks abschmelzen | Usability U-C02-01 |
| MCP-WRITE | MCP/Voice-Schreibparität zu UI | Open Gaps / U-C02-02 |
| ACTION-DEN | Action-Registry-Dichte (SD→Actions) | Usability U-C10-01 |
| OCR-LOCAL | Lokale OCR/Vision (TaxHacker-Muster) | Usability U-C10-02 |
| TAX-MCP | Zitierbare Steuer-/Melde-Skills | Usability U-C08-01 |
| FIN-IA | `finance`/`fibu` Navigationskonsolidierung | Usability U-C06-03 |

### Extern (nicht Repo-P0)

DATEV-Cutover, TSE/DSFinV-K-Prüfwerkzeug, ERiC/ATLAS-Zertifikate, Hardware-Waage, Endnutzer-UAT/SUS Stufe 2.

---

## 5. Vergleich zu Referenzsystemen (kurz)

| Referenz | Aussage 2026-10 |
|---|---|
| zvoove/L3 | Funktionsparität Kernkette repo-seitig ohne P0-Gap; Gewohnheit/UX weiter pflegen |
| SAP/Oracle/Dynamics | Breiteres Ökosystem & Copilot-Reife; VALEO gewinnt Time-to-Value + Agrar |
| Odoo | Modularität/AI leicht; VALEO tiefer Landhandel |
| Light | Finance-Agentik voraus; kein Ops/Waage — Komposition, kein Ersatz |
| ERPClaw / OpenLedger / TaxHacker / OpenAccountants | Muster für Actions, Ledger-Guards, lokale OCR, Tax-MCP |

Ausführlich: [Usability-Vergleichsdossier](../quality-assurance/usability-erp-vergleichsdossier-20261007.md).

---

## 6. Was bewusst nicht mehr gilt

- Gesamt-Maturity **~38 %** (2025-01 Executive Summary)
- „12–15 Capabilities fehlen komplett“ als aktuelle P0-Liste
- Roadmap „38 % → 80 %“ aus Swarm-Orchestrierung 2025 als Steuergröße
- SAP-Fiori „~12 % App-Abdeckung“ (2025 Repo-Archive) als Produktstatus

Diese Zahlen bleiben im Archiv **als historische Momentaufnahme** lesbar.

---

## 7. Nächste Steuerung

1. P0 Finance-Wahrheit vor Feature-Breite.
2. Gap-Hub + Open Gaps als einzige Priorisierungsquellen.
3. Quartalsweise Domänenmatrix aktualisieren (nächster Termin vorgeschlagen: 2027-01).
4. Stufe-2 SUS nach Schließen der Finance-Blocker.
