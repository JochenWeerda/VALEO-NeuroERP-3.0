---
title: MCP Legacy-Neuro Ausfuehrungsgrenze
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: Token-, Mandanten-, Header- und Freischaltungsgrenzen des Legacy-Neuro-Transports.
---

# MCP-Ausfuehrungsgrenze — 2026-10-13

## Lieferung

Teil von Stufe 1 des [MCP-Schreibstandards](../architecture/mcp-write-standard.md).
NeuroToolExecutionService verwendet keinen Entwicklungs-, globalen Superglue- oder
Ersatz-Token mehr. Vor Transport werden Signatur, Aussteller, Zielgruppe, Ablauf,
Subject, Mandantenbindung und bestehende Sitzungskontrolle ueber verified_identity
geprueft. Zusaetzliche Header sind auf Korrelations-/Request-ID begrenzt; Identitaets-
und Mandantenheader koennen nicht ueberschrieben werden. Parameter und Policy-Kontext
mit fremden Mandantenselektoren werden abgelehnt.

Der REST-Einstieg /neuro/execute uebergibt den geprueften Bearer statt eines vom
Request-Rumpf gelieferten Transporttokens. Der Transporttoken wird getrennt vom Fachkontext uebergeben und gelangt weder
in Klassifizierung noch Planung/LLM-Kontext; Authorization wird im Request-Trace redigiert. Transportfehler geben keine
ungeprueften Exception-Texte aus.

Legacy-SCHREIBEN-/ESKALIEREN-Tools sind deaktiviert; Request-Flags oder selbst angegebene
Freigaben schalten sie nicht frei. Externe Ausfuehrung bleibt ohne abgenommenen
Ziel-/Credential-Vertrag gesperrt; ihr ungenutzter HTTP-Transport wurde entfernt.
Der Broker behandelt execution_rejected sowie HTTP 401/403 als Fehler, nicht als
angeblich ausgefuehrte oder lediglich degradierte Aktion.

## Nachweise

- 72 Faelle in vier betroffenen Testdateien bestanden (eine vorhandene TestClient-Deprecation-Warnung).
- Vier betroffene Testdateien: neuro_tool_execution, neuro_tool_broker,
  security_outbound_policy und neuro_pipeline.
- Echte synthetische RSA-Signaturen und produktive JWT-/Mandantenpruefungen;
  JWKS-Lieferung und Sitzungsspeicher sind fuer diese Vertragsfaelle isoliert.
  Kein Nachweis einer realen Keycloak-/Redis-Betriebsabnahme.
- Positive interne Ausfuehrung, Erhalt der Endpoint-Rollenentscheidung, fehlende und
  fruehere Entwicklungstokens, falsche Signatur/Audience/Issuer, Ablauf, fremde und
  verschachtelte Mandantenselektoren, Header-Overrides, deaktivierte Writes und externe
  Ziele, redigierte Credentials sowie Bindung des REST-Transporttokens.
- Vorherige Pipeline-Erwartungen an erfolgreiche Aufrufe ohne Anmeldung wurden durch
  ausdrueckliche 401-/Fehlervertraege ersetzt. Plan-/Dry-run- und Approval-Tests bleiben.
- Keine DB/Container erstellt, keine Migration und keine Geschaeftsdaten veraendert.

## Grenzen und Folgearbeit

Dies schliesst die Legacy-Neuro-Transportgrenze, nicht die systemweite Stufe 1.
Der separate MCP-ERP-Ausfuehrungsdienst, Command-/Capability-/Superglue-Brokerpfade,
versionierte Domain-Command-Bindungen, explizite Agentenrollen-Freischaltung,
transaktionaler Audit/Outbox-Vertrag und vollstaendige Idempotenz-/Versionsgarantien
muessen gesondert inventarisiert und abgenommen werden. Keine dauerhafte Freischaltung
per Request-Boolean oder Admin-Sonderfallback einfuehren.

Read/Calculate/Validate-Kategorien sind bestehende Metadaten; ihre vollstaendige
Seiteneffektfreiheit ist erst durch die kanonische Registry-/Command-Abnahme bewiesen.
Die vorhandene Endpoint-Autorisierung bleibt erforderlich. Eine abgewiesene Ausfuehrung
ist kein erfolgreicher Geschaeftsvorfall.

## Weitere Gates

Godfile-Ratsche gruen (15, exakte Baseline); diff --check fuer die eigenen Aenderungen
sauber. Der Handbuch-Driftcheck meldet vier geaenderte Artefakte im geteilten Baum
(index, Maskenkatalog, Automatisierung, Manifest). Diese liegen als fremde Aenderungen
vor und werden weder ueberschrieben noch in diesem Slice committet. Die eigenen
Quellpfade sind keine Regenerierungstrigger des Agent-Handbuchs. Das globale Drift-Gate
bleibt damit offen; kein Gesamt-CI-Gruen behauptet.
