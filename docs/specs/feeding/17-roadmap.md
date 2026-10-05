---
title: "Fuetterungsberatung — Roadmap und 240-Pakete-Arbeitsprogramm"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Abhaengigkeits- und releaseorientierte Lieferstrategie fuer das vollstaendige integrierte System.
---

# 17 — Roadmap

## 1. Liefermodell

Die Roadmap kombiniert die Releases A–C aus `implementation-plan.md` mit
[240 einzeln claimbaren TDD-Paketen](work-packages/README.md). Pakete sind keine
starren Kalenderzusagen. Priorisiert wird nach Nutzerwert, Risiko, Abhaengigkeit
und nachgewiesener Daten-/Regelreife.

## 2. Programmstruktur

| Bereich | Pakete | Release-Schwerpunkt |
|---|---:|---|
| Betriebsakte, Gruppen, Einheiten, Futter, Analysen, Bedarf | 001–060 | A Kern |
| Ration, Editor, Warnungen, Optimierung, Varianten | 061–110 | A Editor |
| Plan, Ausfuehrung, Versorgung, Einkauf | 111–150 | B Betrieb |
| Leistung, Beratung, Massnahmen, Berichte, Zusammenarbeit | 151–200 | C Beratung |
| Labor, Herd-Data, Mixer, Agenten | 201–240 | B/C Integration und Assistenz |

## 3. Abhaengigkeits-Spine

```text
Betrieb → Gruppe → Einheiten → Futter → Analyse → Bedarf
→ Ration → Bewertung/Optimierung → Variante → Plan
→ Ausfuehrung/Versorgung → Leistung → Beratung/Massnahme/Bericht
```

Integrationen docken an freigegebene neutrale Ports an. Agenten folgen erst,
wenn Policy, lesende Werkzeuge und fachliche Evidenz des jeweiligen Bereichs
stehen. Ein externes Live-Gate blockiert nicht den neutralen Vertrag, wohl aber
die Kennzeichnung als produktiv.

## 4. Claim- und Ausfuehrungsregel

Vor Beginn: Abhaengigkeiten und Workboard pruefen, Paket reservieren, Slice-YAML
und Claim-Commit erstellen. Dann Red → Green → Refactor → Regression. Ein Paket
bleibt offen, bis seine Definition of Done und Requirement-Traceability belegt
sind. Parallelisierung ist nur mit klarem Datei-/Themenbesitz zulaessig.

## 5. Release A — beratungsfaehig

Release A endet nicht mit vorhandenen Tabellen. Ein Berater kann einen
berechtigten Betrieb oeffnen, Datenreife herstellen, eine reproduzierbare Ration
erstellen, Warnungen verstehen, Varianten vergleichen, freigeben und berichten.
Pflicht: Pakete 001–110 soweit fuer diese Journey relevant, Golden-/Security-/
A11y-/Performance-Gates und Pilotabnahme am synthetischen Referenzbetrieb.

## 6. Release B — betriebsfaehig

Ein freigegebener Stand wird als unveraenderlicher Plan ausgegeben, mobil oder
maschinenlesbar ausgefuehrt, mit Ist-Daten abgeglichen und in Versorgung/Einkauf
uebergeben. Pflicht: Pakete 111–150 sowie relevante Labor-/Mixerpakete 201–230.

## 7. Release C — controlling- und beratungsfaehig

Leistungsdaten, Beratung, Massnahmen, Zusammenarbeit und Berichte bilden einen
nachvollziehbaren Wirkungskreislauf. Agenten unterstuetzen erklaerbar innerhalb
von Policies und Human Gates. Pflicht: Pakete 151–200 und 231–240.

## 8. Aufwand und Kapazitaet

S/M/L in den Paketdokumenten sind Vor-Refinement-Spannen von 1–2, 3–5 und 6–10
Personentagen. Sie enthalten Implementierung, Test, Doku und Abnahme, aber keine
Wartezeit externer Gates. Forecasts werden aus gemessener Durchlaufzeit erstellt,
nicht durch Addition als scheinexakter Fixtermin.

## 9. Steuerungsmetriken

- verifizierte Requirements und FEED-T-Tests je Capability;
- Red-Green-Evidenzquote und escaped defects;
- Durchlaufzeit, Blockierzeit und Rework;
- Datenreife, Journey-Erfolg und fachliche Pilotabnahme;
- offene P0/P1-Schulden und externe Gates;
- Doku-/OpenAPI-/Migration-/Screen-Drift.

## 10. Aktueller Startpunkt

FEED-CORE-015 und damit ein erster Teil der Pakete 001–010 ist produktiv
umgesetzt und getestet. Der Paketkatalog ersetzt nicht die bestehende
Slicehistorie; beim Claim wird das passendste Paket mit dem neuen oder bereits
abgeschlossenen Slice verknuepft. Naechster Kernpfad ist der Tiergruppen-Ausbau,
sofern die Vollstaendigkeitsgates dieses Referenzwerks gruen sind.

## 11. Abschlusskriterium des Gesamtprogramms

Das Programm ist erst fertig, wenn alle expliziten Requirements entweder
VERIFIED oder fachlich begruendet NOT_APPLICABLE sind, externe BLOCKED-Pfade nicht
als geliefert ausgegeben werden, alle Release-Journeys und Querschnittsgates
gruen sind und der aktuelle Produktionsstand die Kapitel 00–17 ohne Drift
widerspiegelt.
