---
title: Technische Snapshot-API an geprueften Mandanten binden
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Abgegrenzte Snapshot-Sicherheitskorrektur

Die drei technischen Snapshot-Wege verwendeten tenant_id aus der Anfrage. Jetzt kommt der Mandant ausschliesslich aus get_tenant_id. Fremde Querywerte waehlen weder beim Lesen noch beim Anlegen einen anderen Mandanten. Da technische Snapshots beliebige fachliche Inhalte enthalten koennen, verlangen diese generischen Wege die vorhandene admin-Rolle. Fachliche Lese- und Schreibwege behalten ihre bisherigen Bereichsrollen; es entsteht kein neues Rechtesystem.

Das vorhandene Persistenzmodell wird bei der regulaeren additiven Initialisierung registriert. Kein Schema wird waehrend eines Requests angelegt. Die kleinen Unit-Vertraege ersetzen ihren Store ausdruecklich und akzeptieren keine 500-Antwort mehr als Erfolg.

71 Tests bestanden: sieben neue HTTP-Grenzfaelle fuer Mandant, Rolle und fehlende Anmeldung sowie vorhandene Snapshot-, SQL-, Reporting- und Paginationstests. Testidentitaeten sind als Testgrenze ausgewiesen; sie behaupten keine Signaturpruefung. Keine neue Datenbank oder Container, kein Reset und keine Migration.

Die OpenAPI-Lieferung ist auf genau die drei bestehenden Snapshot-Pfade begrenzt. Keine Pfade entfernt, keine fremden Fachpfade oder bestehenden Schemas geaendert. Die gleichzeitig vorbereitete Studio-Erweiterung ist nicht Bestandteil dieses Meilensteins. Dateibesitz und Nutzerfreigabe stehen unter CI-SOURCE-REPAIR-20261016 und dem geerbten CI-GRUEN-Claim.
