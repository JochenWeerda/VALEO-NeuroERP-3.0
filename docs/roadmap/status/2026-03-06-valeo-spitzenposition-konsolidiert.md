# VALEO NeuroERP – Spitzenposition Landhandel: Konsolidierte Strategie

**Stand:** 2026-03-06  
**Fokus:** Landhandel, Genossenschaften, Agrarkonzerne

---

## Kurzfazit

Das System ist für einen Landhandel-/Genossenschafts-ERP-Ansatz bereits ungewöhnlich breit, aber noch nicht auf Spitzenniveau. Drei zentrale Hebel entscheiden über den Aufstieg:

1. **Prozessdurchgängige Produktivität** – Keine Medienbrüche, keine Mock-Daten in kritischen Cockpits
2. **Agentenfähige Architektur** – MCP/Tool-Contracts, idempotente Commands, Human-in-the-Loop
3. **Skalierbare UX/Performance unter Last** – Read-Models, SLOs, Multi-User-Parallelbetrieb

---

## Ist-Bild (lokal geprüft)

| Aspekt | Befund |
|--------|--------|
| **Funktionsfläche** | Ca. 402 Frontend-Seiten, ~135 API-Router-Includes ([routes.tsx](packages/frontend-web/src/app/routes.tsx), [api.py](app/api/v1/api.py)) |
| **Landhandel-Domain** | Strukturell angelegt (Agribusiness, Kontrakte, Qualität, Traceability etc.) in [domains/agrar](app/domains/agrar) |
| **Dokumentierter Soll-Ist** | Zentrale Lücken: Mock-Daten, monolithische Kopplung, begrenzte E2E-Workflow-Automation, UX-Defizite ([valeoneuroerp_soll_ist.md](docs/analysis/valeoneuroerp_soll_ist.md), [current-processes.md](docs/architecture/current-processes.md)) |
| **Fehlerbilder** | analytics/kpis undefined, wiederholte 500 bei controlling – Symptome: fehlende robuste Read-Models, inkonsistente Query-Contracts, lückenhafte Fallbacks |

---

## Wettbewerbsvergleich: Kurzüberblick

| Anbieter | Stärken | Schwächen | VALEO-Position |
|----------|---------|-----------|----------------|
| **ServiceERP / a.amic** | Branchennahe operative Prozesse, Praxisnähe, Stammdaten/Abwicklung | Schwächer bei AI-/Agent-Interoperabilität | Operativ hinterher, architektonisch voraus |
| **Odoo** | Schnelle Masken-/Workflow-Erstellung (Studio, Automated Actions), Time-to-Market | Komplexe Agrar-Prozesslogik oft nur via Add-ons/Custom | Mask-Builder ähnlich, aber weniger Ökosystem |
| **SAP / Oracle** | End-to-End, Governance, Skalierung, Rollen-/Prozessmodell, AI-Agent-Strategie (Joule, Agent Studio) | Implementierungskomplexität, Kosten | Enterprise-Reife hinterher, AI-First-Vision vergleichbar |

**Inference:** Architektonisch näher an einem eigenen „vertical AI ERP“ als klassische Landhandel-Systeme, operativ noch nicht so reibungslos wie etablierte Suiten.

---

## Was fehlt zur Spitze (Handlungsfelder)

### 1. Process Coverage 100 % in produktiven Masken

- Alle Kernabläufe ohne Medienbruch: **Kontrakt → Annahme/Waage → Qualität/Trocknung → Settlement → FiBu → Reporting → Compliance**
- Keine Mock-/Dualpfade mehr in kritischen Cockpits
- Vollständige Waage/Annahme-Masken für alle Warenflüsse

### 2. Workflow Engine als Produktkern

- Versionierte, mandantenfähige Workflows mit Freigaben, Simulation, Rollback
- SLA-Überwachung und Prozess-Mining (Lite)
- Ereignisgetriebene End-to-End-Transparenz statt isolierter CRUD-Masken

### 3. AI-first + Agent-ready UUIX

- Einheitlicher **Actions-Layer** (stabile, idempotente Business-Commands), nicht nur Page-APIs
- MCP-/Tooling-Schicht, OpenAPI-konforme „Agent Contracts“, semantische Event- und Dokumentkontexte
- **Human+Agent Co-Work:** Agent schlägt vor, Mensch bestätigt, Audit-Trail dokumentiert

### 4. Geschwindigkeit Maskenaufbau

- Metadaten-/Schema-getriebene Maskengenerierung (Form, Validierung, RBAC, Feldregeln, Layout)
- Ziel: neue prozessfähige Maske in **Stunden**, nicht Tagen

### 5. Performance & Multi-User Parallelbetrieb

- Harte SLOs: p95 API, p95 first-contentful-interaction, Durchsatz pro Prozesskette
- Read-Model/Caching-Strategie, Async-Jobs, Bulk-Operations
- Conflict-Handling (optimistic locking), Lasttests für Saisonspitzen (Erntefenster)
- Technische Schulden aus 500ern/Query-Fehlern zuerst eliminieren

### 6. UUIX/Design-Reife

- Ein Designsystem mit verbindlichen Prozesspatterns (Listen, Objektseiten, Wizard, Ausnahmen, Freigaben)
- Konsistente Informationsdichte, Keyboard-/Touch-Pfade
- **Agenten-UI-Flächen:** Erklärbarkeit, Confidence, „Warum?“-Panel

---

## Priorisierung: Nächste 90 Tage

| Welle | Wochen | Schwerpunkte |
|-------|--------|--------------|
| **Wave A** | 1–4 | E2E-Kernprozess, Waage/Annahme, Trocknungsregeln, mandantenfähige Prozessvarianten, Audit; Workflow Versionierung, SLA; Query-Verträge, 500er-Fixes |
| **Wave B** | 5–8 | Settlement mit Freigabe; Human-in-the-Loop für AI; Policy Explainability; Designsystem; Command Palette; Touch-Optimierung; Quick Actions; Read-Models; Optimistic Locking; Tracing |
| **Wave C** | 9–12 | Queue-basierte Jobs; GoBD-Belegkette; Intrastat; Security-Hardening; SLO/Runbooks; Vorbereitung idempotente Commands, Lasttests, EDI-Hub |

### Konkrete Maßnahmen (Top 5)

1. **Stabilisierungsschicht:** Alle 500/Query-Contract-Fehler und API-Read-Models fixen, SLO-Monitoring aktiv
2. **Top-10 Landhandel-Prozesse** vollständig „click-to-cash“ ohne Mock schließen
3. **Workflow-Plattform** produktiv machen (Versionierung, SLA, Audit, Freigaben)
4. **Agent-Layer** (MCP/OpenAPI Actions + Policy Guards + Audit) auf 3 Kernprozessen pilotieren
5. **Schema-driven Mask Builder** verbindlich für neue Seiten machen

---

## Verknüpfungen

| Dokument | Inhalt |
|----------|--------|
| [Top-50 Gap Backlog Landhandel](2026-03-06-top-50-gap-backlog-landhandel.md) | IDs 001–050, Aufwand, Abhängigkeiten, KPI-Zielwerte, Wave-Zuordnung |
| [Arbeitsaufteilung Codex vs. Hauptstrang](2026-03-06-arbeitsaufteilung-codex-hauptstrang.md) | 30 % Codex (Parallel Chat), 70 % Hauptstrang, Status-Tracking für gegenseitige Kontrolle |

---

## Web-Quellen (Referenz)

| Thema | URL |
|-------|-----|
| SAP Business AI / Joule / Agents | https://www.sap.com/products/artificial-intelligence.html |
| SAP Fiori Design System | https://experience.sap.com/fiori-design-web/ |
| Oracle AI Agent Studio (Fusion Apps) | https://docs.oracle.com/en/cloud/saas/readiness/sales/25b/sales25b/25B-sales-wn-f36912.htm |
| Oracle Redwood UX | https://www.oracle.com/redwood/ |
| Odoo Studio | https://www.odoo.com/app/studio |
| Odoo Automated Actions | https://www.odoo.com/documentation/19.0/applications/studio/automated_actions.html |
| Odoo Deployment/Workers | https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html |
| Perplexity API Docs | https://docs.perplexity.ai/ |
| Model Context Protocol (MCP) | https://github.com/modelcontextprotocol |

---

## Repo-Referenzen

| Dokument | Pfad |
|----------|------|
| Soll-Ist-Analyse | [docs/analysis/valeoneuroerp_soll_ist.md](../../analysis/valeoneuroerp_soll_ist.md) |
| Aktuelle Prozesse | [docs/architecture/current-processes.md](../../architecture/current-processes.md) |
| Top-50 Gap Backlog | [2026-03-06-top-50-gap-backlog-landhandel.md](2026-03-06-top-50-gap-backlog-landhandel.md) |
| A.eins Gap Backlog | [docs/roadmap/a-eins-gap-backlog.md](../a-eins-gap-backlog.md) |
| GAP-Konsolidierung | [gap/consolidated-overview.md](../../../gap/consolidated-overview.md) |
| AI-Vision | [docs/AI-VISION.md](../../AI-VISION.md) |
| UX-Standard | [docs/UX-STANDARD-VALEO.md](../../UX-STANDARD-VALEO.md) |
| Masken-Standard | [docs/MASKEN.md](../../MASKEN.md) |
