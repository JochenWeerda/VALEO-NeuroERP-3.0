---
title: Agrarportal – eigenes Handelspartnerverzeichnis
type: reference
audience: [agent, entwickler, qa, architect]
owner: Codex
status: aktiv
last_reviewed: 2026-11-16
version: 1.0.0
description: Abnahme der lesenden Mitgliedschaftsermittlung als erste Brokerphase.
---

# Liefergrenze

GET `/api/v1/portal/handelspartner` liest eigene gueltige Kundenzuordnungen.
Kein Kontextwechsel, kein Token, keine neue Rolle, keine Fachschreibwirkung.
Nur ID, Name, Anzahl eigener Kundenkonten und Markierung des Token-Mandanten.
`stage=discovery_only`, `context_switch_available=false` verhindern eine
Verwechslung mit einem bereits ausfuehrbaren Wechsel.

Die bestehende Portalrechtetabelle bestimmt die zulaessigen Kundenrollen.
Die Systemverbindung ist zwingend, als `valeo_system` ohne Superuser und mit
BYPASSRLS; ihre Transaktion wird explizit READ ONLY. Fehlkonfiguration,
falsche Rolle und zu grosse Ergebnismenge antworten neutral mit 503.
Identitaetsfehler werden vor jedem DB-Zugriff abgewiesen. Kein freier Subject-
oder Tenant-Selektor und kein App-DB-Fallback. Der bestehende signierte
Mandantenkontext bleibt unveraendert.

# Nachweise

- 13 isolierte Service-Vertraege: gepruefte Identitaet und eindeutiger Tenant,
  fehlende Systemkonfiguration, falsche DB-Rollen, Parameterbindung,
  Wiederherstellung des Kontexts, Rollback/Close, Ergebnislimit, neutrale Fehler.
- Zwei HTTP-Adaptertests: Subject aus Authentifizierung statt Query,
  Authentifizierungsfehler verhindert DB-Aufruf, POST bleibt 405.
  Dependency-Overrides sind kein kryptographischer JWT-Nachweis.
- PostgreSQL-SQL-Verhalten gegen den bestehenden `valeo_probe`:
  zwei eigene Handelspartner, mehrere eigene Kunden, fremdes Subject,
  widerrufene/abgelaufene Beziehung, geloeschter Kunde, inaktiver Mandant,
  ausgeschlossene interne Beziehungsrolle und unbekanntes Subject.
  Exakte produktive SQL, eigene synthetische Daten vollstaendig zurueckgerollt.
  Dieser SQL-Test verwendet die zum Seeden notwendige privilegierte
  Pruefstandverbindung; er allein beweist nicht den produktiven Rollenpfad.
- Die finale gemeinsame Suite besteht mit 23 Tests ohne Skip (13 Service-, zwei HTTP-,
  zwei PostgreSQL- und sechs Einrichtungsvertraege). Die ersten 16 Tests bestanden ebenfalls. Ein erster Lauf scheiterte an
  einem zu langen synthetischen Kundenschluessel; das Fixture wurde gekuerzt.
- Zusaetzlicher echter Service-Test mit Datenbankrolle `valeo_system`,
  SQL-Reihenfolge und `SHOW transaction_read_only=on` bestanden im finalen Lauf.
- Generierte OpenAPI, Architekturindex, Endpunkt-/Serviceinventar und
  Agent-Handbuch nachgezogen. Response-Model- und Summary-Abdeckung jeweils
  3729/3729, null untypisierte Wege oder fehlende Summaries.

Keine neue Datenbank, kein Container, kein DDL, kein Reset, keine Migration.
Pruefstand vorher vorhanden auf `psm_register_entfernt_20261104`.
Keine Bereitstellung dieses Backends im lokalen Frontendbetrieb behauptet.

# Folgende Phase

Vertrauenswuerdige Ausstellung und Widerruf des aktiven Handelskontexts,
rollengetrennte Kundenauswahl, Cache-/Requestwechsel und echte Browserabnahme.
Kundengebundene Belegvariante, Foto-Anfrage, Adress-/Silo-Vorschlaege und
Futterberatung bleiben gesonderte Fachslices. Die verifizierte Einzeltenant-
Bindung wird fuer diese Folgearbeit nicht aufgeweicht.

## Gezielte Einrichtung der Lese-ACLs

Der erste echte Systemrollenlauf war rot: Rolle vorhanden, aber PostgreSQL
42501 auf allen drei Quellen. Keine fachliche Datenluecke als leere Liste
kaschiert. Der neue Weg `scripts/provision_portal_directory_reads.py` plant
standardmaessig nur und prueft vorhandene Rolle und Tabellen vor jeder Vergabe.
`--apply --rollback` erprobt transaktional; `--apply` uebernimmt gezielt
Schema-USAGE und SELECT auf genau diese drei Quellen. Keine Rollenanlage,
Passwortaenderung, Eigentumsuebernahme, Defaultprivilegien oder Schreibgrants.
Vorhandene Rechte anderer Verbraucher werden nicht widerrufen.

Am 2026-11-16 war kein fremder aktiver Pruefstandprozess vorhanden. Probelauf
und gezielte Vergabe auf `valeo_probe` bestanden. Entwicklung und Livebackend
unveraendert. Fuer weitere Umgebungen ist dieselbe gezielte Einrichtung nach
koordiniertem Fenster notwendig, falls die regulaere Rollenprovisionierung
diese Leserechte noch nicht eingerichtet hat. `DATABASE_URL` kommt nur aus
der Prozessumgebung; Direktverbindungen tragen `PGAPPNAME=agent:codex-portal-broker`.

## Gesamt-CI: explizite Inventarklassifikation

Der erste gemeinsame main-Lauf meldete ausschliesslich im Integritaetsjob
eine fehlende Klassifikation von portal_handelspartner.py. Die neue Kategorie
identity-membership beschreibt die gepruefte eigene Mitgliedschaft ueber
Mandanten hinweg mit Quellen-/Test-/QA-Verweis. Keine falsche Einstufung als
stateless/public/shared und keine globale Ausnahme. Drei Regressionstests
bestaetigen Klassifikation und weiterhin rote unbekannte Adapter. Lokal alle
neun Verbesserungspipelines bestanden, einschliesslich Tenant-Klassifikation
und Baseline-Integritaet.

Der Backendlauf43946243084 erkannte im physischen Tabellenkatalog exakt drei
fehlende read_by-Verweise auf den neuen Portal-Service; Schemas, Tabellen,
Spalten und sonstige Katalogwerte unveraendert. Die beiden generierten
Katalogdateien wurden aus fresh-schema-table-catalog dieses exakten CI-Laufs
uebernommen. Keine Migration oder lokale Schemaanpassung.

## Frontend-Gesamtvertrag fuer main

Der erste komplette Frontendlauf am gebuendelten Stack fand 15 Fehler in
fuenf Testdateien (2136 bestanden). Vier Workspace-Vertraege erwarteten noch
das Dashboard als Standard, alte interne Rankingcodes und automatisch
geoeffnete Inbox. Sie verwenden nun den expliziten Arbeitsuebersichtsmodus
bzw. oeffnen Arbeitsuebersicht/Document-Inbox ueber die echte Bedienfolge.
Die Auth-Refresh-Attrappe stellt die inzwischen benoetigten getUser/
getAccessToken-Leser ausdruecklich bereit; ohne Portalsitzung wird weiterhin
kein Kundenkontokopf gesendet. Keine Produktions-Fallbacks fuer Testattrappen.

Gezielte Gesamtabnahme dieser fuenf Dateien: 23/23 bestanden, kein Skip.
Auth-, Fehler-, Filter-, Routing-, Rangfolge- und Nichtbuchungspruefungen
bleiben erhalten. Artefakt: artifacts/main-integration-frontend-contracts.json.
