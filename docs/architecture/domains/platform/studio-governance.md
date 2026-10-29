---
title: Studio-Governance und Revisionshistorie
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# Studio-Governance — Impact Note

Die bestehende Studio-API und der bestehende Draft-Speicher im Backend bleiben fuehrend. Die additive Tabelle domain_shared.screen_definition_history haelt jeden neuen Inhalts-/Statusstand in derselben Transaktion fest. Kein Container, Dienst oder konkurrierendes Vorschlagsregister entsteht; C4-Grenzen bleiben unveraendert.

Freigabe setzt verifizierte menschliche Adminidentitaet, getrennten Editor, eingereichten Reviewstatus, Inhaltskatalog und erwartete Revision voraus. AI-Proposer koennen durch Metadaten keine Sicherheitsregeln oder produktiven Code aendern. MCP-Schreibadapter bleiben gemaess MCP-WRITE-014 deaktiviert, solange Capability-/Rollenabnahme fehlt.

Die Historie bewahrt Snapshot und Subject ohne erfundene lokale Benutzer-/E-Mail-Zuordnung. PostgreSQL blockiert nachtraegliche Zeilenmutation sowie TRUNCATE. Keine Kaskade entfernt Historie mit dem Draft. Historienabfragen sind paginiert und mandantengebunden. Bestehende Stande vor der Migration werden nicht nachtraeglich zu einer Freigabehistorie umgedeutet.

Migration und Nachweise: [Studio-Revisionshistorie](../../../quality-assurance/studio-revision-history-20261014.md). Idempotenz, Agenten-/Korrelationsattribute, maskenseitige Historie und fachliche Prozessvariantensimulation sind nachfolgende Integrationen. Die vollstaendige Engine-Abnahme ist dadurch noch nicht erreicht.

## Fachsprachliche Weiterentwicklung 2026-10-15

[STUDIO-SEMANTIC-001](../../studio-semantic-standard.md) ist der verbindliche Entwicklungsauftrag fuer den mehrstufigen Dialog und die kataloggebundene Maskenerstellung. Bestehende Meridian-Engine, Rechte und revisionsgebundene Freigabe bleiben fuehrend. Der Dialog und die komplexe Referenzmaske sind gesondert nachzuweisen; vier Vorlagen ersetzen diesen Nachweis nicht.


## STUDIO-MIGRATION-001 und STUDIO-CHANNEL-001 (20.10.2026)

Funktionsmigration, automatische kataloggebundene Verdrahtung und erforderliche
Schema-/Tabellengenerierung gehoeren zum vorhandenen Studio, nicht zu einem
separaten Maskenwerkzeug. Neuer erster Baustein: authentifizierter Planweg
`POST /api/v1/studio/migration-plan` und `studio migrationsentwurf` in der CLI.
Fehlende Bindungen werden ausschliesslich aus dem kuratierten Katalog ergaenzt.
Vorhandene widerspruechliche Werte werden weder still bereinigt noch genehmigt.

Additive Tabellen-/Spaltenvorschlaege erzeugen echte versionierte Alembic-Quellen,
keine direkt ausfuehrbaren SQL-Eingabefelder. Tabellen erhalten Mandanten-FK,
mandantenbezogenen Schluessel sowie Version und Urheber/Zeitpunkt. Erweiterungen
bestehender Tabellen sind vorerst nur nullable und auf mandantengebundene Tabellen
begrenzt; Pflichtfelder erfordern eine eigene gepruefte Backfillmigration.
Identitaets-/Auditspalten koennen nicht frei ueberschrieben werden. Der Plan bindet
Definition, Katalog, physisches Schemainventar, Alembic-Head, Mandant und Urheber
inhaltlich; er ist noch kein gespeicherter Freigabenachweis. C4 bleibt unveraendert.

**STUDIO-CHANNEL-001:** Jede neue Maske muss ueber Human-UI, CLI und MCP bedienbar
sein. Identische Fachaktionen benutzen dieselben Domain-Commands, Rollen- und
Datensatzrechte, verifizierte Mandantenbindung, Transaktions-/Auditgarantien und
Idempotenzregeln. Abnahme umfasst positive und negative Faelle je Zugang,
Fremdmandant/Objekt, Rollenentzug sowie Wiederholungen. MCP-WRITE-001 bis015 gilt
unveraendert. Kritische Agentenaktionen benoetigen die aktionsgebundene Genehmigung;
eine menschenvorbehaltene Aktion darf nicht durch einen Adapter freigeschaltet werden.

Der neue Plan weist alle drei Zugaenge zunaechst als `not_verified` aus und nennt
die verpflichtenden Vertraege als Blocker. Weder Planerzeugung noch syntaktisch
korrekte Alembic-Quelle ersetzen diese Abnahme. Studio-Schreibfreigabe,
Schemaaktivierung, vollstaendige CRUD-/Capability-Generierung und neuer UI-Editor
sind damit noch nicht umgesetzt. Vor jeder Aktivierung sind diese Nachweise an
die unveraenderliche Fassung zu binden; der bestehende Releaseweg bleibt gesperrt,
wenn seine Simulation/Validierung fehlt. Keine Behauptung einer bereits
systemweit erweiterten Dreikanal-Freigabepruefung.


## Gespeicherter Migrationsplan (21.10.2026)

POST /api/v1/studio/drafts/{draft_id}/migration-plan nimmt ausschliesslich
expected_revision, idempotency_key und optionale schema_changes entgegen.
Derselbe beleg_write-/verifizierte Mandantenkontext wie bestehende Authoring-
Commands gilt. Die Definition wird unter Draftsperre serverseitig gelesen.
Antwort StudioSavedMigrationOut bindet Planhash, Kandidatenrevision/-hash,
Urheber, Mandant und validierten Schemaauftrag. Speicherung als migration_plan
in der bestehenden unveraenderbaren Studio-Historie, keine neue Tabelle.
CLI: studio plan-speichern ENTWURF --revision REVISION [--schema DATEI]
[--idempotenz UUID] [--ausgabe DATEI]. Wiederholung gibt den urspruenglichen
Historienstand zurueck; sie ist keine neue Abnahme gegen heutige Kataloge.
requires_definition_update kennzeichnet noch ungespeicherte Bindungsvorschlaege.
Keine Statusaenderung, DDL oder Publikation; Erweiterung des vollstaendigen
Dreikanal-Freigabegates bleibt offen. ADR084 Proposed und QA
studio-plan-history-20261021.md dokumentieren Nachweis und Grenzen.
