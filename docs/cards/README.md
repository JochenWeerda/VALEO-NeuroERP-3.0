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

1. Card-Status nach Slice-Abschluss aktualisieren (`abgeschlossen` / `umgesetzt`).
2. Behobene Gaps durchstreichen oder in Tabelle mit **behoben** markieren.
3. `python scripts/cards-inventory-audit.py` ausführen.
4. Verbleibende echte Lücken in `open-gaps-and-known-issues.md` spiegeln.

Vorlage: [`card-template.md`](card-template.md)
