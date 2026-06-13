# VALEO NeuroERP - Projektdokumentation

## Zweck

Diese Dokumentation ist die zentrale Kontextquelle fuer Prozessanalyse, Workflow-Validierung, UI-/CRUD-Pruefung, Browser-Use-Tests und Umsetzung im Repo.

Sie richtet sich an:

- Entwickler
- QA
- Prozessanalysten
- LLMs und Coding-Agents

## Vor jeder Aufgabe lesen

1. [Projekt-Gesamtstand 2026-05-27](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/PROJEKT-GESAMTSTAND-2026-05-27.md) — aggregierte Sicht über alle Waves und Compliance
2. [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
3. [System Overview](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/system-overview.md)
4. [Domain Landhandel und Agrarhandel](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/domain-landhandel-und-agrarhandel.md)
5. passende Datei unter `docs/workflows/`
6. [Open Gaps and Known Issues](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/open-gaps-and-known-issues.md)
7. [Browser-Use Checklists](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/browser-use-checklists.md)

## Arbeitsregeln

- Prozesse immer dokumentationsbasiert analysieren.
- Workflows immer bis auf kleinste pruefbare Einheiten zerlegen.
- Standardmasken bevorzugt erweitern, wenn das fachlich und UX-seitig sauber bleibt.
- Spezialmasken nur bei echtem Bedarf erstellen.
- Gefundene Fehler sofort beheben, wenn sie den aktuellen oder angrenzenden Prozess beeintraechtigen.
- Nach jeder relevanten Aenderung Doku, Tests und Soll-Ist-Bewertung aktualisieren.

## Relevante Doku-Bereiche

- **Auth & Mandant (API/erp-domain):** [AUTH-AND-TENANT-CONCEPT.md](AUTH-AND-TENANT-CONCEPT.md), ADR unter `docs/architecture/`, sowie [ERP: Finanz & Mandant – Multitenancy](erp-finanz-multitenancy.md) (`finanz`-Schema, Migrationen, SQL-Runner). Schnellwege von der Repo-Wurzel: **`pnpm migrate:erp-finanz`**, **`pnpm test:erp-domain`**.
- `docs/project-context/`: fachlicher und technischer Rahmen
- `docs/workflows/`: Arbeitsweise fuer Workflow-Zerlegung, Prompting und Struktur (Kernel-Actions/DB: [kernel-action-execution-mutations.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/kernel-action-execution-mutations.md)); Agrar-Materialfluss ↔ Lieferkette: [wm-agri-silo-supply-chain-integration-2026-06-13.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/wm-agri-silo-supply-chain-integration-2026-06-13.md)
- `docs/cards/`: Card-Templates und Ablagelogik
- `docs/quality-assurance/`: Browser-Use-, CRUD- und Soll-Ist-Pruefung
- `docs/warehouse/`: Agrar-Lager / WMS-Vertiefung — Einstieg [warehouse/README.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/warehouse/README.md) (Materialfluss, Hofplan, externes Handbuch-Inventar)
- `docs/agent-ops/`: restart-sichere Parallelarbeit fuer mehrere Agenten
- `docs/adr/`: verbindliche Architektur- und Entscheidungsregeln
- [Frontend Routing](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/frontend-routing/README.md): TanStack-Route-Tree, typisierte Deep Links und Legacy-Redirects
- [Production Readiness Runbook](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/operations/production-readiness-runbook.md): harte Release-Gates, Auditor-Simulation, Deployment und externe Freigaben
- [Dependency and Compatibility Maintenance](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/operations/dependency-and-compatibility-maintenance.md): Vertragsversionierung, Schema-Kompatibilitaet, Security-Patches, Major-Upgrades und Release-Kompatibilitaetsmatrix (`artifacts/release-compatibility-matrix.json`)

## Parallele Agentenarbeit

Wenn zwei oder mehr Agenten parallel arbeiten, ist zusaetzlich verpflichtend:

1. [AGENTS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/AGENTS.md)
2. [Agent Ops README](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/README.md)
3. [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)

zu verwenden.

## Source of Truth

Diese Datei ist eine `abgeleitete Sicht`.

Verbindlicher Liefer- und Reifegrad liegt in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/architecture/process-kernel/wave-*/STATUS.md`
- `docs/roadmap/status/*.md`
- strategische Leitpläne (ergänzend): [Strategic Next Steps (2026-03-31)](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/roadmap/2026-03-31-strategic-next-steps.md)

## Qualitaetsziel

Alle End-to-End-Workflows muessen:

- fachlich vollstaendig
- technisch durchgaengig
- UI-seitig nutzbar
- CRUD-faehig
- Browser-Use-pruefbar
- im Tagesgeschaeft eines Landhandels oder einer Agrargenossenschaft belastbar

sein.
