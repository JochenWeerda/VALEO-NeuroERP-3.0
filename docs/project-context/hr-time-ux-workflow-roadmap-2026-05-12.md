---
title: HR-Time UX Workflow Roadmap 2026-05-12
type: explanation
audience: [entwickler, product]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: UX-Roadmap fuer klickarmes HR-Time-Arbeitscockpit — Prozessauffuehrung statt CRUD-Masken-Sammlung; Zielbild und Maskentypen fuer Zeiterfassung und Abwesenheit (Stand 2026-05-12).
---

# HR-Time UX Workflow Roadmap

Stand: 2026-05-12

## Zielbild

HR-Time wird als klickarmes Arbeitscockpit gefuehrt, nicht als Sammlung isolierter CRUD-Masken. Der Nutzer startet mit einer fachlichen Frage, sieht sofort den passenden Arbeitsvorrat, filtert nach wenigen Kriterien und kann den Prozess bis zum naechsten revisionsfaehigen Status abschliessen.

Grundsaetze:

- maximal ein zentraler Such-/Filterbereich je Cockpit
- Zeilenaktionen statt manueller ID-Eingabe
- Blocker zuerst, Details erst nach Auswahl
- Listen, Kalender und Formulare zeigen denselben Kontext
- Agent-Hinweise sind priorisierte Arbeitsauftraege, keine dekorativen Texte
- Druck, Export und Handoff sind explizite Endpunkte eines Workflows

## User-Fragen, Masken und Antworten

| User-Frage | Primaere Maske | Eingeblendete Information | Direktaktion |
|------------|----------------|---------------------------|--------------|
| Was ist heute offen? | Agent Worklist | Blocker, Freigaben, Payroll-Bereitschaft, Planungswarnungen | Blocker bearbeiten, Payroll vorbereiten, Schicht pruefen |
| Wer fehlt oder blockiert Planung? | Arbeitsplan + Praeferenz-Checks | Abwesenheit, Schulferien, Brueckentage, Feiertage, Nachttour-Praeferenzen | Ersatz planen, Arbeitsplan drucken |
| Welche Zeit muss korrigiert werden? | Arbeitszeitliste | Zeit, Typ, Status, Mitarbeiter, Aktion Bearbeiten | Korrigieren und erneut einreichen |
| Wer kann eine Tour/Schicht fahren? | Planung / Driver-Dispo | Rolle, Qualifikation, Verfuegbarkeit, Lenkzeit, Fahrzeug | Vorschlag uebernehmen, Fahrer ersetzen |
| Kann Payroll exportiert werden? | Payroll-Readiness | bereite Eintraege, blockierte Eintraege, Blockerliste | Exportpaket erzeugen, Blocker oeffnen |
| Welche Kampagne erzeugt Engpass? | Kampagnenplanung | Rollenbedarf, Schichten, Abwesenheiten, erwartetes Volumen | Kampagne pruefen, Zusatzschicht anlegen |
| Welche Aussendiensttermine kollidieren? | Aussendienstplanung | Kunde, Gebiet, Kampagne, Kalender, Abwesenheit | Besuch planen, Termin verschieben |

## Such-, Filter- und Sortierkonzept

Alle operativen HR-Time-Sichten erhalten dieselbe Bedienlogik:

- Suche: Mitarbeiter, Tour, Fahrzeug, Kunde, Kampagne, Schichtname, Befundcode.
- Schnellfilter: `Alle`, `Nur Blocker`, `Nur Warnungen`, `Druckbereit`, `Fahrer`, `Payroll`.
- Zeitraum: Heute, Morgen, Woche sowie manuelles Datum.
- Sortierung: Prioritaet, Datum/Zeit, Mitarbeiter, Status, Schweregrad.
- Gespeicherte spaetere Ansichten: `Dispo LKW`, `HR Freigaben`, `Payroll`, `Ernteannahme`, `Aussendienst`.

Aktueller erster Umsetzungsschritt:

- zentrale Suche, Schnellfilter und Sortierung im Zeiterfassungscockpit
- angewendet auf klassische Arbeitszeit und Arbeitsplan
- E2E-Test prueft, dass Such-/Filter-/Sortierpfade im Browser funktionieren

## Roadmap Mit Milestones

| Milestone | Slice-Fokus | Ziel | Quervernetzungen | Abnahme |
|-----------|-------------|------|------------------|---------|
| ~~UX-M1 Arbeitsvorrat finden~~ | ~~`HR-TIME-UX-ROADMAP-001`~~ | ~~Suche, Schnellfilter und Sortierung fuer Arbeitszeit und Arbeitsplan~~ | HR-Time-Cockpit, Agent Worklist, Payroll-Readiness | **Umgesetzt 2026-06-27** in `zeiterfassung.tsx`: Suchfeld, 6 Schnellfilter (Alle/Blocker/Warnungen/Druckbereit/Fahrer/Payroll), 4 Sortierungen (Prioritaet/Datum/Mitarbeiter/Status), Reset-Button — vollstaendig implementiert. |
| ~~UX-M2 Detail- und Aktionspanel~~ | ~~`HR-TIME-ACTIONPANEL-001`~~ | ~~Rechte Detailspalte fuer ausgewaehlte Zeit, Schicht, Fahrer, Payroll-Blocker~~ | `time_entries`, `shifts`, `work-plan`, DMS/Audit | **Umgesetzt 2026-06-27** in `zeiterfassung.tsx`: Rechtes Detail-Panel erscheint bei Row-Fokus im Zeiten- und Arbeitsplan-Tab; zeigt Mitarbeiter/Status/Compliance-Befunde/Aktionen (Bearbeiten, Einreichen, Drucken). |
| UX-M3 Gefuehrter Planungswizard | `HR-TIME-WIZARD-001` | Arbeitsplan erstellen in Schritten: Zeitraum, Bedarf, Praeferenzen, Vorschlag, Druck | Schichtplanung, Abwesenheit, Kalender, Kampagne | Schicht-/Tourvorschlag entsteht ohne manuelle Mehrfacherfassung |
| ~~UX-M4 Driver-Dispo~~ | ~~`HR-TIME-DRIVER-DISPO-001`~~ | ~~LKW-Fahrer, Tour, Fahrzeug, Lenkzeit und Tacho in einer Sicht~~ | Tourenplanung, Fuhrpark, Waage, Driver-Time | **Umgesetzt 2026-06-27** in `zeiterfassung.tsx`: Driver-Tab mit KPI-Badges (Blocker/Warnungen/Fahrzeit), Row-Fokus → Detail-Panel (Fahrer/Tour/Fahrzeug/Dauer/Plausibilitaets-Checks), Tour/Fahrzeug-Korrektur via PATCH `/driver-time/events/{id}`; `useUpdateDriverTimeEvent`-Hook in `personal.ts`. |
| ~~UX-M5 Payroll Closeout~~ | ~~`HR-TIME-PAYROLL-CLOSE-001`~~ | ~~Blocker abarbeiten bis Exportpaket~~ | Zeitbuchung, Freigabe, Payroll, DMS | **Umgesetzt 2026-06-27** in `zeiterfassung.tsx`: Export-Gate im Header- und Agent-Tab-Button (disabled bei Blockern); Payroll-Tab zeigt Gate-Banner mit per-Blocker-Auflösungshinweisen und "Pruefen"-Direktlink → Steuerung; Freigabe-Banner bei Status=ready. |
| UX-M6 Mobile/Terminal | `HR-TIME-MOBILE-001` | Touch-optimierte Buchung fuer Fahrer, Lager, Saisonkraefte | PWA, Offline-Queue, Auth, Audit | Buchung/Korrektur funktioniert mit sehr wenigen Eingaben |
| UX-M7 Kalender- und Saisonleitstand | `HR-TIME-SEASON-BOARD-001` | Heatmap fuer Kampagnen, Ferien, Feiertage, Brueckentage | Kampagne, Kalender, Waage, Silo, Aussendienst | Engpaesse werden vor der Woche sichtbar |

## Quervernetzungen

| Knoten | Verbunden mit | Warum |
|--------|---------------|-------|
| Arbeitszeit | Payroll, Audit, Kostenstellen | Freigegebene Zeiten sind Lohn- und Kostenbasis |
| Abwesenheit | Schicht, Tour, Aussendienst, Kalender | Jede genehmigte Abwesenheit ist Planungsblocker |
| Driver-Time | Tour, Fahrzeug, Waage, Tacho, Payroll | Fahrerzeit ist Spezialfall mit Compliance und Spesenbezug |
| Arbeitsplan | Schicht, Kalender, Kampagne, Schulferien | Planung braucht Verfuegbarkeit und Praeferenzen |
| Kampagne | Waage, Lager, Silo, Fahrer, Aussendienst | Landhandel-Arbeitsspitzen entstehen pro Prozesskette |
| Payroll | Freigabe, Korrektur, DMS, Steuerbuero | Export muss nachvollziehbar und wiederholbar sein |
| Agent Worklist | alle Blockerquellen | Agent priorisiert Arbeit, entscheidet aber nicht final |

## Umsetzungsschnitt Fuer UX-M1 (umgesetzt 2026-06-27)

Dateien:

- `packages/frontend-web/src/pages/personal/zeiterfassung.tsx` ✅ fertig

Umgesetzte Akzeptanz:

- Suchfeld (`searchTerm`) filtert Zeilen in Arbeitszeit (`filteredTimeEntries`) und Arbeitsplan (`filteredWorkPlanAssignments`).
- 6 Schnellfilter (`quickFilter`): Alle, Nur Blocker, Nur Warnungen, Druckbereit, Fahrer, Payroll — ohne Tab-Wechsel aktiv.
- 4 Sortierungen (`sortMode`): Prioritaet, Datum/Zeit, Mitarbeiter, Status.
- Reset-Button setzt alle drei Filter-Felder zurueck.
- Agent-Worklist-Tab zeigt priorisierte Arbeitsauftraege mit Badge-Severity.

## Folge-Slices

| Slice | Kurzinhalt | Voraussetzung |
|-------|------------|---------------|
| `HR-TIME-ACTIONPANEL-001` | Ausgewaehlter Datensatz rechts mit Detail, Befunden und erlaubten Aktionen | UX-M1 |
| `HR-TIME-WIZARD-001` | Arbeitsplan-Assistent mit Vorschlagsuebernahme | Arbeitsplanvertrag stabil |
| `HR-TIME-DRIVER-DISPO-001` | Fahrer-/Tour-/Fahrzeug-Leitstand | Driver-Time + Tourdaten |
| `HR-TIME-PAYROLL-CLOSE-001` | Blocker bis Export abarbeiten | Payroll-Vertrag + Freigabe |
| `HR-TIME-SEASON-BOARD-001` | Saison-/Kampagnenheatmap | Kampagnenkapazitaet + Kalender |
