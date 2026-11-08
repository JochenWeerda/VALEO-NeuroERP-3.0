---
title: Explizite endliche SLO-Messwerte fuer REST und MCP
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# Keine erfundenen SLO-Messwerte

Die beiden MCP-Werkzeuge finance_sla_check und process_slo_check verwenden nun Version 2 und denselben SloCheckIn-Vertrag wie POST /process/slo/check. slo_id und ist_wert sind ausdruecklich erforderlich. Ein endlicher numerischer Wert wird geprueft; ausdrueckliches null bedeutet UNBEKANNT. Fehlt der Wert, wird weder amount noch 0 eingesetzt, und eine feste SLO-ID wird nicht mehr erfunden. Zusatzfelder, Textwerte, Bool und NaN/Infinity werden abgewiesen.

Die Transportpruefung verwendet direkt das Modell und antwortet vor HTTP sanitisiert 422. REST prueft zusaetzlich nichtstandardkonforme JSON-Zahlen vor der Pydantic-Fehlerantwort: Eingabewerte wie NaN koennten sonst das Serialisieren der Validierungsfehlermeldung selbst mit 500 abbrechen lassen. Diese reine Eingabekontrolle erteilt keine Fachrechte. Der gemeinsame Schemavergleich bleibt exakt, keine Abschwaechung seiner Default-/Feld-/Referenzpruefung.

57 gezielte SLO-/DQ-/Migrations-/Schemafaelle bestanden. Neue Faelle belegen fehlende ID/Werte, endliche Zahlen, Null/0-Unterscheidung, beide MCP-Projektionen und rohe NaN/Infinity-HTTP-Eingaben mit 422. 99 bestehende SLO-/Broker-/Transport-/Manifestregressionen bestanden. Der Live-Abgleich der Produktions-OpenAPI bestaetigt elf Lesebindungen und vier kanonische Tool-Eingabeschemas. Isolierte Tests ersetzen die vorgelagerte JWT-Pruefung ausdruecklich; sie sind kein neuer Provider- oder Fachfreigabenachweis. Keine DB, Migration oder neuer Container.

OpenAPI wird nur fuer SLO-Eingabe/Beschreibung und die neue Komponente auf HEAD projiziert; fremde Arbeitskopien bleiben erhalten. Das Gate erfasst elf Lesebindungen und vier kanonische Tool-Eingabeschemas auf drei POST-Wegen (Migration, DQ, SLO zweimal). Andere POST-/Rechte-/CLI-Gleichwertigkeit sowie genehmigte Capability-Version, Studio-Historienanzeige, Prozesssimulation und Release-Sperre bleiben offen.

Der bestehende Broker bindet calculate_skonto_savings faelschlich an die SLO-Pruefung. Eine SLO-Auswertung ist keine Skontoberechnung; ohne ausdrueckliche SLO-Felder scheitert dieser Weg nun vor HTTP. Der richtige fachliche Ersatz bleibt offen und wurde nicht durch eine erfundene Berechnung ersetzt.
