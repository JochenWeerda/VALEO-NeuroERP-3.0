# Top-50 Gap Backlog 2026-03-06 (Landhandel, Genossenschaft, Agrarkonzerne)

**Strategischer Kontext:** [2026-03-06-valeo-spitzenposition-konsolidiert.md](2026-03-06-valeo-spitzenposition-konsolidiert.md) – Kurzfazit, Wettbewerbsvergleich, 90-Tage-Priorisierung

**Arbeitsaufteilung:** [2026-03-06-arbeitsaufteilung-codex-hauptstrang.md](2026-03-06-arbeitsaufteilung-codex-hauptstrang.md) – 30 % Codex (Parallel Chat), 70 % Hauptstrang, einheitliche Statuskontrolle

**Zielbild:** [target-state-landhandel-erp.md](../../architecture/target-state-landhandel-erp.md) – verbindliche Leitplanke für Produktkern, Architektur und Priorisierung.

## Ziel
Dieses Backlog priorisiert die fehlenden Faehigkeiten, um VALEO NeuroERP auf Spitzenniveau gegenueber ServiceERP, a.amic, Odoo, SAP und Oracle zu bringen. Fokus: End-to-End Prozessabdeckung, AI-first Workflows, Agent-Interoperabilitaet, UUIX, Performance, Parallelverarbeitung.

## Bewertungslogik
- Prioritaet: P0 (kritisch), P1 (hoch), P2 (mittel)
- Aufwand: S (1-2 Wochen), M (2-4 Wochen), L (4-8 Wochen), XL (8+ Wochen)
- Horizon: H1 (0-90 Tage), H2 (3-6 Monate), H3 (6-12 Monate)
- KPI-Typen: Produktivitaet, Qualitaet, Performance, Adoption, Compliance

## Block 001-010: Prozessabdeckung Kern Landhandel (P0)

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 001 | E2E Kontrakt->Annahme->Qualitaet->Settlement ohne Medienbruch | >=95% Vorgaenge ohne manuelle Nebenliste | L | Workflow Core, Stammdaten | P0 | H1 |
| 002 | Vollstaendige Waage/Annahme-Masken fuer alle Warenfluesse | 100% Annahmearten ueber produktive Maske | M | Waage APIs, Rollenmodell | P0 | H1 |
| 003 | Trocknungs- und Abzugsregeln als versionierte Engine | 100% Abrechnungen regelbasiert reproduzierbar | M | Rule Engine, Audit | P0 | H1 |
| 004 | Settlement inkl. Gutschrift/Belastung mit Freigabe-Flow | <2% manuelle Korrekturbuchungen | L | Finance, Approval Workflow | P0 | H1 |
| 005 | Saisonale Kampagnenprozesse (Erntefenster) als Vorlagen | Setup-Zeit neue Kampagne <30 min | S | Workflow Templates | P1 | H1 |
| 006 | Kontrakt-Preislogik (Fix, Formel, Terminmarkt) einheitlich | 0 ungeklaerte Preisabweichungen >24h | L | Pricing Service, Marktdaten | P0 | H2 |
| 007 | Nebenkosten/Fracht/Lagergeld automatisch im Prozess | >=90% automatische Kostenzuordnung | M | Logistik, Finance | P1 | H1 |
| 008 | Landhandel-spezifische Reklamationsprozesse E2E | SLA-Erfuellung Reklamationen >=95% | M | CRM Service, DMS | P1 | H2 |
| 009 | Rollenbasierte Prozessvarianten je Genossenschaft | 0 globale Hardcoded Prozessschritte | M | Tenant Config | P0 | H1 |
| 010 | Betriebspruefungsfeste Prozessjournalisierung | 100% kritische Schritte mit Audit Hash | M | Audit Domain | P0 | H1 |

## Block 011-020: Workflow, Policy, Agent-Ready Platform

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 011 | Versionierte Workflow Engine mit Migrationen | 0 ungeplante Workflow-Brueche bei Releases | L | Workflow Service | P0 | H1 |
| 012 | Simulation/Sandbox fuer neue Workflows | 80% weniger Fehler nach Go-Live | M | Testdaten, Rule Engine | P1 | H1 |
| 013 | SLA/Timeout/Eskalationsknoten standardisiert | >=95% SLA-Einhaltung Kernprozesse | M | Notification, RBAC | P0 | H1 |
| 014 | Policy-as-Code mit Tenant Overrides | 100% Ausnahmen regelbasiert dokumentiert | M | Policy Store | P0 | H1 |
| 015 | Human-in-the-loop Freigaben fuer AI Aktionen | 100% AI-Aktionen mit Approval-Trail | M | Agent Layer, Audit | P0 | H1 |
| 016 | Idempotente Business-Commands statt UI-CRUD fuer Agenten | >=99.9% sichere Retries ohne Duplikate | L | API Refactor | P0 | H2 |
| 017 | MCP/OpenAPI Tool Contracts fuer externe Agenten | 20 produktive Agent-Tools freigeschaltet | M | API Governance | P1 | H2 |
| 018 | Ereignisbasierte Prozessbeobachtung (Process Mining Lite) | Durchlaufzeit-Drilldown fuer Top-10 Prozesse | L | Event Bus, Data Mart | P1 | H2 |
| 019 | Policy Explainability im UI (Warum freigegeben/blockiert) | 50% weniger Support-Rueckfragen | S | Frontend Components | P1 | H1 |
| 020 | Workflow-Template Marketplace intern | Neue Prozessvariante in <1 Tag | M | Template Registry | P2 | H3 |

## Block 021-030: UUIX, Designsystem, Bedienlogik

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 021 | Einheitliches Designsystem mit verbindlichen Prozesspatterns | 100% neue Seiten nutzen DS-Komponenten | M | Frontend Platform | P0 | H1 |
| 022 | Command Palette (Ctrl/Cmd+K) fuer Power User | 30% schnellere Task Completion | S | Frontend Shell | P1 | H1 |
| 023 | Keyboard-first fuer alle Kernmasken | >=90% Kernflows ohne Maus bedienbar | M | Accessibility Audit | P1 | H2 |
| 024 | Touch-optimierte Feldworkflows (Tablet/Lager/Waage) | Fehlbedienungen auf Touch -40% | M | Responsive Layouts | P1 | H1 |
| 025 | Kontextsensitive Quick Actions pro Maske | 25% weniger Klicks pro Vorgang | S | Action Registry | P1 | H1 |
| 026 | Inline-Validierung mit domain-spezifischen Erklaerungen | 35% weniger Eingabefehler | S | Validation Layer | P1 | H1 |
| 027 | Konsistente Informationsdichte je Rolle | Nutzerzufriedenheit >=8/10 | M | UX Research | P2 | H2 |
| 028 | Leitsystem fuer Ausnahmefaelle (Error UX) | 50% weniger Abbruchquote bei Fehlern | S | Error Boundaries | P1 | H1 |
| 029 | Agent UX Panel (Confidence, Quellen, Aktion) | AI-Adoption in Kernteams >=60% | M | Copilot UI | P1 | H2 |
| 030 | Multilingual + Fachsprache Landhandel konsistent | 0 kritische Begriffsinkonsistenzen | M | i18n Catalog | P2 | H2 |

## Block 031-040: Performance, Daten, Multi-User Parallelbetrieb

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 031 | Query-Vertraege haerten (nie undefined fuer Query Data) | 0 React Query undefined Laufzeitfehler | S | API Client, Schemas | P0 | H1 |
| 032 | 500er bei controlling/kpis/timeseries eliminieren | Error Rate <0.5% | S | DB Schema, Migrations | P0 | H1 |
| 033 | Read-Models fuer Dashboards statt teurer Live-Joins | p95 Dashboard API <250ms | M | Data Pipeline | P0 | H1 |
| 034 | API-Bulk-Operationen fuer Massenvorgaenge | 3x Throughput bei Batch-Import | M | API Layer | P1 | H2 |
| 035 | Optimistic Locking fuer konkurrierende Bearbeitung | 0 stille Ueberschreibungen | M | DB Models | P0 | H1 |
| 036 | Queue-basierte Hintergrundjobs fuer schwere Prozesse | p95 UI-Response <300ms unter Last | M | Job Runner | P1 | H1 |
| 037 | Lasttests Erntepeak (mehrere Standorte, parallel) | 500 gleichzeitige User stabil | L | Load Test Harness | P0 | H2 |
| 038 | Tenant-isolierte Caches/Rate Limits | 0 Cross-tenant Performance-Kollisionen | M | API Gateway | P1 | H2 |
| 039 | End-to-End Tracing (UI->API->DB->Worker) | MTTR -40% bei Produktionsfehlern | M | OpenTelemetry | P1 | H1 |
| 040 | Datenqualitaetsregeln (Dublette, Pflichtfeld, Referenz) | Stammdatenfehler -50% | M | MDM Rules | P1 | H2 |

## Block 041-050: Compliance, Integrationen, Markt-Differenzierung

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 041 | GoBD Belegkette komplett durchgaengig in allen Finanzpfaden | 100% revisionssichere Kette | L | Finance Service | P0 | H1 |
| 042 | Intrastat/Zoll produktiv inkl. Monitoring/Alerting | 0 versaeumte Meldefristen | M | Compliance Services | P0 | H1 |
| 043 | EDI/API Hub fuer Kunden/Lieferanten/Behorden | >=80% Dokumentaustausch digital | L | Integration Platform | P1 | H2 |
| 044 | Lieferketten-Tracking inkl. ETA/Abweichungsalarme | OTD +10 Prozentpunkte | M | Event Bus, GPS/Telematik | P1 | H2 |
| 045 | DMS + OCR + strukturierte Extraktion in Kernflows | 60% weniger manuelle Belegerfassung | M | DMS, AI OCR | P1 | H2 |
| 046 | Nachhaltigkeit/CO2 Reporting fuer Agrarkonzerne | ESG-Berichte in <1 Tag erzeugbar | M | Sustainability Domain | P2 | H3 |
| 047 | Branchenbenchmarking Cockpit je Genossenschaft | Monatlicher Benchmarkreport automatisch | M | Analytics Mart | P2 | H3 |
| 048 | Offene Integrationsfaehigkeit fuer Agenten (Perplexity etc.) | 10 externe Agent-Use-Cases live | M | Tooling, Security | P1 | H2 |
| 049 | Security-Hardening (OIDC, RBAC fein, Secrets, Audit) | 0 kritische Findings in Pentest | L | IAM, DevSecOps | P0 | H1 |
| 050 | Produktive Betriebsfuehrung mit SLO/SLI und Runbooks | Verfuegbarkeit >=99.9% | M | Observability, On-call | P0 | H1 |

## 90-Tage Ausfuehrungsreihenfolge (empfohlen)
1. Wave A (Wochen 1-4): 001, 002, 003, 009, 010, 011, 013, 014, 031, 032
2. Wave B (Wochen 5-8): 004, 015, 019, 021, 022, 024, 025, 033, 035, 039
3. Wave C (Wochen 9-12): 036, 041, 042, 049, 050 sowie Vorbereitung 016, 037, 043

## Governance
- Woechentliches Steering mit drei Pflicht-KPIs:
  - Delivery: % abgeschlossene P0/P1 Items pro Wave
  - Quality: Error Rate, Reopen Rate, SLA-Erfuellung
  - Adoption: aktive Nutzer in Kernprozessen, AI-Aktionsquote mit Approval

## Architekturleitplanken
- [Target State Landhandel ERP](../../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](../../adr/adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](../../adr/adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](../../adr/adr-005-workflow-policy-kern.md)

## Referenz auf Ist-Quellen im Repo
- [docs/architecture/current-processes.md](../../architecture/current-processes.md)
- [docs/analysis/valeoneuroerp_soll_ist.md](../../analysis/valeoneuroerp_soll_ist.md)
- [docs/roadmap/a-eins-gap-backlog.md](../a-eins-gap-backlog.md)
