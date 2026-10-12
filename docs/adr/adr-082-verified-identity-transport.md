---
title: Verifizierte Identitaet und Mandantenbindung an allen API-Transporten
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: proposed
last_reviewed: 2026-10-12
description: Konsolidierung des vorhandenen OIDC-Vertrags mit zentraler Selektorbindung und Streaming-Isolation.
---

# ADR-082: Verifizierte Identitaet an den Transportgrenzen

**Status:** Proposed. **Datum:** 2026-10-12. Umsetzung des vom Auftraggeber
beauftragten [Identitaetsentwurfs](../architecture/security/central-identity-agent-management-proposal.md).

## Kontext

Die vorhandenen Providerpruefungen wurden durch Entwicklungs-Token, lokale
HS-Token, Header-/Defaultmandanten und separate WebSocket-Authentifizierung
umgangen. Signierte Token allein verhindern keine fremden Mandantenfilter in
Pfad, Rumpf oder Query. Ereigniskanäle waren nicht nach Mandanten getrennt.

## Entscheidung

Der bestehende JWKS-Validator erfordert konfigurierte Aussteller- und
Empfaengerkennung sowie Ablauf und Subjekt. Kein Entwicklungs-Token erteilt
Administratorrechte. Geschuetzte Nicht-API-Wege werden ebenso geprueft. Bereits
verifizierte Claims werden nur innerhalb derselben Anfrage und fuer dasselbe
Credential wiederverwendet. Rollen- und Scope-Vertraege bleiben erhalten.

Ein einzelner eindeutiger ERP-Mandant aus `tenant_id` beziehungsweise
`mandanten_id` ist Pflicht. Die zentrale Bindung prueft alle Headerwerte,
Pfad-, Query-, Formular- und JSON-Selektoren einschliesslich verschachtelter
Modelle. Fehlende deklarierte Selektoren bekommen den geprueften Kontext;
kein Standardmandant entscheidet. Doppelte JSON-Felder werden abgewiesen.
Die Routeinstallation bewahrt FastAPI-Abhaengigkeits- und Ressourcenbereinigung.

WebSockets verwenden dieselbe Providerpruefung und koennen den Mandanten nicht
auswaehlen. Die Produktionsmiddleware beendet Empfang und Zustellung bei
Tokenablauf und setzt den Kontext auch bei Fehlern zurueck. Browser-Querytoken
sind ausschliesslich fuer WebSocket und die beiden vorhandenen SSE-Wege
zulaessig. Mehrdeutige Credentials werden abgewiesen.

SSE-Kanaele verwenden `(tenant_id, channel)` als Schluessel. Sender nennen den
Mandanten ausdruecklich. Streamablauf und Abmeldung entfernen ausschliesslich
die eigene Subscription. Keine globale mandantenuebergreifende Ereigniszustellung.

## Konsequenzen

Alte Entwickleranmeldungen berechtigen nicht mehr zu Fachzugriffen; die Anmeldung
muss ueber den konfigurierten Provider erfolgen. Providerattribute brauchen
administrativ beschraenkte Pflege. Signaturpruefung, Mandant und Rollen ersetzen
keine Fachobjektpruefung oder sofortigen Widerruf. Diese Folgeschritte sowie
Agentenmandate und Ressourcenbudgets bleiben eigene Abnahmen.

Signierte Slack-/Teams-Nachrichten haben bislang frei uebergebene Rollen und
Defaultmandanten. Sie bekommen daher keine generische Auth-Ausnahme. Ihre
Vertrauensgrenze braucht eine verwaltete Integrationsidentitaet und Zuordnung.
Kalender-Capability-Feeds brauchen einen getrennten, explizit begrenzten Vertrag;
die alte pauschale Konfigurationsausnahme allein erteilt keinen Zugriff.

Nachweis: [QA](../quality-assurance/identity-transport-20261012.md).
