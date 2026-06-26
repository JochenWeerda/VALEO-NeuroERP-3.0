---
title: Controlling und Kostenrechnung
type: how-to
audience: [endnutzer, power-user]
owner: Codex
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Controlling und Kostenrechnung

Diese Anleitung beschreibt Kostenstellen, Kostenarten, Buchungen, Umlagen,
BAB-Auswertung und Kostenstellenabschluss.

## Voraussetzungen

- Kontenplan, Kostenstellen, Kostentraeger, Projekte oder Abteilungen sind
  gepflegt.
- Buchungsperiode und Auswertungszeitraum sind offen.
- Kostenstellen-Mappings aus FIBU, Einkauf, Verkauf, Logistik und HR sind
  fachlich freigegeben.

## Kostenstelle anlegen oder pflegen

1. Oeffnen Sie *FIBU* -> *Kostenstellen*.
2. Wechseln Sie in den Tab *Kostenstellen*.
3. Erfassen Sie Nummer, Bezeichnung, Art und Budget.
4. Speichern Sie die Kostenstelle.
5. Deaktivieren Sie nicht mehr genutzte Kostenstellen statt sie in laufenden
   Perioden zu loeschen.

## Kosten buchen

1. Wechseln Sie in den Tab *Buchungen*.
2. Waehlen Sie Kostenstelle, Kostenart, Datum und Betrag.
3. Erfassen Sie einen nachvollziehbaren Buchungstext.
4. Speichern Sie die Buchung.
5. Pruefen Sie die Auswertung fuer den Zeitraum.

## Umlage erfassen

1. Wechseln Sie in den Tab *BAB*.
2. Waehlen Sie Periode, Quell- und Zielkostenstelle.
3. Waehlen Sie Umlageart: Prozent, Betrag oder Menge.
4. Erfassen Sie Wert und Basis.
5. Speichern Sie die Umlage.
6. Pruefen Sie Primaerkosten, Umlagen und Gesamtkosten je Kostenstelle.

## Kostenstellenabschluss pruefen

1. Oeffnen Sie die Controlling-/Kostenrechnungs-Auswertung.
2. Pruefen Sie Budget, Ist, Abweichung und offene Buchungen.
3. Klaeren Sie fehlende oder falsche Kostenstellenzuordnungen.
4. Schliessen Sie die Periode erst, wenn keine relevanten Buchungen mehr fehlen.
5. Nach Abschluss duerfen fuer die gesperrte Periode keine neuen Ist-Buchungen
   ohne definierte Korrektur-/Storno-Regel erfolgen.

## Ergebnis

- Kostenstellen und Kostenarten sind auswertbar.
- BAB und Umlagen zeigen die Verteilung von Primaer- und Sekundaerkosten.
- Budget-/Ist-Abweichungen sind sichtbar.
- Abgeschlossene Perioden sind gegen nachtraegliche Ist-Buchungen geschuetzt.

## Haeufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Kostenstelle fehlt in Buchung | Stammdaten oder Mapping unvollstaendig | Kostenstelle anlegen und Mapping pruefen |
| Umlagebetrag wirkt falsch | Basis, Prozent oder Quellkostenstelle falsch | Umlageparameter und BAB pruefen |
| Periode laesst sich nicht schliessen | Offene Buchungen oder fehlende Freigabe | offene Positionen klaeren |
| Auswertung leer | Zeitraum, aktive Kostenstelle oder Mandant falsch | Filter und Stammdaten pruefen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/finance.tsx` und
  `packages/frontend-web/src/app/navigation/fibu-suite.tsx`: Navigation
  *Kostenstellen*.
- `packages/frontend-web/src/pages/fibu/kostenstellenrechnung.tsx`:
  Auswertung, BAB, Kostenstellen, Kostenarten und Buchungen.
- `docs/agent-ops/slices/DOM-CONTROLLING-004.yaml`: Budget-Lifecycle,
  Plan/Ist-Abweichung und Kostenstellenabschluss.
- `docs/workflows/dom-controlling-004-controlling-deepening-2026-06-23.md`:
  fachlicher Controlling-Workflow.
- `docs/project-context/open-gaps-and-known-issues.md`: externe Freigabe der
  Konten-/Steuer-/Kostenstellen-Mappings.

Reverse-Pflege: Wenn Kostenstellenarten, BAB-Logik, Umlagearten, Periodenstatus,
Budgetregeln oder FIBU-/HR-/Logistik-Mappings geaendert werden, diese Seite und
die Controlling-Workflow-Dokumente gemeinsam aktualisieren.
