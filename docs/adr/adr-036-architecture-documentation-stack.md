# ADR-036 — Architektur-Dokumentations-Stack

**Status:** Accepted
**Datum:** 2026-06-27
**Entscheider:** Architektur / Dokumentation

## Kontext

VALEO NeuroERP 3.0 ist ein großes Multi-Domain-ERP (Agrar, CRM, FiBu, Lager, DMS, POS/TSE, Compliance) mit hybridem Deployment (FastAPI-Monolith, selektive Microservices, BFF, 20+ Docker-Container). Die bestehende Dokumentation ist **operativ stark** (Process Kernel, ADRs, Workflows), aber **formal-architektonisch lückenhaft**: kein System-Context-, kein Container-Gesamtbild, kein arc42-Rahmen, kein ERD.

Für Onboarding, Integrationsplanung und Enterprise-Architektur-Audits reicht UML allein nicht aus.

## Entscheidung

VALEO führt einen **mehrschichtigen Architektur-Dokumentations-Stack** ein:

| Ebene | Notation / Format | Ort |
|---|---|---|
| Ordnungsrahmen | ISO/IEC/IEEE 42010 (Stakeholder, Concerns, Viewpoints) | `docs/architecture/views/stakeholder-concerns.md` |
| Enterprise-Landkarte | ArchiMate-äquivalent (vereinfachtes Schichtendiagramm, Mermaid) | `docs/architecture/views/enterprise-landscape.md` |
| Software-Gesamtbild | C4 Model (Context, Container, Component) — **Mermaid C4** | `docs/architecture/views/c4-*.md`, `components/` |
| Technische Abläufe | UML Sequenzdiagramme (Mermaid) | `docs/architecture/views/sequences/` |
| Geschäftsprozesse | Mermaid-Flowcharts (bestehend, BPMN-äquivalent) | `docs/architecture/process-map.md`, `docs/workflows/` |
| Datenmodell | ERD (Mermaid) aus Canonical Domain Model | `docs/architecture/views/erd-canonical-domain.md` |
| Entscheidungen & Risiken | arc42 (Hub-Seiten) + ADRs | `docs/architecture/arc42/`, `docs/adr/` |
| Lieferstand | Process Kernel (eigene Viewpoint-Sicht) | `docs/architecture/process-kernel/STATUS.md` |

**Tooling-Regeln:**

1. Diagramme primär als **Mermaid in Markdown** (MkDocs-kompatibel, Docs-as-Code).
2. **Kein** paralleles PlantUML/Draw.io/Archi-Ökosystem ohne expliziten Bedarf.
3. Container-Inventar wird aus `docker-compose.yml` **generiert** (`scripts/generate_container_inventory.py`).
4. arc42-Kapitel sind **dünne Hub-Seiten** — verlinken auf bestehende Quellen, duplizieren keinen Inhalt.
5. Process Kernel bleibt **eigenständige Delivery-View**, wird nicht durch C4 ersetzt.

## Begründung

- **C4** liefert verständliche Zoom-Stufen für Entwickler, Betrieb und Integratoren.
- **ArchiMate-äquivalente Landkarte** ordnet Fachdomänen, Anwendungen und Technologie ohne Voll-ArchiMate-Tooling.
- **ISO 42010** strukturiert Sichten nach Stakeholder-Bedürfnissen statt „ein riesiges Diagramm“.
- **UML** nur für kritische Sequenzen und Canonical Core — nicht monolithisch.
- Bestehende Stärken (ADRs, Workflows, Process Kernel) bleiben erhalten.

## Konsequenzen

**Positiv:**

- Schnelleres Onboarding und klarere Integrationslandschaft
- Abgleichbarkeit Code ↔ Dokumentation via Generator-Drift-Checks
- Audit-fähige Architekturbeschreibung ohne Tool-Lock-in

**Negativ:**

- Pflegeaufwand bei Container-/Integrationsänderungen
- Mehr Navigationsstruktur — erfordert Disziplin bei PRs

## Referenzen

- [Architektur-Index](../architecture/index.md)
- [Viewpoint-Katalog](../architecture/views/viewpoint-catalog.md)
- [Dokumentationskonzept](../dokumentation/dokumentationskonzept.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-035 Kein Workflow-Designer](adr-035-kein-workflow-designer.md) — Mermaid statt BPMN-Designer
