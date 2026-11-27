# Handshake: 2026-11-26 — M7-INSTALL-DEMO-A11Y-20261126

**Von:** Cursor Cloud  
**An:** Lead / Betrieb  
**Ziel:** M7-Vorarbeiten ohne M6 — Installationshandbuch-Gerüst, Demo-Mandant, Barrierefreiheitsbericht-Gerüst.

## Stand (Abschluss 2026-11-27)

- Branch: `cursor/m7-install-demo-a11y-8809` · **PR #226 MERGED**
- `docs/deployment/installationshandbuch.md`
- `scripts/demo_mandant.py` (`--anlegen` / `--loeschen` / `--status`), nur `valeo_probe`
- `tests/test_demo_mandant.py` — Unit (Mock) + Integration gegen Probe
- `docs/compliance/barrierefreiheitsbericht.md` (axe Kernrouten; Stichproben offen)
- Querverweise in `docs/roadmap/m7-m8-vorarbeiten.md`

## Abnahme (Post-Merge Audit 27.11.2026 Europe/Berlin auf `main`)

- `node scripts/docs-governance-check.cjs` → OK (116 Dateien)
- Demo anlegen+löschen gegen `valeo_probe`:
  - `python scripts/demo_mandant.py --anlegen` → Mandant neu, Konto 8000 neu
  - `python scripts/demo_mandant.py --loeschen` → Mandant gelöscht, Kontenzeilen=1

## Abgrenzung

- Claude `M7-M8-VORARBEITEN-20261125` (Löschkonzept/M5/Helm) unangetastet
- Keine echten Personen-/L3-Daten

## Nächster Schritt

1. ~~PR #226 mergen~~ **erledigt**
2. Weitere M7-Slices (Lizenz, Löschlauf, …) bleiben eigene Claims
