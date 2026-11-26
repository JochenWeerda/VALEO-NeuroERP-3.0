# Handshake: 2026-11-26 — M7-INSTALL-DEMO-A11Y-20261126

**Von:** Cursor Cloud  
**An:** Lead / Claude (Admin-Merge); Betrieb für Prüfstand-Lauf  
**Ziel:** M7-Vorarbeiten ohne M6 — Installationshandbuch-Gerüst, Demo-Mandant, Barrierefreiheitsbericht-Gerüst.

## Stand

- Branch: `cursor/m7-install-demo-a11y-8809` · PR #226 · Head (siehe Push)
- `docs/deployment/installationshandbuch.md`
- `scripts/demo_mandant.py` (`--anlegen` / `--loeschen` / `--status`), nur `valeo_probe` (oder `ALLOW_DEMO_MANDANT_ANY_DB=1`)
- `tests/test_demo_mandant.py` — Unit (Mock) + Integration gegen Probe
- `docs/compliance/barrierefreiheitsbericht.md` (axe Kernrouten; Stichproben offen)
- Querverweise in `docs/roadmap/m7-m8-vorarbeiten.md`

## Abnahme

- `node scripts/docs-governance-check.cjs` → grün (lokal belegt)
- Demo anlegen+löschen gegen `valeo_probe`: Integrationstest vorhanden; Lauf braucht DB (Cloud-Env ohne Postgres → Skip)

## Abgrenzung

- Claude `M7-M8-VORARBEITEN-20261125` (Löschkonzept/M5/Helm) unangetastet
- Keine echten Personen-/L3-Daten

## Nächster Schritt

1. CI am Head abwarten → Claude Admin-Merge („bereit zum Merge, Head \<sha\>“)
2. Integrationstest einmal gegen `valeo_probe` in CI/Prüfstand grün belegen
