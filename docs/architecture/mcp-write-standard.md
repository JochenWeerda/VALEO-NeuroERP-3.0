---
title: Kontrollierte schreibende Agentenaktionen
type: reference
audience: [agent, entwickler, architect, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: Verbindlicher Architekturstandard MCP-WRITE-001 bis 015 und Integrationsreihenfolge.
---

# MCP-WRITE — Kontrollierte schreibende Agentenaktionen

**Verbindlich seit 2026-10-13, vom Auftraggeber festgelegt.** Dieser Standard konkretisiert
[ADR-004](../adr/adr-004-command-action-layer.md),
[ADR-007](../adr/adr-007-agent-tool-contract-governance.md),
[ADR-014](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md) und
[ADR-019](../adr/adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md).
Er gilt auch waehrend der Entwicklung. Seine Verabschiedung ist kein Nachweis, dass
bestehende Adapter bereits alle Anforderungen erfuellen.

## Verbindliche Regeln

**MCP-WRITE-001 — Kontrollierte schreibende Agentenaktionen.** Schreibende MCP-Adapter
duerfen Geschaeftsdaten ausschliesslich ueber registrierte, versionierte Domain-Commands
veraendern. Sie duerfen weder direkt auf Datenbanktabellen schreiben noch fachliche
Validierungen, Mandantenisolation, Berechtigungen, Freigabeprozesse oder revisionssichere
Buchungsregeln umgehen. Jede schreibende Aktion muss authentifiziert, autorisiert,
validiert, idempotent und vollstaendig nachvollziehbar sein. Rechnungsfreigabe, Buchung,
Stornierung, Zahlung und Bestandskorrektur erfordern eine gesonderte, aktionsgebundene
Berechtigung beziehungsweise Genehmigung gemaess Freigaberichtlinie. MCP ist ausschliesslich
Transport- und Interaktionsadapter, keine eigenstaendige Geschaeftslogik.

| Regel-ID | Verpflichtung |
|---|---|
| MCP-WRITE-002 | Schreibzugriffe nur ueber die zentrale Capability Registry und registrierte, versionierte Domain-Commands. |
| MCP-WRITE-003 | Mandantenkontext ausschliesslich aus vertrauenswuerdiger Authentifizierung und autorisierter Auswahl; Eingaben und Header gewaehren keine Mandantenrechte. |
| MCP-WRITE-004 | RBAC/ABAC und Datensatzberechtigungen vor jeder Aktion und jeder Wiederholung pruefen. |
| MCP-WRITE-005 | Eingaben serverseitig anhand versionierter Schemas und Fachregeln validieren. |
| MCP-WRITE-006 | Idempotency Key fuer jede geschaeftsveraendernde Aktion; Wiederholungen erzeugen keine Doppelwirkung. |
| MCP-WRITE-007 | Optimistische Nebenlaeufigkeitskontrolle durch expected_version oder einen vergleichbaren Mechanismus bei bestehenden Aggregaten. |
| MCP-WRITE-008 | Freigaben an konkreten Beleg, Aktion, unveraenderten Aenderungsumfang und begrenzte Gueltigkeit binden. |
| MCP-WRITE-009 | Audit-Trail mit Benutzer-, Agenten-, Mandanten-, Aktions- und Korrelationsidentitaet sowie Ergebnis. |
| MCP-WRITE-010 | Keine teilweisen, inkonsistenten Geschaeftsvorfaelle bei Fehlern; transaktionale Verarbeitung und Outbox verwenden. |
| MCP-WRITE-011 | Festgeschriebene Belege und Buchungen ausschliesslich ueber zulaessige Korrektur- und Stornoprozesse aendern. |
| MCP-WRITE-012 | Jeder Schreib-Command erhaelt Mandantenisolations-, Berechtigungs-, Wiederholungs- und Negativtests in CI. |
| MCP-WRITE-013 | Minimale Agentenrechte; Tool-Sichtbarkeit allein gewaehrt keinerlei Schreibrecht. |
| MCP-WRITE-014 | Schreibende MCP-Funktionen sind zunaechst deaktiviert; ausdrueckliche Freischaltung pro Capability und Agentenrolle erst nach Abnahme. |
| MCP-WRITE-015 | Identische Fachaktionen ueber MCP, REST, CLI und UI verwenden dieselben Domain-Commands, Validierungsregeln, Autorisierungsentscheidungen und Transaktionsgarantien. Kein Adapter darf fachlich unzulaessige Ergebnisse herbeifuehren. |

## Ausfuehrungs- und Freigabestufen

| Klasse | Beispiel | Regel |
|---|---|---|
| R0 – Lesen | Rechnung abrufen | Automatisch nach Authentifizierung, Autorisierung und Mandanten-/Datensatzpruefung. |
| R1 – Entwurf | Auftrag oder Rechnung als Entwurf anlegen | Automatisch bei Berechtigung und ausdruecklich freigeschalteter Capability. |
| R2 – Operative Aenderung | Mengen oder Stammdaten aendern | Automatisch innerhalb serverseitig definierter Grenzen. |
| R3 – Geschaeftlich verbindlich | Rechnung ausstellen, Bestellung ausloesen | Explizite Freigabe oder vorab genehmigte, passende Richtlinie. |
| R4 – Kritisch | Zahlung, Storno festgeschriebener Buchung | Gesonderte starke Autorisierung und gegebenenfalls Vier-Augen-Freigabe gemaess Richtlinie. |

R0–R4 sind VALEO-interne Architekturregeln, keine MCP-Risikoklassen. Es gibt keine pauschale
manuelle Freigabe fuer jede Schreibaktion. Die Klassifizierung folgt der tatsaechlichen
Wirkung: Rechnungsentwurf R1, Ausstellung R3, Zahlung R4. Agenten duerfen ihre eigene
Freigabe weder erzeugen noch durch eine Selbstauskunft ersetzen.

## Verbindliche Integrationsreihenfolge

Die vier Stufen werden in dieser Reihenfolge abgenommen; spaetere Adapter duerfen
vorherige Sicherheitsgates nicht umgehen.

1. **Ausfuehrung absichern.** Vertrauenswuerdige Benutzer-/Agentenidentitaet,
   autorisierter Mandant, zielgebundene Tokens und Rechtepruefung durchsetzen.
   Globale Entwicklungs-/Ersatz-Token-Fallbacks entfernen; zusaetzliche Ausfuehrungsheader
   duerfen Authorization oder Mandant nicht ueberschreiben. Unabgenommene Writes sperren.
   Gate: fehlende/ungueltige Identitaet, fremder Mandant, unzureichende Rechte und nicht
   freigeschaltete Agentenrolle werden vor jeder Geschaeftsaenderung abgewiesen.
2. **Bestehende Register vereinheitlichen.** Command-/Action-Register, MCP-Katalog und
   Screen-Aktionskatalog auf kanonische Capability- und versionierte Command-Identitaeten
   abbilden. Keine unabhaengige zweite DocumentCapability-Wahrheit einfuehren.
   Gate: jede Schreib-Capability hat genau einen verantwortlichen Domain-Command,
   versioniertes Schema, Rechte, Risikoklasse, Freigaberichtlinie und Freischaltzustand;
   fehlende oder widerspruechliche Zuordnungen blockieren die Freischaltung.
3. **Kanalvertraege pruefen.** Mandant/Rechte, geaenderte Wiederholungen, Parallelzugriff,
   Versionskonflikte, Freigabebindung, Rollback, Audit und Outbox gemeinsam pruefen.
   Gate: MCP, REST, CLI und UI erzielen fuer denselben Fachvorgang dieselbe zulaessige
   Wirkung und dieselben fachlichen Ablehnungen. Tests verwenden den gemeinsamen
   Pruefstand mit eigenen Transaktionen/Datensaetzen; keine neuen Testdatenbanken.
4. **Masken und MCP ableiten.** Versionierte Ein-/Ausgabeschemas, Aktionsbeschreibungen
   und Adapter-Mappings aus den kanonischen Vertraegen erzeugen. Masken ueber die zentrale
   ScreenDefinition/RenderPlan/UniversalMaskRuntime-Kette integrieren.
   Gate: Drift-Pruefung, echte Browserabnahme und MCP-Transport-/Protokollabnahme;
   anschliessend gezielte Freischaltung je Capability und Agentenrolle.

## Ausfuehrungsvertrag und Capability-Beispiel

Das folgende YAML ist ein **internes Vertragsbeispiel**, keine neue bereits implementierte
Registry und keine MCP-Standarddefinition. Es wird auf vorhandene Register abgebildet.

```yaml
apiVersion: valeo.erp/v1
kind: DocumentCapability
name: sales.invoice.create
domain: sales
access: write
enabled: false
authorization:
  scope: sales.invoice.create
  tenantIsolation: required
  actorIdentity: required
  agentIdentity: required
execution:
  command: sales.invoice.create
  commandVersion: v1
  schema: sales.invoice.create.v1
  idempotencyKey: required
  expectedVersion: optional
  transaction: required
  outbox: enabled
policy:
  riskLevel: R1
  approval: policy_based
  defaultEffect: deny
audit:
  enabled: true
  correlationId: required
  persistOutcome: true
```

- expectedVersion darf bei erstmaliger Erstellung fehlen. Aenderungen bestehender
  Belege brauchen einen verpflichtenden Versions-/vergleichbaren Konfliktmechanismus;
  Erstellungen aus bestehenden Quellen pruefen auch deren konsistenten Zustand.
- Idempotenz wird dauerhaft und nebenlaeufigkeitssicher gespeichert, an Mandant,
  Command-Version und Eingabe-Fingerprint gebunden. Gleicher Schluessel mit geaendertem
  Inhalt wird abgewiesen; Ergebnisabruf bleibt autorisiert.
- Freigaben sind serverseitig an Belegversion, Aktion und Aenderungs-Fingerprint gebunden.
  Inhaltliche Aenderungen oder Ablauf machen die Freigabe ungueltig; Wiederholungen
  duerfen keine weitere Wirkung ausloesen.
- Geschaeftsaenderung, verbindlicher Erfolgsnachweis und Outbox-Eintrag gehoeren in
  dieselbe Transaktion. Abgewiesene/fehlgeschlagene Versuche werden datensparsam separat
  protokolliert, ohne fehlgeschlagene Geschaeftsaenderungen zu committen.
- Outbox-Verbraucher verarbeiten Wiederholungen idempotent; externe Effekte erhalten
  definierte Wiederanlauf-/Kompensationsregeln. Keine unbewiesene Exactly-once-Zusage.
- Technische Agentenidentitaet und delegierender Benutzer stammen aus geprueften
  Identitaets-/Delegationsdaten, niemals ungeprueft aus dem Request-Rumpf.

## Lieferstand und offene Migration

Festgelegt ist dieser Architekturstandard. Eine systemweite Laufzeitdurchsetzung ist
**noch nicht abgenommen**. Bereits vorhandene MCP-Writes erhalten keinen Bestandsschutz:
Freischaltung erfordert dieselben Nachweise; fehlende Nachweise bedeuten deaktiviert.
Konkrete Migrationen werden als eigene Slices geclaimt und mit Tests geliefert.

Bekannte Pruefpunkte: Token-/Header-Fallbacks in app/services/neuro_tool_execution.py;
fachliche SQL-Schreibpfade in app/services/mcp_execution_service.py;
parallele Register und Adapter-Mappings. Diese Liste behauptet keine vollstaendige Inventur.
Operative Nachweise gehoeren ins [Workboard](../agent-ops/active-workboard.md) und den
[Process-Kernel-Status](process-kernel/STATUS.md), offene Luecken bleiben im
[Gap-Verzeichnis](../project-context/open-gaps-and-known-issues.md) sichtbar.

## Protokollreferenzen

- [MCP Authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization): Zielbindung und Validierung von Access Tokens.
- [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools): Tool-Schemas und Metadaten ersetzen keine serverseitige ERP-Freigabepolitik.
