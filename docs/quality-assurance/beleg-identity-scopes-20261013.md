---
title: Belegrechte im Identitaetstoken
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: belege:read/write als rollenbeschraenkte Keycloak-Projektion vorhandener Bereichsrechte.
---

# Belegrechte im Token — 2026-10-13

## Entscheidung und Lieferung

Auf ausdrueckliche Vorgabe des Auftraggebers werden ausschliesslich die vorhandenen
Bereichsrollen aus app/auth/finance_roles.py verwendet. Keine neuen BELEGE-Rollen,
keine separate Berechtigungsmatrix und keine Rollenvergabe an bestehende Nutzer.

BELEG_READ_ROLES ist das gemeinsame Rollentupel fuer open_items_read/beleg_read;
BELEG_WRITE_ROLES traegt die unveraenderten bisherigen beleg_write-Rollen.
Keycloak projiziert genau diese Tupel auf die rollenbeschraenkten Client-Scopes
belege:read und belege:write. Die vorhandenen Ausnahmen admin/manager werden gemaess
dieser bestehenden Fachregel uebernommen, nicht als neue Sonderregel eingefuehrt.

- Lesen: FINANCE, SALES, CRM und EINKAUF jeweils LESEN/BEARBEITEN/ADMIN sowie die
  vorhandenen allgemeinen Ausnahmen.
- Bearbeiten: FINANCE, SALES und EINKAUF jeweils BEARBEITEN/ADMIN sowie die vorhandenen
  allgemeinen Ausnahmen; reine Leser und CRM-Rollen erhalten kein Schreib-Scope.
- Schreibberechtigte erhalten das Leserecht gemaess vorhandener Rolle ebenfalls.

Die Scope-Zuordnung wird vor der Client-Zuweisung serverseitig gespeichert und
zurueckgelesen. Nicht deklarierte Rollen, fehlende Rollen, gescheiterte Speicherung oder
abweichende Scope-Repräsentationen brechen die Integration ab. Fremde Mappers bleiben
erhalten. Wiederholte Provisionierung erzeugt keine zusaetzlichen Rollen oder Mappings.

Die Provisionierung ergaenzt die lokalen Frontend-/Backend-Clients sowie die Definition
des vorhandenen Staging-Clients valeo-erp-staging. Im laufenden lokalen Keycloak wurden
nur die beiden Scopes, deren Rollenbindungen und deren Zuweisung an die zwei bestehenden
ERP-Clients integriert. Kein Realm-Reset, keine Kennwort-/MFA-Aenderung, keine neue
Datenbank oder Dockerinstanz. Staging wurde als Konfiguration geprueft, nicht deployt.

## Verifikation

24 gezielte Tests bestanden: Beleg-Scope-Vertrag, bestehende Provider-Provisionierung
und unveraenderter Fachrollen-Katalog (34 Rollen). Signierte RSA-Testtokens gehen durch
die produktive HTTP-Identitaetsgrenze und den echten MCP-Dispatch fuer beleg.arten:
belege:read erlaubt das Werkzeug; belege:write allein und fehlende Beleg-Scopes liefern
403. Dieser Aufruf greift nicht auf Geschaeftstabellen zu. JWKS-Lieferung und
Sitzungsspeicher sind in diesen Vertragstests isoliert.

Am echten lokalen Provider sechs Scope-Evaluationen (je beide ERP-Clients):

| Bestehende Rolle | belege:read | belege:write |
|---|---|---|
| keine Bereichsrolle | nein | nein |
| EINKAUF_LESEN | ja | nein |
| EINKAUF_BEARBEITEN | ja | ja |

Die Provider-Evaluation wurde auch mit ausdruecklich angefragten beiden Scopes
geprueft; der Request allein erteilt kein Recht. Drei eigens dafuer angelegte
Provider-Identitaeten wurden im finally-Pfad geloescht; keine ERP-Fachdaten angelegt.
Ausgegeben wurden ausschliesslich Pruefergebnisse, keine Namen, E-Mails, Kennwoerter,
Token oder persoenlichen Identitaetsdaten. Evaluation ist kein Browser-Login-/MFA-Nachweis.

## Grenzen und Anschluss

Neue Anmeldung fuer sicher neu ausgestellte Token verwenden. Personen und Agenten
erhalten ihre vorhandenen Bereichsrollen ueber die bestehende Identitaetsverwaltung;
belege:write darf keine fachliche Freigabe oder MCP-Freischaltung ersetzen.
Die drei Beleg-MCP-Werkzeuge bleiben lesend; keine schreibende Capability wurde aktiviert.
Buchung/Storno, Preis- und konkrete Aktionsrechte sowie MCP-WRITE-001 bis 015 sind
weiterhin an den jeweiligen Domain-Command und dessen Freigaberichtlinie gebunden.

Der grosse bestehende MCP-Beleg-Fachtest verwendet direkte DB-Sessions und bedarf einer
expliziten Bindung an valeo_probe vor Ausfuehrung. Er wurde fuer diesen Identitaetsslice
nicht als DB-Abnahme verwendet. Kein Gesamt-CI-/Browser-Gruen aus diesen Nachweisen ableiten.

## Referenzen

- [Keycloak: Client scopes und Rollenbindung](https://github.com/keycloak/keycloak/blob/main/docs/documentation/server_admin/topics/clients/con-client-scopes.adoc)
- [MCP-Schreibstandard](../architecture/mcp-write-standard.md)

## Reale Browser-/Runtime-Abnahme (Nachtrag 2026-10-13)

Der Auftraggeber hat EINKAUF_BEARBEITEN fuer die vorhandene synthetische Browser-
Testkennung ausdruecklich freigegeben. Die Rolle ist lokal additiv zugewiesen;
Kennwort, MFA und andere Rollen wurden nicht geaendert. Die Neuanmeldung lief ueber
regulaeres Logout, Keycloak-Passwortanmeldung und OIDC-PKCE-Callback. Im tatsaechlich
neu ausgestellten Browser-Token wurden belege:read, belege:write und die vorhandene
Einkaufsrolle bestaetigt; ausgegeben wurden nur Boolesche Pruefergebnisse.

Der erste reale Aufruf lieferte Unknown ERP tool (404): app-Code war eingebunden,
config/mcp_erp_tools.yaml dagegen nur als alter Image-Stand vorhanden. Der gepushte
Katalog wurde gezielt in den bestehenden Backend-Container uebertragen und der
Prozess neu gestartet. Kein Container/DB neu angelegt; Worker starten langsam.
Die Compose-Definition bindet den kanonischen Katalog jetzt read-only ein, damit
spaetere Container-Neuerstellungen nicht erneut einen alten Katalog verwenden.
Der bestehende Container hat bis zur naechsten regulaeren Neuerstellung noch die
kopierte Katalogfassung; fuer aktuelle Aufrufe ist sie aktiv.

Reale Browser-Aufrufe mit dieser Sitzung: beleg.arten 200 (neun Arten), beleg.suchen
200 (null sichtbare Belege), beleg.lesen fuer eine absichtlich nicht vorhandene
Einkaufsbeleg-ID 404 mit mandantenbezogener Ablehnung. Kein Fachdaten-Schreibzugriff.
Ein positiver Einzelbelegabruf ist damit **noch nicht abgenommen**; er erfordert
passende Referenzbelege und die autorisierte Testmandantenbindung. Die vorhandenen
MCP-Schreibsperren wurden nicht aufgehoben.

Screenshot ohne Kennwort/Token: artifacts/beleg-relogin-granted-20261013.png
(lokales Arbeitsartefakt). Der geteilte Git-Index war weiterhin gesperrt; keine
fremde Sperre geloescht und keine fremden staged Aenderungen zurueckgesetzt.
