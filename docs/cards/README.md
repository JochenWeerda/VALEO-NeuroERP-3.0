# Cards

## Zweck

Cards sind die kleinste fachlich prüfbare Einheit einer Workflow-Analyse.
Sie dienen **internen** Prozess- und Gap-Audits — nicht der veröffentlichten
Endnutzer-Doku (MkDocs schließt `docs/cards/` per `exclude_docs` aus).

## Konsolidierter Stand

- **Inventar:** [`docs/_internal/cards-inventory.md`](../_internal/cards-inventory.md)
  (maschinell via `scripts/cards-inventory-audit.py`)
- **Security-Hardening:** abgeschlossene SEC-Slices siehe
  [`docs/roadmap/status/2026-04-01-security-hardening-phase-1.md`](../roadmap/status/2026-04-01-security-hardening-phase-1.md)
- **Migration:** Cards werden nicht 1:1 in MkDocs übernommen; verifizierte
  Ergebnisse fließen in `docs/workflows/`, Benutzerhandbuch oder
  `docs/project-context/open-gaps-and-known-issues.md`.

## Granularitätsregel

- Eine Card pro Hauptaktion, Entscheidung, Schleife, Rücksprung oder Sonderfall.
- Wenn eine Card mehr als eine fachliche Hauptaktion enthält, zerlege sie weiter.
- Wenn Alternativpfade eigene UI-, Daten- oder Regellogik haben, erstelle eigene Cards.
- Wenn ein Schritt ohne eigene UI-, Daten- oder Entscheidungslogik auskommt, kann er mit Nachbar-Cards zusammengelegt werden.

## Pfadkonvention

Empfohlene Struktur:

- `docs/cards/verkauf/`
- `docs/cards/einkauf/`
- `docs/cards/lager/`
- `docs/cards/agrar/`
- `docs/cards/security/`
- `docs/cards/neuro-core/`

## Dateinamenschema

- `VK-010-ernte-annahme.md`
- `P2P-020-direktbestellung-standardmaske.md`
- `SEC-003-auth-tenant-hardening.md`

## Pflege (Docs-as-Code)

1. Neue Prozess-Cards mit YAML-Frontmatter anlegen (Vorlage: [`card-template.md`](card-template.md)).
2. Ketten-Zuordnung in [`docs/_internal/workflow-chains.md`](../_internal/workflow-chains.md) pflegen.
3. Card-Status nach Slice-Abschluss aktualisieren (`abgeschlossen` / `umgesetzt`).
4. Behobene Gaps durchstreichen oder in Tabelle mit **behoben** markieren.
5. Inventar regenerieren:

```bash
python scripts/cards-inventory-audit.py
```

6. Frontmatter-Nachzug für Registry-Cards (idempotent):

```bash
python scripts/migrate-cards-frontmatter.py
```

7. Verbleibende echte Lücken in `open-gaps-and-known-issues.md` spiegeln.

**Ketten-Registry:** [`workflow-chains.md`](../_internal/workflow-chains.md) · **Inventar:** [`cards-inventory.md`](../_internal/cards-inventory.md)

Vorlage: [`card-template.md`](card-template.md)
