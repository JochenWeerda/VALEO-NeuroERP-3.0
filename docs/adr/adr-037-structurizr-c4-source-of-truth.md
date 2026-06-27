# ADR-037 — Structurizr DSL als primäre C4-Quelle

**Status:** Accepted
**Datum:** 2026-06-27
**Bezieht sich auf:** ADR-036 (Architecture Documentation Stack)

## Kontext

ADR-036 führte C4-Diagramme als **Mermaid in Markdown** ein. Für ein **Architecture Operating System** (agentensteuerbare Architektur) reicht handgepflegtes Mermaid nicht aus:

- Kein diffbares Modell gegen Code (Container, Beziehungen)
- Duplikatpflege zwischen `docker-compose.yml`, Inventar und Diagrammen
- Agenten brauchen eine **Single Source** für System/Container/Beziehungen

Structurizr DSL ist „models as code“, versionierbar in Git und exportierbar in mehrere Sichten.

## Entscheidung

1. **Primäre C4-Quelle:** [`docs/architecture/c4/workspace.dsl`](../architecture/c4/workspace.dsl)
2. **Gerenderte Views:** `docs/architecture/views/c4-01-system-context.md` und `c4-02-containers.md` werden durch [`scripts/render_c4_views.py`](../../scripts/render_c4_views.py) **generiert** (Mermaid-Embeds) — nicht manuell editiert.
3. **Component-/Sequenz-/ERD-Diagramme** bleiben vorerst in Markdown (Mermaid), bis in DSL migriert.
4. **Structurizr CLI** ist optional für PNG/PlantUML-Export; CI nutzt primär den Python-Renderer + `--check`.
5. **Architecture Index** [`config/architecture-index.yaml`](../../config/architecture-index.yaml) verweist auf DSL und Domain-Packs.

## Konsequenzen

**Positiv:**

- Agenten und Drift-Checks können Container/Beziehungen aus DSL parsen
- Ein Modell, viele Views (Context, Container, später Deployment)
- Abgleich mit `generate_container_inventory.py` möglich

**Negativ:**

- ADR-036 Regel „Mermaid primär manuell“ ist für L1/L2 **aufgehoben**
- Renderer muss gepflegt werden bis Structurizr CLI in CI voll integriert ist

## Migration

- Einmalige Überführung aus bestehenden C4-Mermaid-Views in `workspace.dsl`
- `render_c4_views.py` ersetzt manuelle Mermaid-Blöcke in Context/Container-MD

## Referenzen

- [ADR-036](adr-036-architecture-documentation-stack.md)
- [architecture-protocol.md](../architecture/agents/architecture-protocol.md)
- [Structurizr DSL](https://docs.structurizr.com/dsl)
