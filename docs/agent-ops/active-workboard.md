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
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufslisten fuer Avis und Auftragsbestaetigungen als operative Sammelarbeitsplaetze verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis-liste,auftragsbestaetigungen-liste}.tsx`
**Abnahmekriterien:** Beide Listen zeigen Stau, Blocker und naechste Bulk-Aktion ueber der Liste, ohne den Tabellenraum zu ueberfrachten.
**Erledigt:** `anlieferavis-liste.tsx` und `auftragsbestaetigungen-liste.tsx` fuehren jetzt denselben leichten Sammelvorgangskopf fuer Liefer- und Freigabestau ueber der bestehenden ListReport-Facharbeit.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-020

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungslaeufe und UStVA/ELSTER als echte Finance-Follow-up-Raeume verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{fibu/zahlungslaeufe,finance/ustva,fibu/elster-online}.tsx`
**Abnahmekriterien:** Die Seiten zeigen FIBU-Druck, Fristen und naechste Massnahme ueber dem Arbeitsraum.
**Erledigt:** `zahlungslaeufe.tsx`, `finance/ustva.tsx` und `fibu/elster-online.tsx` zeigen jetzt Fristen, Freigabedruck und Einreichungs-/Exportpfad als leichten Finance-Follow-up-Rahmen ueber Wizard bzw. Fachformular.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-021

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Schnittstellen- und Meldefolgearbeitsplatz mit demselben schlanken Fallmodell harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/schnittstellen-center.tsx`, ggf. angrenzende FIBU-Follow-up-Seiten.
**Abnahmekriterien:** Schnittstellen-Center zeigt operativen Druck, Risiken und naechste Aktion ohne KPI-Dopplung.
**Erledigt:** `fibu/schnittstellen-center.tsx` fuehrt Connector-, Revisions- und Periodenlage jetzt als technischen FIBU-Fallkopf mit kurzer Timeline und Masterdatenkontext.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-022

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme- und Queue-Sammelraum mit derselben Leitlogik weiterziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
**Abnahmekriterien:** Warteschlange zeigt operativen Stau, aktuelle Prioritaet und naechste Massnahme ueber der Liste.
**Erledigt:** `annahme/warteschlange.tsx` verdichtet Queue-Druck, Objektkettenlage und Bottleneck-Hinweis jetzt als operativen Annahmekopf ueber der bestehenden Operator-Oberflaeche.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-023

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-/Qualitaets-Sammelarbeitsplaetze auf den leichten Operationsrahmen heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{labor/proben-liste,qualitaet/labor-liste}.tsx`
**Abnahmekriterien:** Laborlisten zeigen Probenstau, kritische Faelle und naechste Folgeaktion ueber der Liste.
**Erledigt:** `labor/proben-liste.tsx` und `qualitaet/labor-liste.tsx` zeigen jetzt offenen Analyse- und Probenstau, Labor-/Chargekontext und die naechste Folgeaktion ueber den Tabellen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-024

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und Restgrenzen nach der dritten Rollout-Welle erneut komprimiert dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Der Rollout bleibt nachvollziehbar und weiterhin bewusst schlank.
**Erledigt:** Scope und Open-Gaps dokumentieren jetzt die dritte Welle fuer Einkaufslisten, FIBU-Follow-up, Schnittstellen, Queue und Laborraeume weiterhin als leichten Rollout ohne Zusatz-Requests.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-025

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditorenraum als FIBU-Profiarbeitsplatz mit echter Folgeaktion statt Info-Toast vertiefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/kreditoren.tsx`
**Abnahmekriterien:** `fibu/kreditoren.tsx` fuehrt DATEV-/Exportpfade als belastbare Folgeaktion ohne lokale Quittungs-Toastlogik.
**Erledigt:** `fibu/kreditoren.tsx` ist jetzt als echter Follow-up-Arbeitsraum mit Fallkopf, Kontext und Timeline verdichtet; DATEV-Export fuehrt direkt in den Buchungsuebergabe-Raum statt lokaler Info-Toast.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-026

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lieferanten-Dokumentraum mit realem Downloadverhalten statt TXT-Fallback professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`
**Abnahmekriterien:** Dokumentdownload in `lieferanten-stamm.tsx` nutzt nur echte Artefaktpfade und zeigt klare Fehlerfuehrung ohne pseudo-download.
**Erledigt:** `lieferanten-stamm.tsx` nutzt jetzt nur noch den echten Downloadpfad; pseudo-TXT-Fallback ist entfernt und Fehlersituationen zeigen klaren DMS-/Artefakt-Hinweis.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-027

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fuhrpark-Funktionsaktionen robust und revisionssicher machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fuhrpark/fahrzeug-stamm.tsx`
**Abnahmekriterien:** Drucker-/Druck-/Unfall-/Loesch-Aktionen behandeln Fehler sauber und quittieren nicht mehr blind.
**Erledigt:** `fuhrpark/fahrzeug-stamm.tsx` fuehrt Setup-, Druck-, Unfall- und Loesch-Aktionen jetzt mit try/catch, klaren Fehlertoasts und Loeschbestaetigung aus.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-028

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Charge-Verfolgung von fragiler Static-Toast-Konfiguration auf belastbaren Runtime-Aktionspfad ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/futtermittel/charge-verfolgung.tsx`
**Abnahmekriterien:** Bulk-Aktionen in der Charge-Verfolgung sind eindeutig runtime-gebunden und enthalten keine toten Static-Action-Reste.
**Erledigt:** `futtermittel/charge-verfolgung.tsx` fuehrt keine static Toast-BulkActions mehr; alle Massenaktionen laufen nur noch ueber den runtime-verdrahteten Aktionspfad.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-029

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/FIBU-Monatswerte als Fiori-artigen Operatorraum mit klaren Folgeaktionen und Kontrolldichte veredeln.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/monatswerte.tsx`
**Abnahmekriterien:** Monatswerte liefern klaren Fallkopf, Risiken und naechste Aktion ohne Zusatz-Requests, konsistent zum Operational-Modell.
**Erledigt:** `fibu/monatswerte.tsx` hat jetzt denselben leichten Fallrahmen fuer L3/FIBU-Auswertung (Status, Risiken, naechste Aktion) ohne neue Datenabfragen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-030

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/Cutover-nahe Buchungsuebergabe als FIBU-Leitstand mit Governance- und Revisionskontext vervollstaendigen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/schnittstelle-fibu.tsx`
**Abnahmekriterien:** Schnittstelle-FIBU zeigt operativen Druck, Revisions-/Cutover-Kontext und belastbare Folgewege ohne Platzhalteraktionen.
**Erledigt:** `fibu/schnittstelle-fibu.tsx` zeigt jetzt Fallkopf, Timeline und Revisions-/Cutover-Kontext fuer den Buchungsuebergabeprozess, inklusive klarer Folgefuehrung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-031

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsjournal als FIBU-Operatorraum mit Revisionsdruck, Periode und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchungsjournal.tsx`
**Abnahmekriterien:** `fibu/buchungsjournal.tsx` zeigt Fallkopf, Kontext und Timeline aus bereits geladenen Journaldaten und fuehrt DATEV-/Stornofolge ohne Blindflug.
**Erledigt:** `fibu/buchungsjournal.tsx` fuehrt Journalbuchungen jetzt als Revisionsfall mit Fallkopf, Referenzkontext, Timeline und direktem Exportpfad in die Buchungsuebergabe.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-032

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Abschluss-Checkliste als echter Close-Fall mit Pflichtdruck, Owner und Flow-Spine-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/abschluss-checklist-detail.tsx`
**Abnahmekriterien:** `abschluss-checklist-detail.tsx` verdichtet Pflichtquote, Blocker und naechste Abschlussaktion oberhalb der Checkliste.
**Erledigt:** `abschluss-checklist-detail.tsx` zeigt jetzt den Close-Fall mit Pflichtdruck, Flow-Spine-Bezug, Blockern und kompakter Vorgangssicht ueber der Checkliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-033

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditoren-Zahlungslauf als Fiori-artigen Zahlungsoperatorraum mit Governance- und Freigabedruck heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
**Abnahmekriterien:** `zahlungslauf-kreditoren.tsx` zeigt kompakten Zahlungsfallkopf, Kontext und Timeline ohne Zusatz-Requests.
**Erledigt:** `zahlungslauf-kreditoren.tsx` fuehrt den Kreditorenlauf jetzt mit Freigabe-, Skonto- und Ausfuehrungsdruck ueber dem bestehenden SEPA-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-034

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lastschriftlauf als Debitoren-Follow-up mit Mandats-, Frist- und Ausfuehrungsdruck darstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx`
**Abnahmekriterien:** `lastschriften-debitoren.tsx` bekommt denselben leichten Vorgangsrahmen fuer Mandatslage, Freigabe und Export.
**Erledigt:** `lastschriften-debitoren.tsx` surfact Mandatsluecken, Debitorenlauf und Freigabestatus jetzt als kompakten Follow-up-Rahmen ueber dem ObjectPage-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-035

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchhaltungsuebersicht als L3/FIBU-Cockpit mit Perioden- und Schnittstellenlage professionell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchhaltungsuebersicht.tsx`
**Abnahmekriterien:** `buchhaltungsuebersicht.tsx` zeigt kompakten Operatorrahmen fuer Periodenlage, Exportpfad und Revisionskontext.
**Erledigt:** `fibu/buchhaltungsuebersicht.tsx` verdichtet Periodenlage, Revisionskontext und Folgepfade jetzt als L3/FIBU-Cockpit ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-036

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Waagenliste als physischer Leitknoten auf das einheitliche Fallmodell ziehen, ohne die bestehende Uebersicht zu ueberladen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/liste.tsx`
**Abnahmekriterien:** `waage/liste.tsx` fuehrt kompakten Fallkopf, Kontext und Timeline fuer den physischen Kettenzustand aus vorhandenen Daten.
**Erledigt:** `waage/liste.tsx` nutzt jetzt denselben leichten Fallrahmen fuer Bottleneck, Eichlage und die physische Kette direkt ueber der Operatorliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-037

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Bankabgleich als echter Klaerungs- und Ausgleichsfall mit Owner, Matching-Druck und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
**Abnahmekriterien:** `bank-abgleich.tsx` nutzt den leichten Fallrahmen ohne neue Requests und macht offene Matching-Lage sofort lesbar.

## OP-ROLL-038

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Payment-Matching als FIBU-Klaerungsarbeitsplatz mit Kontext, Timeline und Folgepfad professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/payment-matching.tsx`
**Abnahmekriterien:** `payment-matching.tsx` fuehrt Rueckstand, Matching-Risiko und naechste Aktion komprimiert ueber dem Arbeitsraum.

## OP-ROLL-039

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** AP-Invoices-Liste als operativer Pruef- und Freigabestauplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoices-list.tsx`
**Abnahmekriterien:** `ap-invoices-list.tsx` zeigt Stau, Blocker und naechste Sammelaktion aus vorhandenen Listen-/Statusdaten.

## OP-ROLL-040

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** AP-Invoice-Form als echter Pruef- und Buchungsfall mit Governance- und Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoice-form.tsx`
**Abnahmekriterien:** `ap-invoice-form.tsx` erhaelt den leichten Fallrahmen fuer Freigabe, Blocker und naechste Massnahme ohne neue API-Last.

## OP-ROLL-041

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** FIBU-Offene-Posten-Gesamtraum als operatorischer Sammelfall zwischen Debitoren und Kreditoren verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/offene-posten.tsx`
**Abnahmekriterien:** `fibu/offene-posten.tsx` zeigt OP-Druck, Ausgleichslage und Folgeweg ueber dem Arbeitsraum.

## OP-ROLL-042

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Zahlungseingaenge als echter Clearing- und Rueckstandsraum mit kompaktem Vorgangsbild heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungseingaenge.tsx`
**Abnahmekriterien:** `zahlungseingaenge.tsx` surfact Rueckstand, Abgleichslage und naechste Aktion oberhalb der Facharbeit.

## OP-ROLL-043

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Zahlungsvorschlaege als FIBU-Entscheidungsraum mit Priorisierung und Governance-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungsvorschlaege.tsx`
**Abnahmekriterien:** `zahlungsvorschlaege.tsx` zeigt Prioritaet, Liquiditaetsdruck und naechste Folgeaktion ohne neue Requests.

## OP-ROLL-044

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** BWA als Fiori-artigen Analysearbeitsplatz mit Perioden-, Abweichungs- und Folgekontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bwa.tsx`
**Abnahmekriterien:** `bwa.tsx` fuehrt Fallkopf, Kontext und Timeline aus bereits geladenen Auswertungsdaten.

## OP-ROLL-045

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Bilanz als L3/FIBU-Abschlussraum mit Risiko- und Folgepfad konsistent zum neuen Arbeitsmodell ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bilanz.tsx`
**Abnahmekriterien:** `bilanz.tsx` liefert kompakten Operatorrahmen fuer Abschlusslage, Revisionskontext und Drilldown-Folgewege.

## OP-ROLL-046

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Rueckverfolgung als physischer Ausnahme- und Nachweisfall mit Charge-/Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/rueckverfolgung.tsx`
**Abnahmekriterien:** `charge/rueckverfolgung.tsx` zeigt Status, Blocker und Folgewege fuer Charge-/Nachweisfaelle ohne neuen Datenpfad.

## OP-ROLL-047

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Wareneingang als physischer Fall zwischen Annahme, Charge und Lager deutlich mit dem Zielbild verknuepfen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/wareneingang.tsx`
**Abnahmekriterien:** `charge/wareneingang.tsx` fuehrt den leichten Fallrahmen fuer Ressource, Blocker und naechste Aktion aus vorhandenen Daten.

## OP-ROLL-048

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Tourenplanung als Logistik-Leitraum mit Folgecharakter, Bottleneck und Aktionspriorisierung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/tourenplanung.tsx`
**Abnahmekriterien:** `tourenplanung.tsx` bekommt den kompakten Vorgangsrahmen fuer Druck, Blocker und naechste Massnahme ohne Zusatz-Requests.
