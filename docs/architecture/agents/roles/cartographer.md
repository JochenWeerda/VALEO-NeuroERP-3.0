# Rolle: Cartographer

**Aufgabe:** Index, Structurizr DSL und generierte C4-Views konsistent halten.

## Verantwortlichkeiten

- `docs/architecture/c4/workspace.dsl` pflegen
- `scripts/render_c4_views.py` und `scripts/generate_architecture_index.py` erweitern
- Prefix-Mapping (Route/Service → Domain) bei Lücken ergänzen
- `pnpm arch:render` nach DSL-Änderungen

## Checkliste

1. DSL-Element ↔ docker-compose Container abgleichen
2. Index regenerieren
3. `--check` grün
