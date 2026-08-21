---
title: ADR-057 MDE-Eingangskorb auf dem Mobile-Sync-Kern
type: adr
audience: [architektur, entwickler, product, qa]
owner: platform/integrations
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-057 MDE-Eingangskorb auf dem Mobile-Sync-Kern

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Die L3-Inventur zeigte einen operativen MDE-Eingang mit manueller
Verarbeitung. VALEO besass bereits den persistenten, mandantenbezogenen
`MOB-SYNC-001`-Kern fuer Inventurzaehlungen, Lieferbestaetigungen,
QS-Ergebnisse, Ernteannahmen und Siloumbuchungen. Es fehlten jedoch eine
Operator-Worklist, fachliche Vorvalidierung, ehrliche Duplikatantworten,
Quarantaene, auditiertes Retry und serverseitige Tabellenabfragen.

## Entscheidung

- MDE wird als Bedien- und Haertungsschicht des bestehenden Mobile-Sync-Kerns
  umgesetzt; es entsteht keine zweite Import-Queue.
- `domain_ops.mobile_event_queue` bleibt die kanonische Queue und erhaelt
  additiv Versuchszaehler, letzten Versuch und den Status `quarantined`.
- `mobile_event_queue_audit` protokolliert Annahme, Verarbeitung, Fehler,
  Quarantaene und begruendete Wiederholung append-only.
- Bekannte Eventtypen werden vor Persistenz gegen minimale Payloadvertraege
  validiert. `(tenant_id, device_id, idempotency_key)` bleibt der
  Idempotenzschluessel.
- Die Bedienoberflaeche ist die native ScreenDefinition
  `schnittstelle/mde-inbox`. Statusabhaengige Zeilenaktionen werden zentral im
  Fast-Table-Renderer deklariert und nicht als MDE-Sondertabelle gebaut.
- Fachliche Handler bleiben in ihren kanonischen Domaenen. Die Queue besitzt
  keine fremden Fachaggregate.

## Konsequenzen

Bestehende Mobile-Clients bleiben mit dem additiven Vertrag kompatibel und
erhalten bei Duplikaten die bestehende Event-ID. Ein fehlerhaftes Ereignis
wird nach drei fehlgeschlagenen Verarbeitungsversuchen quarantiniert. Externe
Geraeteformate und Provider-Mappings bleiben Adapter- und Pilot-Gates; sie
werden nicht in den kanonischen Queuevertrag eingebaut.
