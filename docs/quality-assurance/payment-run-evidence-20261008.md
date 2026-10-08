---
title: Zahlungslauf mit belegter Vier-Augen-Freigabe 2026-10-08
type: reference
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: abgeschlossen
last_reviewed: 2026-10-08
---

# Freigabenachweis im Zahlungslauf

Der vorhandene HTTP-CommandEndpoint und der direkte Freigabeweg nutzen denselben
zentralen Guard. Fehlende authentifizierte Freigeber werden vor Datenbankzugriff
mit 403 gesperrt. Mandant und Lauf werden unter FOR UPDATE geprueft; unbekannte
oder fremde Laeufe bleiben 404. Nur draft mit belegtem, vom Freigeber verschiedenem
Ersteller ist freigabefaehig. Fehlende Ersteller sind keine Altbestand-Ausnahme.
Es werden keine Ersteller historischer Laeufe erfunden oder nachgetragen.

validate, dryRun, propose und execute pruefen dieselben Nachweise. Vorschauen
schreiben weder Fachdaten noch Audit/Outbox; der bestehende Delegationsweg
behaelt den gemeinsamen Commit von Freigabe, Audit und Ereignis. FINANCE_ADMIN
und die menschliche Vier-Augen-Freigabe bleiben erforderlich. forbiddenForAgents
bleibt erhalten: Diese Reparatur ist keine MCP-Zahlungsfreigabe.

## Abnahme

Original: 18 fehlgeschlagene und sieben bestandene neue Guard-/HTTP-Vertraege.
Reparierter isolierter Lieferstand: 36 Tests ohne Skip in 61,43 Sekunden gruen:
25 neue Guard-/HTTP-Vertraege, sechs bestehende Payment-API-Vertraege und fuenf
echte PostgreSQL-Zahlungsablauf-Vertraege. Geprueft wurden erfolgreiche Wirkung
mit authentifiziertem Freigeber, genau ein Audit/Ereignis, Wiederholung,
Mandantenisolation, fehlende Begruendung und schreibfreie Vorschau.

Die bestehende Testfixture legt ihren eigenen Testlauf mit dem belegten
Test-Ersteller maker an, verschieden vom authentifizierten Testfreigeber dev.
Nur die eigenen UUID-Testmandanten und deren Daten werden aufgeraeumt. Vorher
scripts/pruefstand_db.py --status: vorhandener valeo_probe, Revision
postfach_microsoft_20261008, keine fremde aktive Verbindung. Keine neue DB,
Container, Schemaaenderung, Migration oder Ruecksetzung.

Lokale Evidenz: artifacts/ci-payment-evidence-original.log und
artifacts/ci-payment-evidence-final.log. Unveraenderte Tests benoetigen lokal
freigegebene Windows-Asyncio-Sockets; keine Produkt-/Testabschwaechung.
Bestehende CI fuehrt diese Regressionen weiterhin aus; Folge-CI offen.

## Handshake und weitere Arbeit

FIN-CLOSE bleibt an ADR-076 gebunden: Kassenidentitaet, belegter Bestand,
exakte Bewertung und zentrale Gegenkontierung fehlen fuer einen echten Abschluss.
Keine Wiederbelebung des entfernten Direktbuchungswegs.

Zahlauf open_high bezeichnet weiterhin fehlende MCP-Anbindung unter
forbiddenForAgents; der menschliche HTTP-CommandEndpoint existiert bereits.
Die 31 blocked_no_endpoint bleiben offen. Lokale Formular-Neuanlage und Navigation
muessen von fachlich speichernden Aktionen unterschieden werden; echte Commands
muessen vorhandene Mandantenservices, Eingabeschemata und Transaktionen nutzen.
Kein pauschales Umetikettieren oder fingierter Endpoint. Fremde Postfach- und
MCP-Arbeiten unveraendert.
