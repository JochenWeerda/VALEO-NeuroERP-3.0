---
title: Maskenaktion Ausfuehrungsgrenzen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: Deklarierte Aktionsrechte und nicht mutierende DocFlow-Vorschauen im gemeinsamen Runtime.
---

# Maskenaktion: Ausfuehrungsgrenzen

## Befund und Lieferung

Vor der Aktivierung der Belegvarianten wurden zwei bestehende Vertragsluecken erkannt.
checkActionPolicy pruefte bisher nur Agentensperren, nicht das deklarierte Aktionsrecht.
Die Aktionspolicy uebernimmt jetzt action.permission; fehlt es in den aufgeloesten
Berechtigungen, wird der direkte Aufruf fuer Menschen und Agenten vor HTTP abgewiesen.
Das genaue Recht bleibt erforderlich; belege:write ersetzt belege.buchen nicht.
Backend-Autorisierung bleibt verpflichtend und autoritativ.

Die generische Runtime sendet _mode/_idempotencyKey/_auditReason; DocFlow verlangt
Domain-Command-Felder (idempotency_key/expected_version usw.) und antwortet nicht
mit dem generischen ActionResult. Nicht jede DocFlow-Aktion unterstuetzt eine
Vorschau. Fuer direkte /api/v1/docflow-Endpunkte sind dryRun/validate/propose deshalb
im gemeinsamen Adapter vor HTTP gesperrt, bis ein versionierter Command-Adapter
mit ausdruecklichem Vorschauvertrag existiert. Ein Preview darf keine Mutation
verursachen. Die vorhandene Human-Form-Sperre und Agentensperren bleiben erhalten.

## Nachweise

28 Vitest-Faelle in drei Dateien bestanden: ActionRuntime, Human-InputFlow und
ScreenPermissions. Neue Faelle pruefen fehlende Rechte beider Caller-Arten, das
exakte Recht gegen einen groben Transport-Scope, keinen HTTP-Aufruf bei DocFlow-
dryRun/validate/propose trotz gueltiger Schreibberechtigung und Idempotenzpayload,
sowie keinen execute-Aufruf ohne Aktionsrecht. Keine Fachdaten/DB angefasst.

## Liefergrenzen

Keine Belegvariante ist dadurch registriert oder schreibend freigeschaltet.
BELEG-020 Teil 2 bleibt offen: Meridian-Metadaten, kanonischer Domain-Command-Adapter
mit Schema/Idempotenz/Versionspruefung, Ergebnisnormalisierung, Aktionszustand,
Registry/Routing/Inventare und echte Sichtpruefung. Dieser Slice prueft die
Client-Ausfuehrungsgrenze, nicht die gesamte serverseitige MCP-WRITE-Durchsetzung.
Fehlende permission-Deklarationen sind weiter ueber die Masken-Governance zu schliessen;
eine nicht deklarierte Berechtigung wird hier nicht erfunden.
