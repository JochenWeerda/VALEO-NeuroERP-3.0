---
title: Futtermittel und Produktion
type: how-to
audience: [endnutzer, power-user]
owner: Codex
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Futtermittel und Produktion

Diese Anleitung beschreibt die Kette Einzelfuttermittel -> Rezeptur ->
Produktionsauftrag -> Charge -> QS/Trace.

## Voraussetzungen

- Einzelfuttermittel sind gepflegt und mit Lagerartikeln verknuepft.
- Rezepturen sind vollstaendig und fachlich freigegeben.
- Rohwarenbestand ist verfuegbar und QS-seitig nicht gesperrt.
- Produktions- und QS-Rollen sind fuer den Mandanten freigegeben.

## Einzelfutter und Mischfutter pflegen

1. Oeffnen Sie *Futtermittel* -> *Einzelfuttermittel*.
2. Pruefen Sie Artikelnummer, Name, Kategorie, Naehrwerte und Status.
3. Oeffnen Sie *Mischfuttermittel* fuer Rezeptur- oder Produktpflege.
4. Berechnen oder pruefen Sie Naehrwerte nach Aenderungen.
5. Archivieren oder sperren Sie nicht mehr verwendbare Futtermittel.

## Futtermittel-Wareneingang buchen

1. Oeffnen Sie *Futtermittel* -> *Wareneingang*.
2. Waehlen Sie Lieferant, Artikel, Menge, Lagerort und Charge.
3. Erfassen Sie QS-/Analysehinweise.
4. Buchen Sie den Wareneingang.
5. Pruefen Sie, ob der Bestand fuer Rezeptur und Produktion sichtbar ist.

## Mischfutter-Produktionsauftrag erstellen

1. Oeffnen Sie *Produktion* -> *Mischfutter-Produktion*.
2. Waehlen Sie Rezeptur und Produktionsmenge.
3. Pruefen Sie Komponentenbedarf gegen verfuegbaren Bestand.
4. Klaeren Sie fehlende Lagerartikel-Verknuepfungen ueber die Ensure-Aktion.
5. Erfassen oder bestaetigen Sie die Chargen-ID.
6. Erstellen Sie den Produktionsauftrag.

## Produktion freigeben, starten und abschliessen

1. Pruefen Sie den Auftrag in der Auftragsliste.
2. Fuehren Sie die naechste Statusaktion aus:
   freigeben, Produktion starten, fertigmelden oder stornieren.
3. Pruefen Sie bei Freigabe den Bestandsabzug der Einzelfuttermittel.
4. Dokumentieren Sie Abweichungen und QS-Befunde.
5. Oeffnen Sie bei Bedarf den Trace, um Rohwaren, Rezeptur und Fertigcharge zu
   verfolgen.

## Ergebnis

- Rohwarenverbrauch wird mit Produktionsauftrag und Charge verbunden.
- Lagerbewegungen entstehen nur fuer verknuepfte Einzelfuttermittel.
- Rezeptur, Menge, Charge und QS-Status sind vor Produktionsstart sichtbar.
- Trace zeigt die Verbindung von Rohware zu Fertigwaren-Charge.

## Haeufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Produktion nicht startbereit | Rezeptur, Menge, Charge oder Komponente fehlt | Produktionsplan vervollstaendigen |
| Bestand fehlt trotz Rohware | Einzelfutter ist nicht mit Lagerartikel verknuepft | Inventory-Link/Ensure-Aktion ausfuehren |
| Rezeptur kann nicht freigegeben werden | Anteile summieren nicht auf 100 Prozent | Rezepturpositionen korrigieren |
| QS blockiert Fertigmeldung | Charge oder Rohware ist gesperrt | QS-Befund klaeren und Freigabe dokumentieren |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: Navigation
  fuer Futtermittel- und Produktionsseiten.
- `packages/frontend-web/src/pages/produktion/mischfutter-produktion.tsx`:
  Produktionswizard, Bestand, Chargennachweis und Statusaktionen.
- `packages/frontend-web/src/pages/futtermittel/*.tsx`: Einzelfuttermittel,
  Mischfuttermittel, Wareneingang, Statistik und Rationszugang.
- `docs/workflows/wave-physical-chain-feed-production-audit-2026-06-12.md`:
  Audit Rohware -> Rezept -> Produktionsauftrag -> Charge -> QS/Trace.
- `docs/agent-ops/slices/FEED-CHAIN-004.yaml`,
  `docs/agent-ops/slices/FEED-CHAIN-004.5.yaml` und
  `docs/agent-ops/slices/DOM-FEED-PROD-004.yaml`: Lagerartikel-Link,
  Bewegungsbelege und Produktions-Lifecycle.

Reverse-Pflege: Wenn Rezepturstatus, Produktionsstatus, Bestandssnapshot,
Inventory-Link, QS-Freigabe oder Trace-Regeln geaendert werden, diese Seite und
die Futtermittel-/Produktions-Workflow-Dokumente gemeinsam aktualisieren.
