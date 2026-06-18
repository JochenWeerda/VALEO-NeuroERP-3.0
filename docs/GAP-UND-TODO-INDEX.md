# GAP- und TODO-Dokumentation – Index und Konsolidierung

**Zweck:** Einheitlicher Einstieg für alle Gap-, Todo- und Plan-Dokumente. Vermeidung von Dopplungen; klare Zuordnung, was aktuell und was archiviert ist.

**Zuletzt geprüft:** 2026-06-18 (Wave-3 Produktions-Readiness, Logistik-Kette, DOM-*-004-Tiefenwelle, HRM-Payroll-Deep).
**Aggregierter Gesamtstand:** [PROJEKT-GESAMTSTAND-2026-05-27.md](PROJEKT-GESAMTSTAND-2026-05-27.md) (aktualisiert 2026-06-18).
**Geschlossen (Implementierung):** Button-UX-Audit F1–F19, E2, E4, W10, W14, W15, M1–M21, M23. TSE/Offline: Konzept in `docs/AUTH-AND-TENANT-CONCEPT.md` (M22). **Phase 1–6** abgeschlossen, siehe Phase-Completion-Reports. **Slices 006–011** abgeschlossen (XRechnung-Export, Command Palette, DSGVO Art. 30/33, Voice-Intents, Meridian-Hardcolors). **DOM-*-004-Tiefenwelle** abgeschlossen (2026-06-12). **Logistik-Kette** abgeschlossen (2026-06-12/13). **Wave-3 Produktions-Readiness** abgeschlossen (2026-06-18).
**Neu seit Mai 2026:** DOM-*-004-Welle, Logistik-Kette, Wave-2+3 Integration/Readiness-Slices, HRM-Payroll-Deep, DSGVO Art. 30/33. **Keine verbliebenen gesetzlichen Lücken** im Repo; externe Gates (ATLAS, ERiC, UAT-Unterschriften) bleiben offen.

---

## 1. Kanonische Dokumente (aktiv nutzen)

| Bereich | Dokument | Inhalt |
|--------|----------|--------|
| **GAP-Analyse (fachlich)** | [`gap/README.md`](../gap/README.md) | Einstieg GAP-Dokumentation; Verweise auf Capability Models, gaps.md, procurement-gaps.md, gaps-sales.md, gaps-crm-marketing.md, gaps-agriculture.md |
| **GAP-Übersicht** | [`gap/consolidated-overview.md`](../gap/consolidated-overview.md) | Domain-Übersicht, Maturity, Priorisierung, Roadmap |
| **GAP-Umsetzung** | [`gap/implementation-roadmap.md`](../gap/implementation-roadmap.md) | Detaillierte Implementierungs-Roadmap |
| **UX/Button-Audit** | [`.cursor/button-ux-audit-todo.md`](../.cursor/button-ux-audit-todo.md) | Diskrepanzen, Workflow-Lücken, Mock/TODO; **alle Einträge erledigt** (M9, M11–M15, E4, F18, A6/A12; Offen: –) |
| **FiBu-Suite (Design)** | [`docs/FIBU-SUITE-TODO.md`](FIBU-SUITE-TODO.md) | UX/Design-System, Maskenliste P0/P1, Ribbon vs. PageToolbar |
| **FiBu-Connectors** | [`.cursor/fibu-connectors-status.md`](../.cursor/fibu-connectors-status.md) | Lohn, Asset Ledger, Connector-Framework; **Lohn-Connector Delete: im Code implementiert** |
| **Gap-Closure-Plan** | [`.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md`](../.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md) | Phasenplan (Phase 1–6), Todo-Status pro Phase |
| **Phase-2-Report** | [`docs/PHASE-2-COMPLETION-REPORT.md`](PHASE-2-COMPLETION-REPORT.md) | Finance P1 (12 Cap.), CRM P0/P1 (4 Cap.) — Abschluss 2026-03-05 |
| **Phase-3-Report** | [`docs/PHASE-3-COMPLETION-REPORT.md`](PHASE-3-COMPLETION-REPORT.md) | Sales Domain (15+ Cap.), Procurement Konsolidierung — Abschluss 2026-03-05 |
| **Phase-4-Report** | [`docs/PHASE-4-COMPLETION-REPORT.md`](PHASE-4-COMPLETION-REPORT.md) | CRM/Marketing Erweiterung (7 Cap.) — Abschluss 2026-03-05 |
| **Phase-5-Report** | [`docs/PHASE-5-COMPLETION-REPORT.md`](PHASE-5-COMPLETION-REPORT.md) | Finance + Procurement P2/P3 — Abschluss 2026-03-05 |
| **Phase-6-Report** | [`docs/PHASE-6-COMPLETION-REPORT.md`](PHASE-6-COMPLETION-REPORT.md) | Agriculture Backend + Erweiterung — Abschluss 2026-03-05 |
| **GAP-Closure Summary** | [`docs/GAP-CLOSURE-SUMMARY.md`](GAP-CLOSURE-SUMMARY.md) | Konsolidierte Übersicht Phasen 1–6, Stand 2026-03-05 |
| **GoBD/Audit-Gaps** | [`.cursor/plans/gaps-schliessen-audit-gobd.plan.md`](../.cursor/plans/gaps-schliessen-audit-gobd.plan.md) | GoBD-Konformität, Risiko-Maßnahmen, Datenmodell/APIs (kein Todo-Array, inhaltlicher Plan) |
| **Auth/Tenant/TSE/Offline** | [`docs/AUTH-AND-TENANT-CONCEPT.md`](AUTH-AND-TENANT-CONCEPT.md) | Backend/Frontend Tenant & User; Kunden-Suche; TSE- und Offline-Queue-Konzept (Mock/TODO M22, M23) |
| **Geplant-Index** | [`docs/GEPLANT-INDEX.md`](GEPLANT-INDEX.md) | Überall wo „geplant“ vorkommt — Umsetzungspotenzial und Priorisierung |

---

## 2. Verifizierung (Stichprobe 2025-03-05)

Einige Einträge aus dem Button-UX-Audit wurden im Code geprüft. Ergebnis:

| ID | Audit-Aussage (vorher) | Code-Befund | Aktion |
|----|-------------------------|-------------|--------|
| **F15** | Fortsetzen/Löschen nur lokal | `suspended-sales.tsx`: `handleDelete` ruft `api.delete('/api/v1/pos/suspended-sales/${saleId}')` auf | In Audit auf **Erledigt** gesetzt |
| **W15** | Kein Backend-Aufruf Ein-/Auslagerung | `einlagerung.tsx`: `apiClient.post('/api/v1/lager/einlagerung', …)`; `auslagerung.tsx`: `api.post('/api/v1/lager/auslagerung', …)` | In Audit auf **Erledigt** gesetzt (F9 bestätigt) |
| **M17** | TODO: API call to save OP-Kreditor | `finance/op-kreditoren.tsx`: `createMutation` mit `apiClient.post('/api/v1/finance/open-items', payload)` | In Audit als **erledigt** geführt (M17 aus Tabelle Mock/TODO streichen oder „API vorhanden“ vermerken) |
| **F2** | Bank-Import kein onClick | Dialog + POST /finance/bank-statements/import implementiert | **Erledigt** |
| **F4** | Zahlungsvorschläge Freigeben ohne Handler | onClick → navigate /fibu/zahlungslaeufe | **Erledigt** |
| **F5** | Verbindlichkeiten „Zahlungslauf planen“ kein onClick | onClick → navigate /fibu/zahlungslaeufe | **Erledigt** |
| **E2** | Import Toast „kommt in Kürze“ | `bestellungen-liste.tsx` etc.: `onImport` mit Dialog + POST-Stub | **Erledigt** (Stub) |
| **M18** | Echte Kunden-Suche | `finance/invoice-form.tsx`: Combobox + GET /api/v1/crm/customers?search= | **Erledigt** |
| **Tenant/Auth** | Feste tenant_id/user_id | CRM, zahlungseingaenge, workflows, bestellung/saatgut/duenger-stamm, chart-of-accounts, debitoren-stamm: useTenant/useAuth | **Erledigt** |
| **Lohn-Connector Delete** | Status „pending“ | `lohn-connector.tsx`: `handleDelete` + `deleteRun.mutate(id)` vorhanden | In fibu-connectors-status auf **implementiert** gesetzt |

---

## 3. Weitere Gap-/Roadmap-Dokumente (Referenz)

- **docs/roadmap/** – Sprint- und Lieferpläne (z. B. finance-suite-sprint-plan-s1-s6.md, a-eins-gap-backlog.md)
- **docs/roadmap/status/** – Statusberichte (gap-delivery-plan, gap-remediation-roadmap, must-have-gap-audit)
- **docs/archive/** – Ältere Gap-Analysen (VALEO-ERP-*, GAP-ANALYSIS-COMPLETE.md, VALEO-NEUROERP-TODO-STATUS-2025.md) → nur noch Referenz, nicht als aktueller Stand
- **swarm/** – Missions- und Sprint-Pläne (gap-closure-orchestration.md, P0-GAPS-COMPLETE.md, status/finance-gaps-completion-report.md)

Für **tagesaktuellen Gap-Stand** die kanonischen Dokumente in Abschnitt 1 nutzen.

---

## 4. Nächste Schritte (Plan-Fortsetzung)

- **Button-UX-Audit:** Abgeschlossen; keine offenen Punkte. Abschnitt 5 in `.cursor/button-ux-audit-todo.md` dient nur noch als Referenz.
- **Fachliche Gaps (inhaltliche Lücken):** Für Priorisierung und Detail-Gaps die **gap/*.md**-Dokumente nutzen: [gap/README.md](gap/README.md), [gap/gaps.md](gap/gaps.md), [gap/procurement-gaps.md](gap/procurement-gaps.md), [gap/gaps-sales.md](gap/gaps-sales.md), [gap/gaps-crm-marketing.md](gap/gaps-crm-marketing.md), [gap/gaps-agriculture.md](gap/gaps-agriculture.md).
- **Gap-Closure-Plan:** Phasen 2–6 siehe `.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md`; Phase 1 Agrar P0 „in_progress“, übrige Phasen „pending“.
- **Tests:** Geänderte Flows (E4, F18, A6/A12, USt-ID) können in `packages/frontend-web/src/__tests__/` (Vitest) bzw. `tests/` (pytest) abgedeckt werden.

---

## 5. Empfehlung: Pflege

1. **Button-UX-Audit:** Bei Abarbeitung Eintrag auf „Erledigt“ setzen und ggf. kurze Code-Referenz (Datei/Zeile) ergänzen.
2. **Gap-Closure-Plan:** Phasen-Status (pending/in_progress/completed) in der Plan-Datei halten; große Meilensteine ggf. in `gap/implementation-roadmap.md` spiegeln.
3. **Neue Gaps/TODOs:** Primär in `gap/*.md` (fachliche Gaps) bzw. `.cursor/button-ux-audit-todo.md` (UI/Button/Mock) eintragen.
4. **Geplant-Index:** Bei Abarbeitung von „geplant“-Stellen: `docs/GEPLANT-INDEX.md` pflegen, Status aktualisieren.
4. **Archiv:** Abgelöste oder historische Analysen nach `docs/archive/` verschieben und im Index mit „(archiv)“ kennzeichnen.

---

*Dieser Index ersetzt keine inhaltlichen Gap-Analysen; er bündelt nur Einstiegspunkte und dokumentiert die durchgeführte Konsolidierung.*
