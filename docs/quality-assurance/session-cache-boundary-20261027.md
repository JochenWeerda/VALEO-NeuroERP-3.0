---
title: Sitzungsgrenze fuer Browsercache und montierte Maskenzustaende
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# Zentrale Sitzungsgrenze

Der globale QueryClient in DataBootstrap und weiter montierte Komponenten
konnten Daten des vorherigen Sicherheitskontexts behalten. Das Inbox-Widget
besitzt beispielsweise einen eigenen geladenen Queue-Zustand. Eine neue
serverseitige Berechtigungspruefung bei prepare verhindert keine veraltete
Anzeige bereits geladener Daten.

DataBootstrap trennt nun den Datenprovider nach Subjekt, Token-Mandant und
normalisierten Rollen/Scopes. Ein Wechsel baut Provider und Kindzustaende neu
auf und bricht alte Abfragen ab beziehungsweise leert den alten Client.
Die Signatur des Tokens wird weiterhin ausschliesslich serverseitig geprueft;
der Browser liest Claims nur fuer die Cache-Trennung. Weder Token noch
Anzeigename oder E-Mail stehen im Cache-Schluessel.

Gleiche Identitaet und gleiche Rechte bei normalem Tokenrefresh erhalten den
Client und Formularentwurf. Reihenfolge und Dubletten von Rollen/Scopes
erzeugen keinen kuenstlichen Kontextwechsel.

## Nachweis

Vor Korrektur: vier Wechseltests fehlgeschlagen, Refresh-Test bestanden.
Nach Korrektur: sechs Tests bestanden, einschliesslich spaeter Antwort einer
alten Sitzung. Verwendet werden echtes React-Lifecycleverhalten und der echte
QueryClient; nur Authentifizierung und FeatureFlagProvider sind ersetzt.
Dies ist kein Browser-/Serverauthentifizierungsnachweis.

Sol mit geringer Denkleistung fuehrte den abgegrenzten Slice aus. Keine
Datenbank, Installation oder breite Testsuite. Unter Windows lagen TEMP/TMP
fuer den gezielten Vitest-Lauf im eigenen ignorierten Cache, um einen
temporaeren EPERM-Rename zu vermeiden. Die volle Typpruefung ist im gemeinsamen Frontend-Nachlauf bestanden
(tsc Projektbuild und vollstaendige Frontend-Typpruefung).
Der gezielte integrierte Nachlauf besteht mit 79 Tests in elf Dateien:
Sitzungsgrenze, Entityprojektion, Inbox und Workspace-Zusammensetzung.
Studio-Katalogcheck: 848 Definitionen synchron. Keine Datenbank verwendet.
Dies ersetzt weder Browserabnahme noch die noch rote Gesamt-CI.
