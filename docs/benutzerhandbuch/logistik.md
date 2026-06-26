---
title: Logistik und Touren
type: how-to
audience: [endnutzer, power-user]
owner: Codex
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Logistik und Touren

Diese Anleitung beschreibt die Arbeit von Disposition, Lager und Fahrer:
Tour planen, Frachtbrief erstellen, Lieferung verfolgen und ePOD abschliessen.

## Voraussetzungen

- Lieferschein oder Versandauftrag ist vorhanden.
- Fahrzeug, Fahrer und geplante Stopps sind bekannt.
- Gewichte, Zeitfenster und Empfaengeradresse sind gepflegt.
- Fuer ePOD muss der Fahrer den Ablieferungsnachweis erfassen koennen.

## Tour planen

1. Oeffnen Sie *Logistik* -> *Tour & Fracht (Dispo)*.
2. Pruefen Sie offene Lieferungen, Fahrzeugkapazitaet und Zeitfenster.
3. Legen Sie eine Tour an oder oeffnen Sie eine bestehende Tour.
4. Ordnen Sie Stopps zu.
5. Fuehren Sie die Dispositionspruefung aus.
6. Klaeren Sie Ueberladung, fehlende Adressen oder Zeitfensterkonflikte.

## Frachtbrief erstellen

1. Oeffnen Sie *Logistik* -> *Frachtbriefe*.
2. Waehlen Sie Tour, Lieferschein oder Empfaenger.
3. Pruefen Sie Absender, Empfaenger, Ware, Gewicht, Gefahr-/QS-Hinweise und
   Frachthinweise.
4. Speichern Sie den Frachtbrief.
5. Drucken oder exportieren Sie den Beleg fuer Fahrer und Empfaenger.

## Lieferung verfolgen und ePOD abschliessen

1. Oeffnen Sie die Tour.
2. Pruefen Sie Tourereignisse und GPS-Track, falls verfuegbar.
3. Setzen Sie den Stoppstatus nach Rueckmeldung des Fahrers.
4. Erfassen Sie den ePOD: Empfaengername, Signaturhinweis, Zeit und optional
   Foto-/Dokumentreferenz.
5. Schliessen Sie den Stopp per ePOD-Settlement ab.
6. Pruefen Sie, ob die Tour abrechnungs- oder fakturabereit ist.

## Ergebnis

- Tour, Frachtbrief, Stopps und ePOD bilden eine nachvollziehbare Lieferkette.
- Ueberladung und Zeitfensterkonflikte werden vor Abfahrt sichtbar.
- Abgeschlossene Stopps haben einen Ablieferungsnachweis.

## Haeufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Tour kann nicht freigegeben werden | Kapazitaet oder Zeitfenster verletzt | Dispositionspruefung lesen und Stopps anpassen |
| Frachtbrief laesst sich nicht speichern | Lieferschein-, Gewichts- oder Empfaengerdaten fehlen | Stammdaten und Belegbezug vervollstaendigen |
| ePOD-Settlement blockiert | Stopp ist noch nicht als geliefert/signiert markiert | Status und ePOD-Daten nachtragen |
| Abrechnung fehlt | Tour nicht abgeschlossen oder bereits fakturiert | Tourstatus und Invoice-Status pruefen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: Logistik-Menue
  mit Tour & Fracht, Tourenplanung und Frachtbriefen.
- `docs/agent-ops/slices/LOG-FRACHTBRIEF-001.yaml`: Frachtbrief-Endpoint
  `GET/POST/PATCH /api/v1/logistik/frachtbriefe`.
- `docs/agent-ops/slices/LOG-TRACK-001.yaml`: Tourereignisse, GPS-Track,
  ePOD und ePOD-Settlement.
- `docs/agent-ops/slices/DOM-LOG-004.yaml`: fachliche Vertiefung
  Tour-Disposition, ePOD-Lifecycle und Frachtabrechnung.
- `docs/workflows/wave-physical-chain-logistics-audit-2026-06-12.md`: Audit der
  Kette Waage -> Lager -> Lieferschein -> Tour/Fracht -> Abrechnung.

Reverse-Pflege: Wenn Tourstatus, ePOD-Felder, Frachtbriefpflichtfelder,
Disposition-Checks oder Abrechnungsregeln geaendert werden, diese Seite und die
Logistik-Workflow-Dokumente gemeinsam aktualisieren.
