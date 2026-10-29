---
title: Abschlusschecklisten - sichere Urheber und Validierung
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-25
---

# Abschlusschecklisten: Sicherheitsnachlauf

Alle betroffenen Routerwege beziehen den Mandanten aus dem verifizierten Kontext. Body-/Querymandanten ersetzen ihn nicht. PostgreSQL-JSONB-Listen werden ohne erneutes json.loads verarbeitet; fehlender datetime-Import korrigiert.

Manuelles Abschliessen und Freigeben schreiben ausschliesslich die gepruefte sub. Der historische completed_by-Eingabewert bleibt zur Clientkompatibilitaet akzeptiert, ist aber wirkungslos; approved_by ist kein API-Parameter mehr. Automatische Abschluesse protokollieren ebenfalls den ausloesenden geprueften Benutzer.

Gespeicherte validation_query ist niemals ausfuehrbarer Code. Vier serverseitig registrierte Pruefungen verwenden feste schemaqualifizierte Abfragen mit gebundenem Mandanten und Periode. GL-001 prueft Entwuerfe anhand posting_date statt der nicht vorhandenen Journalspalte period. TAX-001 verlangt mindestens eine passende Voranmeldung; zuvor wurde der vorhandene Nachweis wie ein Fehlerzaehler bewertet. AR/AP bewahren die bisherige offene-Posten-Pruefung, sind damit kein neuer Nachweis einer vollstaendigen Abstimmung. Unbekannte automatische Pruefungen bleiben ohne Erfolg; keine freie SQL-Erweiterung durch Templates. Savepoints verhindern, dass ein einzelner fehlgeschlagener Check die gesamte Datenbanktransaktion unbrauchbar macht. Fehlerantworten enthalten keinen SQL-Fehlertext.

Abnahme: 20 kombinierte Sicherheits-/Studio-API-Vertraege bestanden. Neue eigene Suite: fuenf Faelle, davon vier echte PostgreSQL-Faelle. Geprueft sind Urheberspoofing bei Abschluss/Freigabe, unbekannter gespeicherter SQL-Text mit statement_timeout, alle vier registrierten Abfragen, Fremdmandanten und Periodengrenzen. Eigene Zeilen und aeussere Rueckrolltransaktionen; bestehender valeo_probe, Revision loading_stop_fk_20261023. Keine neue DB, DDL oder Container.

Die breite Studio-/Inbox-Tranche und deren gemeinsame generierte Artefakte bleiben ein separater Integrationsschritt. Keine Browser- oder Gesamt-CI-Freigabe. PR42/43 wurden anhand ihrer exakten GitHub-Quellstaende gelesen; deren Integration ist mit dieser Checklistenlieferung nicht behauptet.
