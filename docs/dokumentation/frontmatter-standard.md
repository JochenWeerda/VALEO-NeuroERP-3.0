---
title: Frontmatter-Standard
type: reference
audience: [entwickler, product, qa, admin]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Frontmatter-Standard

Jede **kuratierte** Doku-Seite (Teil der MkDocs-Navigation) trägt einen
YAML-Frontmatter-Block am Dateianfang. Er macht Doku maschinenlesbar
(Agents, Drift-Report, Staleness) und steuert Review-Zyklen.

## Pflichtfelder

```yaml
---
title: Lieferschein in Rechnung umwandeln   # H1-naher Titel
type: how-to                                 # diataxis-typ (s.u.)
audience: [endnutzer]                         # Zielgruppen (s.u.)
owner: Team-Verkauf                           # verantwortlich fuer Pflege
status: aktiv                                 # entwurf | aktiv | veraltet
last_reviewed: 2026-06-25                      # ISO-Datum letzter Review
version: 3.0.0                                 # App-Version, fuer die es gilt
---
```

## Erlaubte Werte

| Feld | Werte |
|---|---|
| `type` | `tutorial`, `how-to`, `reference`, `explanation` |
| `audience` | `endnutzer`, `power-user`, `tenant-admin`, `betrieb`, `entwickler`, `qa`, `security`, `integrator`, `ki-agent`, `product` |
| `status` | `entwurf`, `aktiv`, `veraltet` |
| `last_reviewed` | ISO-Datum `YYYY-MM-DD` |
| `version` | SemVer der App, z. B. `3.0.0` |

## Regeln

- Frontmatter steht **vor** der H1; danach folgt genau eine H1 (`# ...`).
- `last_reviewed` wird bei jedem inhaltlichen Review aktualisiert; abgelaufene
  Reviews werden im Doku-Drift-Report markiert.
- `type` ist genau einer (Diátaxis) — Mischformen werden aufgeteilt.
- Optionale Felder: `tags`, `related`, `deprecated_by`, `tenant_scope`.
- Die Doku-Checks (`scripts/docs-markdown-check.cjs`,
  `scripts/docs-governance-check.cjs`) erlauben den Frontmatter-Block und
  verlangen die H1 unmittelbar danach.

## Beispiel (vollständig)

```markdown
---
title: Erste Ernteannahme Schritt für Schritt
type: tutorial
audience: [endnutzer, power-user]
owner: Team-Agrar
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
tags: [agrar, annahme, einstieg]
related: [benutzerhandbuch/annahme/index.md]
---

# Erste Ernteannahme Schritt für Schritt

...
```
