---
title: Identitätsverwaltung — Mandanten, Kontingente und Anmeldereparatur
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Nachweis und offene Integrationsgrenzen der administrativen Identitätswege.
---

# Identitätsverwaltung: Abnahmestand

Die Gesamtumsetzung ist in Arbeit. Der persönliche Kennwortwechsel und die
Authenticator-Einrichtung wurden vom Auftraggeber auf später verschoben.
Eine abgeschlossene persönliche Browseranmeldung wird nicht behauptet.

## Mandanten

Der Verwaltungsweg verwendet die verifizierte Identität und denselben
Datenbankzugang wie die übrige Anwendung. Mandantenadministration ist für
Stammdaten einschließlich Einstellungen erforderlich. Mandantenübergreifende
Verwaltung und Neuanlage benötigen ausdrücklich `platform:tenants:manage`;
eine Mandanten-Adminrolle oder `admin:all` ersetzt diesen Scope nicht.
Der administrative Zielparameter `target_id` ist kein Wechsel des aktiven
Mandanten. Outbox-Ereignisse halten handelnde Kennung und beide Mandanten fest.

Löschen ist eine physische Löschung, kein anders benanntes Sperren. Jede
Journalzeile, auch Entwurf oder Storno, verhindert die Löschung mit 409.
Der Mandant wird unter `FOR UPDATE` gesperrt; der vorhandene Journal-Fremdschlüssel
im Prüfstand bindet parallele Einfügungen. Weitere geschützte Referenzen werden
vor dem persistenten Sperrmarker durch Flush geprüft. Keine Kaskadenbereinigung
fremder Daten oder geschützter Referenzen. Sperren setzt den Status in PostgreSQL
und eine dauerhafte gemeinsame Zugriffssperre in Redis. HTTP, Streams und interne
Ausführung prüfen diese Sperre an derselben Sitzungsgrenze.

Redis wird vor dem abschließenden DB-Commit gesperrt. Bei einem nachfolgenden
DB-Ausfall bleibt der Zugriff sicher gesperrt; die administrative Abstimmung
dieses Fehlers ist ein Betriebsfall. Keine atomare Transaktion zwischen zwei
Datenspeichern und keine automatische Entsperrung behaupten. Die Sperre dient
auch nach physischer Löschung als Schutz gegen weiter gültige Tokens.

## Kontingente und Nebenbuch

Die technische Vergabe ist im eigenen Mandanten persistent und atomar in Redis.
Ein ausdrücklicher Plattformscope stellt das Wurzelbudget bereit. Nutzer und
Agenten erhalten Unterbudgets; deren Summe kann das Elternbudget nicht erhöhen.
Nichtadministrative Vergabe braucht `identity:quota:allocate` und Eigentum am
Elternbudget. Service-Identitäten benötigen `agent:delegate` und können nur
Agentenbudgets aus ihrem eigenen Budget vergeben. Die Tiefe ist auf drei
Budgetkanten begrenzt; direkte Kinder sind zusätzlich je Budget begrenzt.

Vergabereferenz, handelnde Kennung und Inhalt verhindern doppelte Vergabe.
Reservierungen binden Auftrag, Budget und Menge; Abrechnung ist einmalig,
abweichende Wiederholungen werden abgewiesen. Verbrauch oberhalb der reservierten
Menge wird nicht still gebucht. Unbenutzte Reservierungsmengen werden freigegeben.
Das technische Nebenbuch speichert Vergabe, Reservierung und Abrechnung samt
verifizierter Kennung. Es ist keine finanzielle Kostenbuchung und kein behaupteter
unveränderlicher Finanzbeleg; Preis-/Währungsgrundlagen und Aufbewahrung sind
noch zu integrieren. Budgetgrenzen sind Gesamtmengen, kein bereits eingeführter
monatlicher Tarif. Aufstockung, Periodenwechsel und Betriebsbereinigung bleiben offen.

**Weiter offen:** tatsächliche Reservierung/Tokenmessung an allen Modellaufrufen,
Agentenregistrierung und Unteragentenerzeugung gegen diese Kontingente, effiziente
Archivierung/Partitionierung des Verbrauchsspeichers und tatsächliche Providerkosten.
Die vorhandenen Modellaufrufe sind durch diesen Teilstand noch nicht kontingentiert.

## Native Masken

`admin/identity-budgets` und `admin/token-consumption` verwenden ausschließlich
ScreenDefinition → RenderPlan → UniversalMaskRuntime → UniversalMaskRenderer.
Vergabe: Eingaben, Bestätigung, echte wirkungsfreie Vorschau, Begründung und
Ausführung mit erneuter Autorisierung. Beide Definitionen erreichen
`generatorReady=true`, Advisory 1,00. Plattformrechte werden im UI ebenso wie
im Backend ausschließlich aus konkreten Scopes abgeleitet. Eigene Kontingente
bleiben für angemeldete Nutzer erreichbar. Das UI verleiht keine Serverrechte.

## Anmeldereparatur

Der öffentliche Vergleich ergab: Port 3001 war mit `Invalid parameter:
redirect_uri` abgewiesen. Die genaue Callback-Adresse und die Web-Origin wurden
nach ausdrücklicher Freigabe im bestehenden Client ergänzt und gespeichert geprüft.
Danach zeigte der echte Browser `invalid_scope` für `openid profile email`.
Die öffentliche Discovery nennt tatsächlich nur `openid`, `offline_access`, `roles`.

Realmdateien und Bereitstellung deklarieren nun Standard-Scopes samt
Claim-Mappings, ordnen deklarierte Client-Scopes additiv zu und verifizieren die
Persistenz. Bestehende Scope-Policies, Nutzer, Kennwörter, Rollenzuordnungen,
Clientgeheimnisse und fremde Mappings werden erhalten. Fehlende optionale
Entwicklungsreferenzen ohne Scope sind entfernt. `identity_type` wird aus dem
administrativ geschützten Attribut übernommen, niemals als konstante Identität
erfunden. Grundlagen: [Keycloak-Protokollmapper](https://www.keycloak.org/admin-api/protocol-mappers).

**Laufender Provider:** Die freigegebene Scope-/Mapper-Reparatur wurde angewendet
und ihre Persistenz bestätigt. Öffentliche Anmeldeprüfungen für Port 3000 und
3001 liefern die Keycloak-Anmeldeseite und deren CSS-Ressourcen mit HTTP 200.
Die anschließende frische Browserprüfung von `/login` auf Port 3001 über
„Mit SSO anmelden“ erreicht die Kennwortmaske mit Benutzerkennung und Kennwort,
ohne `invalid_scope`. Es wurden keine persönlichen Zugangsdaten eingegeben.
Eine vollständige authentifizierte Browserabnahme und Screenshotserie stehen aus.

## Prüfungen

Vorhandener Prüfstand `valeo_probe`, Revision
`steuerschluessel_einheit_20261012`; kein Reset, keine Migration und kein neuer
Container bzw. neue Datenbank. PostgreSQL-Fachtests verwenden eigene Daten mit
äußerer Transaktion und Savepoints; Redis-Verträge räumen nur eigene Präfixe auf.

Die abgegrenzte Meilensteinprüfung besteht aus 110 bestandenen Verträgen
(eine Warnung), einschließlich des Schutzes der Mandanteneinstellungen.
Unversionierte Agenten-Prototypfälle sind in dieser Zahl nicht enthalten.
Sechs UI-Rechteverträge bestehen; TypeScript und ESLint der beiden neuen Masken bestehen.
Generatoren und GitHub-Gesamtabnahme sind beim Meilenstein separat nachzuweisen.

Die abgegrenzte Quellstand-Prüfung erzeugt 3142 OpenAPI-Pfade. Dabei meldet
FastAPI doppelte Operation-IDs im bestehenden CRM-Router, unter anderem für
Einwilligungen und Segmente. Dieser Befund ist nicht durch bestandene
Mandanten-/Kontingenttests abgedeckt und bleibt für die Gesamtabnahme offen.

## Rest des beauftragten Handbuchablaufs

Noch nicht erledigt: echter synthetischer Kennwortlogin, Mandanten-Anlage-/
Sperr-/Löschmasken, Administrator- und Nutzeranlage, vollständige Agentenanlage,
Screenshots sämtlicher Eingaben und Ergebnisse. Der persönliche Erstzugang und
seine MFA werden davon getrennt gehalten. Es wurden keine persönlichen
Zugangsdaten veröffentlicht und keine fremden Mandanten gelöscht.
