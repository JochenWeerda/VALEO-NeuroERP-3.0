---
title: Doku-Governance
type: explanation
audience: [entwickler, product, qa, admin]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Doku-Governance

Wie die Dokumentation dauerhaft aktuell, verantwortet und auditierbar bleibt.

## Verantwortlichkeiten (CODEOWNERS)

Review-Zuständigkeiten sind in `.github/CODEOWNERS` je Bereich hinterlegt
(Benutzerhandbuch → Product, Admin → Ops, Schnittstellen/Entwickler → Backend,
Agent-Doku → AI-Platform, Compliance → Compliance). Änderungen an einem Bereich
erfordern Review der jeweils Verantwortlichen.

## CI-Gates

| Gate | Wirkung |
|---|---|
| `mkdocs build` | Baut die kuratierte Site; Fehler blockieren. |
| `docs-markdown-check.cjs` | Markdown-Hygiene (H1, Whitespace, Fences). |
| `docs-governance-check.cjs` | Struktur-/Frontmatter-Regeln. |
| `docs-staleness-check.cjs` | Meldet veraltete Seiten (zunächst nicht-blockierend). |
| `ai-slice-readiness-check.cjs` | Pflichtschema der Slice-YAMLs. |

## Aktualität (Staleness)

Jede kuratierte Seite trägt `last_reviewed`. Der Staleness-Check meldet Seiten
über dem Schwellwert:

```bash
node scripts/docs-staleness-check.cjs --max-age-days 365
```

Im CI läuft er zunächst **nicht-blockierend** (`continue-on-error`), um
Altbestände nicht sofort rot zu färben. Nach der Migration kann er verschärft
werden.

## Review-Frequenz

| Bereich | Frequenz |
|---|---|
| Benutzerhandbuch | je Release |
| Architektur / ADR | bei Änderung |
| Schnittstellen (generiert) | bei API-/Tool-Änderung |
| Compliance | quartalsweise |

## Versionierung & Release-Snapshots

- **Doku-Version = App-Version** (kein eigener Doku-Strang).
- Je Release-Tag erzeugt `docs-release.yml` mit **mike** einen
  unveränderlichen, datierten Doku-Snapshot (revisionssicher, auditrelevant).
- **Live-Site:** <https://jochenweerda.github.io/VALEO-NeuroERP-3.0/>
  (GitHub Pages, Branch `gh-pages`, via `mike` versioniert).
- Nutzerlesbare Änderungen stehen im [CHANGELOG](https://keepachangelog.com/de/1.1.0/)
  (`CHANGELOG.md`).

## Leitprinzip

Doku reist im selben PR wie der Code. Doku-Update ist Teil der Definition of
Done. Drift wird gemessen, nicht gehofft.
