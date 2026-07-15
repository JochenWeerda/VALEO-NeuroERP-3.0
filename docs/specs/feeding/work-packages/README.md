---
title: "Fuetterungsberatung — 240 vertikale TDD-Arbeitspakete"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# Arbeitsprogramm

Jedes Paket ist einzeln claimbar und liefert ein pruefbares Nutzerergebnis. Die zehn Pakete je Capability sind keine getrennten Technikphasen: jedes durchlaeuft die jeweils betroffenen Schichten vertikal und folgt Red → Green → Refactor → Regression. Aufwand ist eine Vor-Refinement-Schaetzung, kein Terminversprechen.

| Pakete | Capability | Requirements |
|---|---|---|
| 001–010 | [Betriebsakte und Zugriffsraum](01-organisation.md) | FEED-BUS-001/002, FEED-RBAC-003/004 |
| 011–020 | [Tiergruppen und Gruppenhistorie](02-tiergruppen.md) | FEED-HERD-001/002/003 |
| 021–030 | [Naehrstoffe, Einheiten und Rundung](03-einheiten.md) | FEED-MAT-003, FEED-LAB-003 |
| 031–040 | [Futtermittel und Referenzwerte](04-futtermittel.md) | FEED-MAT-001/002 |
| 041–050 | [Futteranalysen und Provenienz](05-analysen.md) | FEED-LAB-001/002/004 |
| 051–060 | [Bedarfs- und Bewertungssysteme](06-bedarf.md) | FEED-REQ-001/002 |
| 061–070 | [Rationsversion und Lifecycle](07-ration-lifecycle.md) | FEED-RAT-001/002/005 |
| 071–080 | [Produktiver Rationseditor](08-editor.md) | FEED-RAT-003/004, FEED-UI-002 |
| 081–090 | [Bewertung und Warnungen](09-warnungen.md) | FEED-EVAL-001/002 |
| 091–100 | [Optimierung und Infeasibility](10-optimierung.md) | FEED-OPT-001/004/005 |
| 101–110 | [Variantenvergleich und Entscheidung](11-varianten.md) | FEED-CMP-001, FEED-RAT-005 |
| 111–120 | [Fuetterungsplan und Mischfolge](12-plan.md) | FEED-PLAN-001/002 |
| 121–130 | [Ist-Fuetterung und Rueckmeldung](13-ausfuehrung.md) | FEED-ACT-001/002/004 |
| 131–140 | [Bedarf, Bestand und Reichweite](14-versorgung.md) | FEED-SUP-001/002/003 |
| 141–150 | [Kontrollierte Einkaufsuebergabe](15-einkauf.md) | FEED-SUP-003 |
| 151–160 | [Leistung und Wirkungscontrolling](16-leistung.md) | FEED-PERF-001/002/003/004 |
| 161–170 | [Beratungsfall und Beobachtung](17-beratung.md) | FEED-CONS-001 |
| 171–180 | [Massnahmen und Wiedervorlage](18-massnahmen.md) | FEED-CONS-002, FEED-COLLAB-002 |
| 181–190 | [Berichte und Nachweise](19-berichte.md) | FEED-REP-001/002/003 |
| 191–200 | [Zusammenarbeit und Benachrichtigung](20-zusammenarbeit.md) | FEED-COLLAB-001/002 |
| 201–210 | [Laborintegration und Quarantaene](21-labor.md) | FEED-INT-001, FEED-LAB-002 |
| 211–220 | [Herdenmanagement-Delta-Sync](22-herd-data.md) | FEED-HERD-004, FEED-INT-001 |
| 221–230 | [Mixer- und agrirouter-Austausch](23-mixer.md) | FEED-PLAN-003, FEED-INT-002/003 |
| 231–240 | [KI-Agenten und Governance](24-agenten.md) | FEED-UI-003, FEED-NFR-SEC |
