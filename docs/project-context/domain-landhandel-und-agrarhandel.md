---
title: Domain — Landhandel und Agrarhandel
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Fachliche Realitaet des Landhandels/Agrarhandels — Grundlage fuer Prozessanalyse und Workflow-Validierung in VALEO NeuroERP.
---

# Domain Landhandel und Agrarhandel

## Zweck

Diese Datei beschreibt die fachliche Realitaet, an der Prozessanalyse und Workflow-Validierung ausgerichtet werden muessen.

## Typische Praxis im Landhandel

- Prozesse sind haeufig nicht streng linear.
- Direktstarts sind normal: z. B. Direktlieferschein, Sofortabholung, Wareneingang ohne perfekte Vorstufe.
- Mengen, Preise und Konditionen aendern sich entlang des Prozesses.
- Teilmengen, Splittung, Nachbelastung, Korrektur, Storno und Retoure sind Regelfaelle, keine Ausnahmen.
- Saison-, Ernte- und Kampagnengeschaeft erzeugen hohe Last, Zeitdruck und pragmatische Abkuerzungen.

## Typische Sonderfaelle

- externe Uebernahmen aus Agrarportal, Online-Shop oder Fremdsystemen
- telefonische oder kurzfristige Belegstarts
- abweichende Lieferadresse oder Werk-/Lagerbezug
- Teillieferung, Restmengenfuehrung, Nachlieferung
- Preisfindung spaeter als Auftragserfassung
- Sammelrechnung, Barverkauf, Sofortbelastung
- Qualitaetsabweichung, Reklamation, Retoure, Gutschrift oder Belastung

## Fachliche Leitlinie fuer Workflow-Pruefung

Jeder Prozess ist gegen folgende Praxisfragen zu pruefen:

- Gibt es realistische Standardstarts?
- Gibt es direkte Alternativstarts?
- Sind Verzweigungen, Schleifen und Rueckspruenge abbildbar?
- Koennen Benutzer pragmatisch arbeiten, ohne Medienbruch zu erzeugen?
- Ist ein fachlich sauberer Abschluss moeglich, auch wenn der Start unvollstaendig oder verkuerzt war?

## Umgang mit Annahmen

Wenn fachliche Details im System oder in der Doku fehlen:

- plausible Annahmen auf Basis typischer Landhandelsprozesse treffen
- Annahmen explizit kennzeichnen
- die Doku im passenden Bereich ergaenzen

## Relevanz fuer UI und Masken

Standardmasken bleiben der Normalfall fuer robuste Datenerfassung.
Spezialmasken oder Schnellmasken sind nur dann sinnvoll, wenn:

- der Einstieg stark vereinfacht werden muss
- das Tagesgeschaeft einen echten Direktprozess braucht
- die Standardmaske dadurch nicht ueberladen oder unklar wird

Verbindliche Entscheidungsregel dazu:

- [ADR-031 Standardmaske vs Spezialmaske](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/adr/adr-031-standardmaske-vs-spezialmaske.md)
