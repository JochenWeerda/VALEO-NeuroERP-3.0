---
title: WhatsApp-Browserauftraege im bestehenden Kanalspeicher
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: proposed
last_reviewed: 2026-10-11
description: Dauerhafte Benachrichtigungsvorbereitung ohne zweiten Speicher und ohne behauptete Browserzustellung.
---

# ADR-081: Persistente WhatsApp-Benachrichtigungsvorbereitung

**Status:** Proposed. **Datum:** 2026-10-11.

## Kontext

User-Ziel ist WhatsApp Web via Computer Use. Die fluechtige Outbox verliert
Auftraege beim Neustart und verhindert weder doppelte Vorbereitung noch
Umdeutung desselben Replay-Schluessels. public.outbox_events beschreibt
Ereignisveroeffentlichung, keine WhatsApp-Zustellung.

## Entscheidung

Die Vorbereitung verwendet die vorhandenen Tabellen
domain_shared.channel_process_threads und channel_thread_audit_items. Keine
neue Tabelle, Migration, Datenbank oder Event-Payload auf dem allgemeinen Bus.
Namensraum whatsapp.browser.notification.v1 ist ausschliesslich dem
geschuetzten Benachrichtigungsdienst vorbehalten; er ist kein generisch
ausfuehrbarer/freigebbarer Prozess. Das generische persistente Repository
filtert ihn vor SQL-Lesen und verweigert Speichern/Ersetzen dieses Namensraums.

Auftrags-ID entsteht deterministisch aus Mandant, Benachrichtigungstyp und
Idempotenzschluessel. PostgreSQL-Transaktionssperre serialisiert dieselbe ID;
Inhaltsfingerprint und Tokenurheber entscheiden ueber zulaessigen Replay.
Auftrag und Urheber-Audit werden in einem Savepoint erzeugt; der Aufrufer
committet gemeinsam. Fehler propagieren, kein Memoryfallback. HTTP-Konflikt
ist 409, ungueltiger/fehlender Schluessel 422. API verlangt verifizierten
Tokenkontext und crm:write; Lesen crm:read. Listen sind auf 50 voreingestellt,
maximal 200. Synchrone DB-Arbeit laeuft in synchronen FastAPI-Handlern.

## Konsequenzen

pending_browser ist dauerhafte Vorbereitung, keine Browser-Versandfreigabe
und kein Zustellnachweis. Browserkonto, Empfaenger-/Fachreferenzpruefung,
Leasing/Abbruchabgleich und sichtbarer Versandnachweis sind Folgearbeit.
Der Speicher enthaelt private Nachrichten; generische Kanal-/Approvalwege
duerfen sie nicht lesen oder veraendern. Allgemeine Kanal-Isolation ausserhalb
des reservierten Namensraums ist durch diesen ADR nicht abgenommen.

Die zwei toten Benachrichtigungs-Placeholder in sales_delivery_notes entfallen:
customer_phone ist kein Feld des Anlegemodells; der Rechnungsweg bestand nur
aus pass. Ein kuenftiger Fachverbraucher benoetigt eine tatsaechliche
Empfaengerermittlung, Urheber und stabilen Schluessel in seiner Fachtransaktion.

Grundlage: [ADR-008](adr-008-eventing-outbox-standard.md) und
[User-Transportvertrag](../workflows/whatsapp-web-computer-use.md).
