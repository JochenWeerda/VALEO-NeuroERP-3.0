---
title: L3 Cutover UAT- und Pilotplan
type: test-plan
status: aktiv
owner: Fachbereiche und Cutover Lead
last_reviewed: 2026-08-23
---

# L3 Cutover UAT- und Pilotplan

## Ziel und Entscheidungsmodell

Der Plan weist nach, dass erfahrene L3-Anwender ihre Tagesarbeit in VALEO
NeuroERP vollständig, korrekt und nach kurzer Eingewöhnung ohne unvertretbaren
Zeitverlust ausführen können. Der maschinenlesbare Vertrag
[`config/l3-cutover-uat.yaml`](../../config/l3-cutover-uat.yaml) ist verbindlich.
Fehlende, veraltete oder nicht freigegebene Evidenz führt immer zu `NO_GO`.

Das Programm ergänzt die bestehenden Modul-Checklisten unter `docs/uat/` und
den [Production-Readiness-Runbook](../operations/production-readiness-runbook.md).
Es ersetzt weder fachliche Abnahme noch Sicherheits-, Backup- oder
Rollback-Gates.

## Teilnehmer und Verantwortungen

Je mindestens ein erfahrener Key User aus Verkauf, Einkauf, Lager/Logistik,
Finanzbuchhaltung und Agrar nimmt teil. IT/Betrieb stellt eine zusätzliche
Freigabe. Der Cutover Lead verwaltet Evidenz und Entscheidung, darf fachliche
Freigaben aber nicht selbst ersetzen. Für kritische Journeys unterschreiben
alle beteiligten Rollen.

Es sind ausschließlich anonymisierte oder freigegebene Testdaten zu verwenden.
Personenbezogene Daten, Zugangsdaten und Provider-Secrets gehören nie in die
Evidenzdatei; dort steht nur eine nachvollziehbare Artefakt-Referenz.

## Pflicht-Journeys

| ID | Ablauf | Rollen | Abnahme |
|---|---|---|---|
| `sales_to_cash` | Angebot → Auftrag → Lieferung → Rechnung → OP/Zahlung | Verkauf, Lager, Fibu | Belegkette vollständig, Werte korrekt, Protokoll und Freigabe |
| `procure_to_pay` | Bestellung → Wareneingang → Eingangsrechnung → Zahlung | Einkauf, Lager, Fibu | Mengen-/Wertfluss und Kontierung korrekt |
| `contract_to_settlement` | Kontrakt → Disposition → Ernteannahme → Abrechnung | Agrar, Lager, Fibu | Kontraktbezug, Qualität, Menge und Abrechnung korrekt |
| `inventory_lot_trace` | Bewegung → Charge → Rückverfolgung → Inventur | Lager, Agrar | Lückenlose Vor-/Rückverfolgung und Soll/Ist-Abgleich |
| `production_transfer_postprocessing` | Produktion → Umlagerung → Nachbearbeitung | Lager, Agrar | Buchungsfolge und Bestandswirkung korrekt |
| `document_return_control` | Dokumentenversand → Rücklauf → Kontrolle/Ablage | Verkauf, Einkauf, Fibu | Status, Archivbezug und Wiederauffindbarkeit korrekt |

Jede Journey wird in beiden Migrationsproben und während des Parallelbetriebs
ausgeführt. Erfasst werden Start/Ende, Ergebnis, verwendete Belegreferenzen,
Fehler, Hilfestellungen und Dauer im Vergleich zur vertrauten L3-Ausführung.

## Gewohnheitsbrücke

Vor dem ersten Pilotdurchlauf erhalten Anwender fünf freizugebende Hilfen:

1. L3-zu-VALEO-Begriffsmatrix einschließlich alter Masken- und Feldnamen.
2. Rollenbezogene Startseiten und Favoriten für die häufigsten Masken.
3. Tastatur-, Suche-, Speichern-, Zurück- und Tabellenbedienung als Kurzblatt.
4. Eine einseitige Kurzanleitung pro Pflicht-Journey mit L3-Einstiegspunkt und
   VALEO-Zielpfad.
5. Betreute Übung mit mindestens einem vollständigen Belegfluss pro Rolle.

Abweichungen an Masken werden nicht lokal übersteuert. Sie werden als
ScreenDefinition-/RenderPlan-Gap aufgenommen und zentral über
UniversalMaskRuntime/UniversalMaskRenderer geschlossen.

## Defect-Triage

| Severity | Bedeutung | Cutover-Regel |
|---|---|---|
| P0 | Datenverlust, falsche Buchung, Sicherheits- oder Betriebsstillstand | 0 offen |
| P1 | Kernprozess nicht abschließbar oder Reconciliation falsch | 0 offen |
| P2 | Umgehbarer Funktions-/Bedienmangel | höchstens 5 offen, Owner und Termin Pflicht |
| P3 | Kosmetik oder Optimierung | dokumentiert, kein automatischer Blocker |

Ein erneuter Test ist nach jeder Korrektur Pflicht. Ein Ticket gilt erst als
geschlossen, wenn reproduzierbarer Nachweis, Regressionstest und Key-User-
Bestätigung vorliegen.

## Messwerte und Abnahme

- Alle kritischen Journeys müssen bestanden sein; Gesamtquote mindestens 95 %.
- Median der Aufgabendauer nach Eingewöhnung höchstens 120 % des L3-Werts.
- Anwenderfehlerquote höchstens 2 %.
- Zwei voneinander getrennte Migrationsproben müssen bestanden sein.
- Record-Count- und Betragsabweichung sind null; Mengenabweichung höchstens
  0,001; kritische verwaiste Referenzen sind null.
- Waage, MDE, Tank, DMS/Mail, L3-Standard, Unimet und Druck benötigen jeweils
  einen aktuellen, freigegebenen Realtest-Nachweis.
- Parallelbetrieb umfasst mindestens zehn Geschäftstage.

## Evidenzformat

Eine leere, absichtlich blockierende Vorlage wird erzeugt mit:

```powershell
python scripts/l3_cutover_readiness.py `
  --write-evidence-template artifacts/l3-cutover/evidence.json `
  --output-json artifacts/l3-cutover/readiness.json `
  --output-markdown artifacts/l3-cutover/readiness.md
```

Jede Freigabe enthält `status`, `approver`, ISO-8601-`timestamp` und
`artifact`. Nachweise älter als 90 Tage werden nicht akzeptiert. Der finale
Check lautet:

```powershell
python scripts/l3_cutover_readiness.py `
  --evidence artifacts/l3-cutover/evidence.json `
  --output-json artifacts/l3-cutover/readiness.json `
  --output-markdown artifacts/l3-cutover/readiness.md `
  --fail-on-no-go
```
