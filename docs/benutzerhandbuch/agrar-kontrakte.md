---
title: Agrar-Kontrakte
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# Agrar-Kontrakte

Diese Anleitung beschreibt die Kontraktsteuerung im Landhandel: Kontrakt anlegen,
Erfüllung verfolgen, MATIF-Fixierung, Engagement/Mahnung und Settlement.

## Voraussetzungen

- Modul **Kontrakte** ist für den Mandanten freigeschaltet.
- Partei (Lieferant/Kunde), Artikel/Frucht und Kontraktart sind gepflegt.
- Für MATIF-Fixierungen liegt eine aktuelle Marktnotierung vor.
- Mengenzeiträume und Zu-/Abschläge sind konfiguriert.

## Kontrakt anlegen und prüfen

1. Öffnen Sie *Kontrakte* → *Kontraktübersicht*.
2. Legen Sie einen neuen Kontrakt an oder öffnen Sie einen bestehenden.
3. Prüfen Sie Partei, Frucht, Kontraktart, Menge, Preislogik und Lieferzeitraum.
4. Speichern Sie den Kontrakt und prüfen Sie den Status (offen, teilfixiert, abgeschlossen).

## Erfüllung und Abruf steuern

1. Öffnen Sie *Kontrakte* → *Kontrakt-Erfüllung*.
2. Prüfen Sie offene, abgerufene und überfällige Mengen je Partei und Artikel.
3. Ordnen Sie Annahmen, Lieferungen oder Abrufe dem Kontrakt zu.
4. Klären Sie Abweichungen (Teillieferung, Qualitätsabschlag) vor dem Abschluss.

## MATIF-Fixierung und Bewertung

1. Öffnen Sie *Kontrakte* → *Kontrakt-Fixierung*.
2. Wählen Sie eine MATIF-bepreiste Position mit offener Menge.
3. Erfassen Sie Fixierungsmenge und Fixpreis (inkl. Prämie/Basis).
4. Prüfen Sie fixiert/offen, Durchschnittsfixpreis und Mark-to-Market-Bewertung.
5. Speichern Sie die Fixierung. Ungültige Mengen oder fehlende Notierung führen zu 422.

## Engagement, Mahnung und Settlement

1. Öffnen Sie *Kontrakte* → *Kontrakt-Engagement* für die Mengenübersicht je Artikel/Partei.
2. Prüfen Sie Mahnkandidaten und eskalieren Sie bei offener Kontraktmenge.
3. Öffnen Sie *Kontrakt-Settlement* für die Abrechnung/Verrechnung abgeschlossener Positionen.
4. Prüfen Sie Netto-Vorzeichen, offene Restmengen und Abrechnungsstatus.

## Ergebnis

- Kontrakt, Erfüllung, Fixierung und Settlement bilden eine nachvollziehbare Kette.
- Offene und überfällige Mengen sind vor Mahnlauf und Abrechnung sichtbar.
- MATIF-Bewertungen basieren auf hinterlegten Notierungen, nicht auf Schätzwerten.

## Häufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Fixierung blockiert | Menge größer als offen oder keine MATIF-Position | Offene Menge und Kontraktart prüfen |
| Keine Bewertung | Marktnotierung fehlt | Notierung pflegen oder Fixierung verschieben |
| Mahnung nicht möglich | Keine offene Kontraktmenge | Engagement-Stand prüfen |
| Settlement unvollständig | Positionen noch nicht erfüllt/abgerechnet | Erfüllung und Belegbezüge nachziehen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/commercial.tsx`: Menü Kontrakte
  (Übersicht, Erfüllung, Fixierung, Engagement, Settlement).
- `docs/agent-ops/slices/DOM-CON-004.yaml`: Kontrakt-Erfüllung, Fixierung, Engagement.
- `docs/workflows/dom-con-004-kontrakt-erfuellung-2026-06-10.md`: fachliche Vertiefung.
- `docs/benutzerhandbuch/annahme.md`: Verknüpfung Annahme → Kontrakt-Erfüllung.

Reverse-Pflege: Bei Änderungen an Fixierungsregeln, Engagement-Berechnung,
Mahnstufen oder Settlement-Status diese Seite und die Kontrakt-Workflow-Doku
gemeinsam aktualisieren.
