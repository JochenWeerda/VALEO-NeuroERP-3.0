# Restgap Roadmap 2026-03-20

**Zweck:** Priorisierte Umsetzungsroadmap fuer die nach dem bereinigten Gap-Abgleich real verbleibenden Gaps.

## Ziel

Diese Roadmap uebersetzt die bereinigte Gap-Matrix in eine pragmatische Lieferreihenfolge.
Sie fokussiert nur auf Gaps, die aktuell entweder real offen sind oder nur teilweise belastbar abgeschlossen wurden.

## Statusabgleich

- Basis: [Bereinigte Gap-Matrix 2026-03-20](2026-03-20-gap-matrix-bereinigt.md)
- Strategische Quelle: [Top-50 Gap Backlog 2026-03-06](2026-03-06-top-50-gap-backlog-landhandel.md)
- Operative Liefernachweise: `docs/architecture/process-kernel/wave-*/STATUS.md`

## Priorisierungslogik

- `Phase 1`: direkte Produktkern-Luecken mit hoher betrieblicher Wirkung
- `Phase 2`: Bedien- und Adoptionsluecken fuer produktive Nutzung
- `Phase 3`: Skalierungs-, Belastungs- und Ausbaupfade nach Kernstabilisierung

## Phase 1

Ziel: kritische fachliche Kernketten und Nachvollziehbarkeit schliessen.

| Gap | Thema | Warum jetzt | Konkreter Lieferfokus |
|---|---|---|---|
| 002 | Vollstaendige Waage-/Annahme-Masken | P0-Kernprozess im Landhandel noch unvollstaendig | produktive Masken fuer alle Annahmearten, Rollenpfade, Validierung und Touch-Grundlogik |
| 001 | E2E Kontrakt -> Annahme -> Qualitaet -> Settlement | bereits teilweise geliefert, aber End-to-End noch nicht geschlossen | echte Durchstichkette ohne Nebenlisten, belastbarer Abschlussbeleg |
| 004 | Settlement inkl. Gutschrift/Belastung mit Freigabe-Flow | teilweise geliefert, finanzielle Relevanz hoch | Endabnahme ueber Gutschrift, Belastung, Korrektur und Audit |
| 019 | Policy Explainability im UI | Freigaben und Blockierungen muessen fachlich erklaerbar sein | einheitliche Explainability-Komponente in produktiven Prozessmasken |
| 016 | Idempotente Business-Commands mit vollstaendigem Monitoring/Audit | Kern bereits da, aber Betriebsnachweis unvollstaendig | zentrales Monitoring, Audit-Feed, KPI-Sicht fuer sichere Retries |

## Phase 2

Ziel: produktive Bedienbarkeit, Adoption und Governance-Luecken schliessen.

| Gap | Thema | Warum danach | Konkreter Lieferfokus |
|---|---|---|---|
| 023 | Keyboard-first fuer Kernmasken | Power-User-Produktivitaet erst nach stabilen Kernmasken sinnvoll | Fokus auf Waage, Annahme, Settlement, Reklamation |
| 024 | Touch-optimierte Feldworkflows | direkt relevant fuer Lager, Feld und Waage | Tablet-/Touch-Pfade fuer Annahme und Erfassung |
| 029 | Agent UX Panel | sinnvoll erst nach stabiler Explainability- und Policy-Sicht | Confidence, Quellen, Aktionen und Approval-Kontext in einer UI-Flaeche |
| 008 | Reklamationsprozesse E2E | Technik vorhanden, aber Abschlussbeleg fehlt | E2E-Abnahme CRM + DMS + SLA + Audit |
| 012 | Simulation/Sandbox fuer neue Workflows | Technik vorhanden, aber formal nicht sauber abgesichert | Abnahmepfade, Testdaten, belastbare Simulationsoberflaeche |
| 018 | Ereignisbasierte Prozessbeobachtung | Technik vorhanden, KPI-/Drilldown-Luecke offen | Top-10-Prozessdrilldown, Laufzeit- und Engpasssicht |
| 030 | Multilingual + Fachsprache Landhandel | sinnvoll nach UI-/Explainability-Haertung | Begriffskatalog, Uebersetzung, einheitliche Fachsprache in Kernmasken |

## Phase 3

Ziel: Plattform- und Betriebsreife nach Abschluss der Kern- und UUIX-Luecken.

| Gap | Thema | Warum spaeter | Konkreter Lieferfokus |
|---|---|---|---|
| 021 | Einheitliches Designsystem | hoher Hebel, aber sinnvoll auf stabilisierten Kernmustern | verbindliche Komponentenbibliothek und Pattern-Regeln |
| 020 | Workflow-Template Marketplace intern | Mehrwert steigt erst bei stabilen Workflow- und Simulationspfaden | Katalog, Clone, Governance, Installationspfad |
| 037 | Lasttests Erntepeak | sinnvoll nach funktionaler Schliessung der P0/P1-Kernpfade | Lastprofil, Multi-Standort, Queue-/DB-/API-Grenzwerte |

## Empfohlene Umsetzungsreihenfolge

1. `002`
2. `001`
3. `004`
4. `019`
5. `016`
6. `023`
7. `024`
8. `029`
9. `008`
10. `012`
11. `018`
12. `030`
13. `021`
14. `020`
15. `037`

## Hinweise

- `008`, `012`, `016`, `018`, `029` und `030` sind keine reinen Greenfield-Gaps mehr; dort ist der Schwerpunkt eher Haertung, Abnahme und Source-of-Truth-Bereinigung.
- `002`, `019`, `021`, `023`, `024` und `037` sind die klarsten echten Restluecken.
- Die naechste operative Wave-Planung sollte `Phase 1` in konkrete Arbeitspakete und Wave-Slices uebersetzen.
