## Handoff: 2026-10-22 - Adaptive Workspace / erpclow

**Von:** Research-Agent erpclow/ERPNext (nur Doku)
**An:** Lead Adaptive Workspace / Launchpad
**Ziel des Slices:** Klären, was „erpclow“ meint; Übernahmen aus ERPNext/Frappe Desk und ERPClaw für VALEO Adaptive Workspace dokumentieren — ohne Produktcode.
**Stand:** abgeschlossen (Research). Kein Commit. Launchpad, ScreenDefinitions, MCP-YAML, Workboard unangetastet.

**Erledigt:**

- Repo-Suche: `erpclow` / `ERPNext` / `Frappe` = 0 Treffer (kein interner Codename).
- Öffentlich: `erpclow` ≈ Tippfehler für **ERPClaw** ([github.com/avansaber/erpclaw](https://github.com/avansaber/erpclaw)); Workspace-Quelle ist **Frappe Desk / ERPNext**.
- Lessons-Doc geschrieben.

**Offen:** Phase-1-Umsetzung liegt beim Lead (Palette, Counts, Boot-Vertrag). Dieser Slice fasst keine Launchpad-Dateien an.

**Betroffene Dateien:**

- `docs/architecture/adaptive-workspace-erpclow-lessons.md` (einzige inhaltliche Schreibdatei)
- dieser Handoff

**Tests / Checks:** keine (Research-only)

**Offene Risiken:**

- Chat-first (ERPClaw) oder Frappe-Port als „schnelle Workspace-Lösung“ würde Meridian/MCP-WRITE/Mandant brechen.
- Launchpad-Overlay bleibt lokal; mandantenserver-seitiges Overlay ist Folgeclaim.

**Annahmen:** Adaptive Workspace ist Einstieg + Kommandoebene, nicht zweites Maskensystem. ProcessBand bleibt am Beleg.

**Naechster konkreter Schritt:** Lead liest Abschnitt 5 der Lessons-Doc und schneidet P1 (Palette auf SD/Capability-Aktionen) ohne Auto-Submit und ohne R3/R4 aus der Bar.
