---
title: ADR-040 Contract-gated Herd-Data Connectors
type: decision
audience: [architekt, entwickler, security, fachlich]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-14
version: 1.0.0
---

# ADR-040 Contract-gated Herd-Data Connectors

**Status:** Proposed
**Datum:** 2026-07-14

## Kontext

Fütterungsberatung benötigt regelmäßig Gruppen-, Tiergesundheits- und
Abstammungsdaten aus unterschiedlichen Herdenmanagementsystemen. Anbieter wie
Dairy Data Warehouse beschreiben normalisierte Data Marts und Business-API-
Zugriff, veröffentlichen jedoch keine frei nutzbare OpenAPI-Spezifikation. Der
Datenzugriff setzt außerdem die ausdrückliche Freigabe des Betriebs sowie
vertragliche Access Rights voraus.

## Entscheidung

VALEO definiert einen providerneutralen, eingehenden Herd-Data-Vertrag mit den
Beobachtungstypen `group_kpi`, `health_alert` und `genetic_profile`.

- Anbieterpfade und Query-Parameternamen werden pro Verbindung konfiguriert;
  es gibt keine erfundenen produktiven DDW-Endpunkte.
- API-Schlüssel werden nicht in der Fachdatenbank gespeichert. Die Verbindung
  referenziert ausschließlich einen zugelassenen Environment-/Secret-Key.
- Live-Sync ist nur aktiv, wenn `enabled`, `live_enabled`, Vertragsreferenz,
  Einwilligungsreferenz, Secret und Egress-Allowlist vollständig sind.
- Rohantworten werden am Transport-Rand normalisiert. VALEO speichert
  zeitbezogene Beobachtungen mit Payload-Hash, Gruppenwechsel- und
  Löschkennzeichen sowie ein separates Delta-Sync-Journal.
- Ein täglicher Worker verarbeitet Verbindungen isoliert; ein fehlerhafter
  Betrieb blockiert keine anderen Mandanten.
- Anbieter-/AI-Werte sind Entscheidungshilfen und keine tierärztliche Diagnose.

## Konsequenzen

Der Connector kann nach Übergabe einer lizenzierten Anbieter-Spezifikation ohne
Codeänderung an Pfadnamen angepasst werden. Live-Betrieb bleibt bis zur realen
Vertrags-, Einwilligungs-, Secret- und Mapping-Freigabe blockiert. Neue Provider
können weitere Normalisierer ergänzen, ohne Rationssolver oder Portal an deren
proprietären Rohvertrag zu koppeln.

## Alternativen

- Unverifizierte `/v2/...`-Pfade fest einbauen: verworfen, da nicht offiziell
  dokumentiert und rechtlich/technisch nicht belastbar.
- Anbieterpayloads direkt in die Rationsmaske reichen: verworfen wegen fehlender
  Historie, Tenant-Isolation, Löschbehandlung und Anbieterentkopplung.
