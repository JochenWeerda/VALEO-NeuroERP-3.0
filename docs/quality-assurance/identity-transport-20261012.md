---
title: Identitaet und Mandantenbindung an HTTP und Streaming
type: reference
audience: [entwickler, agent, architect]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Abnahme und verbleibende Integrationsarbeit fuer die erste Stufe des zentralen Identitaetsentwurfs.
---

# Identitaet und Mandantenbindung

## Umsetzung

Vorhandene Providervalidierung ist die gemeinsame Grenze fuer HTTP, Rollen-
Dependencies und alle vier registrierten WebSocket-Wege. Fehlender ERP-Mandant,
mehrdeutige Claims, falscher Aussteller/Empfaenger, Ablauf, falsche Signatur,
Entwicklungs- und lokale HS-Token berechtigen nicht zu Fachzugriffen.

Zentrale Routebindung prueft deklarierte und mitgeschickte Mandantenselektoren;
fehlende Defaultfelder werden durch den geprueften Mandanten ersetzt. Headers
werden serverseitig gebunden. Doppelte JSON-Schluessel werden abgewiesen.
Auch ausserhalb `/api` gibt es keine pauschale Auth-Ausnahme. Query-Credentials
gelten nur fuer vorhandene Browserstreams. SSE-Zustellung erfolgt nach Mandant
und Kanal, WebSocket-Empfang und -Zustellung enden bei Tokenablauf.

## Nachweise

`tests/test_system_tenant_binding.py`: 41 echte HTTP-Vertraege mit RSA/JWKS,
ungueltigen Claims, zwei Mandanten, Query-/Header-/Rumpf-/Formular-/Pfadbindung
und erfolgreicher Rollenpruefung. Signaturen werden wirklich geprueft;
lediglich Schluesselverteilung und Providerkonfiguration sind Testgrenzen.

`tests/test_identity_transport.py` und `test_identity_streams.py`: echte
HTTP-/WebSocket-Requests, getrennte Terminalregistries, gebundener Copilotkontext,
Workflow-Cachezugriff, keine Cross-Tenant-Ereigniszustaellung und selektive
Bereinigung. Zusaetzliche Ablauf- und Parallelkontextfaelle werden mitgeprueft.
Nachbarvertraege fuer Realtime und Finanzrollen werden separat ausgefuehrt.
Keine neue Datenbank, Container, Migration oder Ruecksetzung.

Abnahmestand: 63 Transport-/HTTP-/Inventarfaelle gruen; 19 aktualisierte
Auth-/Mappervertraege gruen; 593 Finanzrollenfaelle und neun bestehende Realtime-
Faelle gruen. Zehn Workflow-Lifecycle-Faelle nach expliziter Testkontext-Isolation
gruen; 16 MCP-Signaturfaelle im integrierten Lauf gruen. Vollstaendige gemeinsame
Abnahme: alle 710 Faelle gemeinsam gruen (45,72 Sekunden). OpenAPI, Codeinventare, Architekturindex
und Agent-Handbuch werden aus isoliertem aktuellem HEAD plus eigenen Quellen
regeneriert; fremdes Arbeitsbaum-WIP wird dabei nicht mitgenommen.

## Betrieb und verbleibende Abnahmen

Die bisherige opaque Entwickleranmeldung reicht nicht mehr. Login ueber den
konfigurierten Provider; issuer/audience/JWKS muessen zusammenpassen und der
administrativ vergebene ERP-Mandant muss im Token stehen. Bestehende lokale
Demo-Tokenminting-Wege sind kein gueltiger ERP-Zugang.

Noch keine systemweite Gesamtfreigabe: Provider-Selbstpflege des Mandanten,
serverseitiger Sitzungs-/Rechtewiderruf, idle/absolute Limits, Agentenmandate,
objektbezogene Freigaben, Ressourcenlimits und Bank-/SEPA-Folgeobjekte sind
weitere Schritte. Alte Callback-/Kalenderausnahmen sind nicht freigegeben;
Slack/Teams brauchen verwaltete Identitaet statt mitgeschickter Rolle/Default.
Policy-Broadcasts haben weiterhin einen globalen Konfigurationsvertrag und
brauchen eine ausdrueckliche Shared-Policy-Abnahme.

OpenAPI-/Inventar-/Handbuch-Generatoren und externer CI-Gesamtlauf werden erst
nach Integration auf dem aktuellen gemeinsamen HEAD abschliessend geprueft.
Fremde Frontend-, Katalog- und Metadatenaenderungen bleiben geschuetzt.
