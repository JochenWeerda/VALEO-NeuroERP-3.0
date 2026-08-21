---
title: ADR-058 Dokumentenruecklauf auf dem kanonischen Docflow
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/dms-compliance
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-058 Dokumentenruecklauf auf dem kanonischen Docflow

## Kontext

VALEO besitzt Docflow-Headers, versionierte Artefakte und Wiedervorlagen, aber
bislang keinen gemeinsamen Arbeitsvorrat fuer versendete und erwartete
Dokumente. L3-Anwender benoetigen diese Sicht nach Benutzer, Kontakt, Datum und
fachlichem Bezug.

## Entscheidung

- Ruecklauffaelle referenzieren kanonische `document_headers` und optional ein
  mandanten- und beleggleiches `document_artifact`.
- Versand- und Ruecklaufstatus besitzen getrennte, geschlossene
  Statusmaschinen. Jeder Wechsel verlangt einen Grund und erzeugt einen
  append-only Auditdatensatz.
- Bezug, Kontakt, verantwortlicher Benutzer, Schlagworte, Faelligkeit und
  Ursprungsroute werden am Ruecklauffall als stabiler Worklist-Vertrag gefuehrt.
- `docflow/dokumenten-ruecklauf` ist eine native, serverseitig paginierte
  Meridian-Worklist. Zeilenaktionen bleiben zentral im Fast-Table-Renderer.
- Provider-Zustellnachweise werden spaeter als Adapterereignisse auf denselben
  Statusvertrag abgebildet und erzeugen keine zweite Ruecklaufqueue.

## Konsequenzen

`L3-GAP-DOCRET-002` ist repo-seitig geschlossen. Reale Mail-/Briefprovider und
fachliche Pilotabnahme bleiben externe Gates; Storage-Auslieferung bleibt beim
kanonischen DMS/Paperless-Adapter.
