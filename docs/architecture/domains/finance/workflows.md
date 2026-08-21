---
title: Finance — Workflows
type: explanation
audience: [entwickler, fachlich]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance — Workflows

Rechnungstapel: kanonische Belegreferenzen sammeln -> Datenqualitaet pruefen ->
durch abweichenden Benutzer freigeben -> idempotent ausfuehren -> Fehlerzeilen
mit Quellbeleg und Nachweis klaeren -> begruendet wiederholen.

- [fin-001 Finance to Reporting](../../../workflows/fin-001-finance-to-reporting.md)
- O2C → FiBu: [seq-o2c-fibu.md](../../views/sequences/seq-o2c-fibu.md)
- Abschluss / Closing: Process Kernel FiBu-Slices
- UStVA / ELSTER: Frontend `meldewesen`, Open Gaps FIBU-006
- POS/TSE: [pos-fiscalization-providers.md](../../pos-fiscalization-providers.md)
