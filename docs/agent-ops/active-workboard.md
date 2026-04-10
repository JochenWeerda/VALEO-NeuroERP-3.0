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
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme-Abrechnung als echten Settlement-Fall mit Ressourcen-, Preis- und Freigabekontext surfacen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
**Abnahmekriterien:** Abrechnung zeigt Fallkopf, knappen Kontext und Timeline ueber dem Settlement-Arbeitsplatz, ohne neue API-Last.
**Erledigt:** `annahme/abrechnung.tsx` zeigt jetzt Settlement-Fallkopf, Abrechnungskontext und Verlauf aus bereits vorhandenen Preview-/Campaign-/Settlement-Daten direkt ueber dem Self-Billing-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-014

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rechnungseingaenge-Liste als operativen Sammelarbeitsplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`
**Abnahmekriterien:** Die Liste zeigt klaren Freigabe-/Verbuchungsdruck und die naechste Bulk-Aktion, ohne den Listenraum zu ueberladen.
**Erledigt:** `rechnungseingaenge-liste.tsx` verdichtet jetzt Freigabe-/Verbuchungsstau, Summenlage und die naechste Bulk-Aktion ueber der bestehenden Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-015

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Mahnwesen als echten Follow-up-Fall mit Owner-, Risiko- und Governance-Sicht verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
**Abnahmekriterien:** Mahnwesen zeigt Mahndruck, Zins-/Connector-Lage und naechste FIBU-Aktion direkt vor dem Objektarbeitsplatz.
**Erledigt:** `finance/mahnwesen.tsx` fuehrt jetzt Mahndruck, Zins-/Connector-Kontext und naechste FIBU-Massnahme als kompakten Follow-up-Kopf ueber dem Objektarbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-016

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Offene-Posten-Raeume fuer Debitoren und Kreditoren auf eine gemeinsame operative Sicht ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/{op-debitoren,op-kreditoren}.tsx`
**Abnahmekriterien:** Beide OP-Raeume zeigen Rueckstand, Risiko und naechste Massnahme konsistent und schlank.
**Erledigt:** `op-debitoren.tsx` und `op-kreditoren.tsx` nutzen jetzt dasselbe leichte OP-Modell fuer Rueckstand, Mahn-/Ueberfaelligkeitsdruck, Kontext und Folgeaktion, ohne die Facharbeit in Tabellen und Dialogen zu verdoppeln.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-017

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufsnahe Dokumenten-/Lieferobjekte mit leichtem Vorgangsbild harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis,auftragsbestaetigung}.tsx`
**Abnahmekriterien:** Beide Objektmasken gewinnen Blocker-, Kontext- und naechste-Aktion-Sicht ohne Doppelung zur Fachmaske.
**Erledigt:** `anlieferavis.tsx` und `auftragsbestaetigung.tsx` haben jetzt einen kompakten Logistik-/Pruefkopf ueber der ObjectPage und bleiben darunter fachlich unveraendert tief.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-018

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und offene Restgrenzen fuer den naechsten Operativ-Rollout dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Es ist dokumentiert, welche Sammel- und Follow-up-Masken jetzt unter dem Zielbild laufen und welche bewusst weiterhin schlank bleiben.
**Erledigt:** Das schlanke Workboard und die Scope-Doku decken jetzt auch Sammel- und Follow-up-Masken fuer Settlement, Rechnungseingaenge, Mahnwesen, OP-Raeume sowie einkaufsnahe Lieferobjekte ab.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-019

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Einkaufslisten fuer Avis und Auftragsbestaetigungen als operative Sammelarbeitsplaetze verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis-liste,auftragsbestaetigungen-liste}.tsx`
**Abnahmekriterien:** Beide Listen zeigen Stau, Blocker und naechste Bulk-Aktion ueber der Liste, ohne den Tabellenraum zu ueberfrachten.

## OP-ROLL-020

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Zahlungslaeufe und UStVA/ELSTER als echte Finance-Follow-up-Raeume verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{fibu/zahlungslaeufe,finance/ustva,fibu/elster-online}.tsx`
**Abnahmekriterien:** Die Seiten zeigen FIBU-Druck, Fristen und naechste Massnahme ueber dem Arbeitsraum.

## OP-ROLL-021

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Schnittstellen- und Meldefolgearbeitsplatz mit demselben schlanken Fallmodell harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/schnittstellen-center.tsx`, ggf. angrenzende FIBU-Follow-up-Seiten.
**Abnahmekriterien:** Schnittstellen-Center zeigt operativen Druck, Risiken und naechste Aktion ohne KPI-Dopplung.

## OP-ROLL-022

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Annahme- und Queue-Sammelraum mit derselben Leitlogik weiterziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
**Abnahmekriterien:** Warteschlange zeigt operativen Stau, aktuelle Prioritaet und naechste Massnahme ueber der Liste.

## OP-ROLL-023

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Labor-/Qualitaets-Sammelarbeitsplaetze auf den leichten Operationsrahmen heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{labor/proben-liste,qualitaet/labor-liste}.tsx`
**Abnahmekriterien:** Laborlisten zeigen Probenstau, kritische Faelle und naechste Folgeaktion ueber der Liste.

## OP-ROLL-024

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Scope und Restgrenzen nach der dritten Rollout-Welle erneut komprimiert dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Der Rollout bleibt nachvollziehbar und weiterhin bewusst schlank.
