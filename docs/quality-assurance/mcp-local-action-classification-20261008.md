---
title: MCP Maskenaktionen mit belegter lokaler Wirkung 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Codex-01a0f3fc
status: abgeschlossen
last_reviewed: 2026-10-08
---

# Lokale Bedienaktionen und fehlende Fachcommands

Der bisherige reguläre Ausdruck klassifizierte auch neu als Mutation.
Die explizite blocked-Liste behandelte dadurch zehn belegte lokale
Bedienaktionen als fehlende HTTP-Fachcommands. Die Generator-Klassifikation
kennt jetzt local_ui mit local_effect. Alle59 Aktionen bleiben im Inventar;
zehn lokale Bedienaktionen werden getrennt von den49 bisherigen
Mutationskandidaten gezaehlt. Es wurde kein Fachcommand implementiert oder
als erfolgreich ausgefuehrt dargestellt.

## Nachgewiesene lokale Aktionen

Acht neu-Aktionen rufen ausschliesslich leeren() auf und kehren zurueck:
Personal Bewerbungen, Einwilligungserklaerungen, Onboarding, Qualifikationen,
Schulungen; Fuhrpark ausgehende Dokumente, Rechnungen und Terminarten.
Die jeweiligen Speichern-/Anlegen-Aktionen bleiben blocked_no_endpoint.

Fuhrpark Fahrzeuge oeffnet /fuhrpark/fahrzeug/neu; Transporte Fahrer oeffnet
/transporte/fahrer/neu. Das Oeffnen der Erfassungsmaske legt kein Objekt an.
Die Registry bekommt kein erfundenes MCP-Tool oder HTTP-Mutationsendpoint.
Die zehn konkreten Handlerbelege werden im Inventur-Vertragstest geprueft;
kein pauschales neu-Muster. Unbekannte neue Maskenaktionen bleiben offen.

Ein neu eingetragener commandEndpoint an einer kuratierten lokalen Aktion
bricht den Generator mit Klassifikationskonflikt ab und fordert Review;
kein stilles Ausblenden einer kuenftigen echten Mutation.

## Restbestand

Es bleiben21 blocked_no_endpoint: Postfach neu/speichern (fremder aktiver
Mail-Slice, hier unberuehrt), Abfrage-Import, Bonusberechnung, Kunden- und
Personalsanktionspruefung, Bestellungs-Speichern, Lieferant neue Bestellung,
Fahrzeug-Speichern/Loeschen, Dokument-/Rechnungs-/Terminart-Speichern,
Frachttabelle/Tour anlegen, Verladung neu und fuenf Personal-Speicheraktionen.
Diese21 werden nicht als erledigt bezeichnet; weitere lokale Kandidaten
brauchen erst belegte Pruefung, echte Fachaktionen benoetigen kanonische
HTTP-Commandvertraege samt Eingabe-, Mandanten- und Transaktionsschutz.

Zahlauf bleibt open_high unter forbiddenForAgents, FIN-CLOSE bleibt
blocked_adr_076. 23 mapped, eine mapped_propose_only, zwei mapped_read und
eine adjacent unveraendert; 39 MCP-Tools unveraendert. Keine API-,
ScreenDefinition-, Frontend-, Service- oder Schemaaenderung.

## Abnahme und Handshake

Original-Gegenprobe22 Vertraege: elf Fehlklassifikationen rot, elf konkrete
Handler-/Unbekannt-Vertraege gruen. Zusaetzlicher neuer HTTP-Bindungs-Driftvertrag.
Finaler isolierter Lieferstand: 160 neue und bestehende Vertraege ohne Skip in12,78 Sekunden gruen; Generator --check gruen..
Generator --check prueft die gesamte Map, einschliesslich dynamischem
Restzaehler; bestehende MCP-Ausfuehrungs- und Registry-Vertraege unveraendert.
Keine DB/Container/Migration/Reset oder neue Fachschreibtests.
Lokale Evidenz: artifacts/ci-mcp-local-original.log und
artifacts/ci-mcp-local-final.log. GitHub-Folgeabnahme nach Push offen.

Kanonisch fuer diesen Stand sind die generierte config/mcp_mask_action_map.yaml
und diese Abnahme. Aeltere Handshakes mit31 blocked dokumentieren den
historischen Befund. Es wurden zehn Fehlklassifikationen korrigiert,
keine zehn fehlenden Fachcommands geliefert.
