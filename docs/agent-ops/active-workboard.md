# Active Workboard

Stand: `2026-04-10`

Dieses Board ist bewusst schlank gehalten, damit Session-Starts und Agent-Handoffs weniger Kontext verbrauchen.

Archiv des vorherigen Boards:
- [active-workboard-2026-04-10-pre-slim.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/archive/active-workboard-2026-04-10-pre-slim.md)

## Arbeitsregel

- Nur aktive oder frisch abgeschlossene Slices bleiben hier sichtbar.
- Historische Serien wandern ins Archiv.
- Claim-Pflicht bleibt unveraendert:
  1. Slice auf `reserviert`
  2. Workboard committen
  3. erst dann implementieren

## Kurzstand

- Das gemeinsame operative Arbeitsmodell ist bereits in den priorisierten Kernmasken ausgerollt.
- Der Rollout-Scope ist dokumentiert in:
  - [operational-rollout-scope-2026-04-09.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/operational-rollout-scope-2026-04-09.md)
- Der naechste Block betrifft Sammel- und Follow-up-Masken mit echtem operativem Mehrwert.

## OP-ROLL-013

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Annahme-Abrechnung als echten Settlement-Fall mit Ressourcen-, Preis- und Freigabekontext surfacen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
**Abnahmekriterien:** Abrechnung zeigt Fallkopf, knappen Kontext und Timeline ueber dem Settlement-Arbeitsplatz, ohne neue API-Last.

## OP-ROLL-014

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Rechnungseingaenge-Liste als operativen Sammelarbeitsplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`
**Abnahmekriterien:** Die Liste zeigt klaren Freigabe-/Verbuchungsdruck und die naechste Bulk-Aktion, ohne den Listenraum zu ueberladen.

## OP-ROLL-015

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Mahnwesen als echten Follow-up-Fall mit Owner-, Risiko- und Governance-Sicht verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
**Abnahmekriterien:** Mahnwesen zeigt Mahndruck, Zins-/Connector-Lage und naechste FIBU-Aktion direkt vor dem Objektarbeitsplatz.

## OP-ROLL-016

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Offene-Posten-Raeume fuer Debitoren und Kreditoren auf eine gemeinsame operative Sicht ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/{op-debitoren,op-kreditoren}.tsx`
**Abnahmekriterien:** Beide OP-Raeume zeigen Rueckstand, Risiko und naechste Massnahme konsistent und schlank.

## OP-ROLL-017

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Einkaufsnahe Dokumenten-/Lieferobjekte mit leichtem Vorgangsbild harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis,auftragsbestaetigung}.tsx`
**Abnahmekriterien:** Beide Objektmasken gewinnen Blocker-, Kontext- und naechste-Aktion-Sicht ohne Doppelung zur Fachmaske.

## OP-ROLL-018

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Scope und offene Restgrenzen fuer den naechsten Operativ-Rollout dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Es ist dokumentiert, welche Sammel- und Follow-up-Masken jetzt unter dem Zielbild laufen und welche bewusst weiterhin schlank bleiben.
