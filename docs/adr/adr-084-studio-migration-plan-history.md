---
title: ADR-084 — Revisionsgebundene Studio-Migrationsplaene
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: proposed
last_reviewed: 2026-10-21
---

# ADR-084: Migrationsplan in bestehender Studio-Historie

## Status

Proposed. Technische Fortsetzung von STUDIO-MIGRATION-001 und STUDIO-CHANNEL-001;
keine neue Freigabepolitik oder automatische Schemaaktivierung.

## Kontext

Der stateless Migrationscompiler bindet Inhalte und Artefakte, jedoch keinen
bereits gespeicherten Entwurf. Eine lokale Plandatei ersetzt keinen dauerhaft
nachvollziehbaren Nachweis fuer eine konkrete Studio-Revision.

## Entscheidung

Ein zusaetzlicher Authoring-Command erzeugt den Plan ausschliesslich aus dem
serverseitig gespeicherten Kandidaten. Erwartete Revision und Wiederholungsschluessel
sind Pflicht. Tenant und Subject kommen aus bestehenden Auth-/Rechteabhaengigkeiten.
Schemaaenderungen bleiben typisierte additive Vorschlaege; freie Definition,
Plan-, Actor-, Tenant- oder Freigabenachweise werden nicht angenommen.

Der Command verwendet dieselbe transaktionale screen_definition_history und
bestehende Row-/Idempotenzsperren wie Studio-Aenderungen. Kein neues Register,
keine neue Tabelle, kein Container oder konkurrierender Geschaeftsdatenspeicher.
Das Audit enthaelt validierten Schemaauftrag, Kandidatenrevision/-hash,
Compilerplan und Bindungshash; PostgreSQL verhindert nachtraegliche Mutation.
Wiederholung liefert den historischen Plan, auch nach Katalogveraenderungen;
sie ist keine erneute Validierung. Andere Inhalte/Identitaeten unter demselben
Schluessel scheitern. Berechnungs-/Persistenzfehler hinterlassen keinen Teilplan.

Automatische Bindungsvorschlaege koennen von der gespeicherten Definition
abweichen. requires_definition_update kennzeichnet dies ausdruecklich; der
Command veraendert den Kandidaten nicht. Eine spaetere Bearbeitung braucht einen
neuen revisionsgebundenen Plan. Status und bestehende Vier-Augen-Freigabe bleiben
unveraendert; plan.can_activate bleibt false, Kanalnachweise not_verified.

## Konsequenzen

UI, CLI und MCP verwenden denselben Servercommand. Das versionierte MCP-Tool
studio.migration.plan ist ausschliesslich fuer diese R1-Authoring-Operation
freigeschaltet; belege:write im Transport ersetzt keine beleg_write-Rollenpruefung
am Ziel. Es leitet nur das Bearer-Token weiter, niemals Tenant- oder Actorwerte.
Validate/dryRun/propose pruefen nur die Auftragssyntax und behaupten keine
fachliche Freigabe. Keine DDL oder Publikation durch diesen Adapter.

Publikation verlangt zusaetzlich einen unveraenderten Plan exakt der geprueften
Revision. Compiler-/Katalogdrift, ungespeicherte Bindungsvorschlaege, andere
Fachblocker und Schemaaenderungen ohne Bereitstellungsnachweis sperren. Ein
Schema-Bereitstellungsnachweis ist noch nicht implementiert; entsprechende
Plaene koennen deshalb nicht publiziert werden. Runtime prueft den angebundenen
Plan erneut. Alte Plan-Replays bleiben historisch, nicht aktuell freigabefaehig.
Allgemeine CRUD-Generierung, Schemaeditor und vollstaendige Human/CLI/MCP-
Fachkettenzertifizierung bleiben offen. Die beiden allgemeinen Nachweisanmerkungen
im Compilerplan bleiben sichtbar, Kanalstatus bleibt not_verified. Die bestehende
grain.v1-Freigabe bleibt auf ihren geprueften read-only UI-Umfang beschraenkt;
sie ist keine universelle Geschaeftsprozessfreigabe.
C4-Grenzen bleiben unveraendert; interner Serviceprefix und API-Projektionen
werden nachgezogen. Keine DDL waehrend Planerstellung oder Testvorbereitung.
