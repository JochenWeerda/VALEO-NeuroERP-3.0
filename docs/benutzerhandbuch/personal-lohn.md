---
title: Personal, Zeit und Lohn
type: how-to
audience: [endnutzer, power-user]
owner: Codex
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Personal, Zeit und Lohn

Diese Anleitung beschreibt die taegliche Arbeit mit Mitarbeitenden,
Zeiterfassung, Abwesenheiten, Payroll-Readiness und Lohnbuchungsuebergabe.

!!! warning "Payroll ist ein Freigabeprozess"
    VALEO bereitet Zeit- und Lohnbuchungsdaten fuer Payroll/DATEV vor.
    Produktive Lohnabrechnung, amtliche PAP-Pruefung, DATEV-/Providerformat,
    Steuerberaterfreigabe, Betriebsvereinbarung und Datenschutzfreigabe bleiben
    externe Gates.

## Voraussetzungen

- Mitarbeiter, Organisation, Rolle, Kostenstelle und Arbeitsmodell sind gepflegt.
- Zeitbuchungen werden durch berechtigte Personen erfasst oder importiert.
- Abwesenheiten und Fahrerzeiten sind vor dem Payroll-Paket geklaert.
- HRM-Betriebsfreigaben sind fuer den Mandanten dokumentiert.

## Zeit erfassen und freigeben

1. Oeffnen Sie *Personal* -> *Zeiterfassung*.
2. Waehlen Sie Datum oder Zeitraum.
3. Erfassen Sie Kommen, Gehen, Pause, Arbeitsbereich und Kostenstelle.
4. Reichen Sie die Buchung ein.
5. Fuehrung oder HR prueft Warnungen und genehmigt die Buchung.
6. Korrekturen nur mit Grund und Auditspur erfassen.

## Abwesenheit erfassen

1. Oeffnen Sie den Abwesenheitsbereich in der Zeiterfassung oder Personalmaske.
2. Erfassen Sie Person, Typ, Zeitraum und Grund.
3. Pruefen Sie Kollisionen mit Tour, Schicht, Aussendienst oder Payroll.
4. Geben Sie die Abwesenheit frei oder lehnen Sie sie begruendet ab.

## Payroll-Paket vorbereiten

1. Oeffnen Sie in *Zeiterfassung* den Tab *Payroll*.
2. Pruefen Sie Payroll-Readiness: bereit, blockiert, offene Freigaben.
3. Klaeren Sie Blocker wie fehlende Kostenstelle, nicht genehmigte Zeit,
   Abwesenheitskollision oder fehlendes Lohnartenmapping.
4. Erzeugen Sie das Payroll-Paket.
5. Pruefen Sie Items, Zeitraum, Zielsystem und Blockerliste.

## Lohnbuchungen in die FIBU uebernehmen

1. Oeffnen Sie *FIBU* -> *Lohn-Connector*.
2. Laden oder starten Sie den Lohn-Importlauf.
3. Pruefen Sie Summen, Konten, Gegenkonten und Kostenstellen.
4. Validieren Sie den Lauf.
5. Buchen Sie erst nach fachlicher Freigabe ins Journal.

## Ergebnis

- Zeitbuchungen sind genehmigt, korrigierbar und auditierbar.
- Abwesenheiten blockieren Planung und Payroll nachvollziehbar.
- Payroll-Pakete enthalten nur freigegebene Werte oder klare Blocker.
- Lohnbuchungen werden kontrolliert in die FIBU uebernommen.

## Haeufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Payroll bleibt blockiert | Offene Zeitfreigabe oder Abwesenheitskollision | Freigabe/Kollision in Zeiterfassung klaeren |
| Kostenstelle fehlt | Mitarbeiterprofil oder Buchung unvollstaendig | Kostenstelle nachpflegen und Paket neu erzeugen |
| Lohn-Import wird abgelehnt | Format, Konto oder Mapping ungueltig | Connector-Profil und Mapping pruefen |
| Fahrerzeit-Warnung | Ueberlappung, fehlende Tour oder fehlende Korrektur | Driver-Time-Ereignis nachbearbeiten |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: Personal-
  Navigation mit Mitarbeiterliste, Zeiterfassung, Stundenzettel und Gates.
- `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`: Time-&-Labor,
  Abwesenheiten, Driver-Time und Payroll-Readiness.
- `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`: HRM-
  Betriebsfreigaben, DATEV-/Payroll-Gate und Evidenztypen.
- `packages/frontend-web/src/pages/fibu/lohn-connector.tsx`: Lohn-Importlaeufe
  in die Finanzbuchhaltung.
- `docs/agent-ops/slices/HR-TIME-PAY-001.yaml`,
  `docs/agent-ops/slices/HRM-PAYROLL-DEEP-001.yaml` und
  `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`:
  Zeit-, Payroll- und Driver-Time-Vertraege.

Reverse-Pflege: Wenn Zeitstatus, Abwesenheitstypen, Payroll-Exportfelder,
Lohnarten, Kostenstellenmapping oder Lohn-Connectoren geaendert werden, diese
Seite und die HRM-/Payroll-Freigabedokumente gemeinsam aktualisieren.
