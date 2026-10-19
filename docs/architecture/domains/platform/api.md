---
title: Platform — Identitaets-API
type: reference
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Geschuetzte Sessionwege und gemeinsame Ausfuehrungsidentitaet.
---

# Identitaets-API

| Weg | Berechtigung und Wirkung |
| --- | --- |
| `GET /api/v1/identity/session` | Gepruefte eigene Sitzung; Subjekt, ERP-Mandant und konfigurierte Grenzen |
| `POST /api/v1/identity/session/logout` | Widerruft die eigene gebundene Sitzung einschliesslich erneuerter Token |
| `POST /api/v1/identity/subjects/revoke` | Mandantenadministration; widerruft bisherige Sitzungen eines Subjekts im eigenen Mandanten |

Alle Wege verwenden dieselbe Provider- und Mandantenpruefung. Der Rumpf des
administrativen Widerrufs benennt nur das Zielsubjekt; der Urheber kommt aus dem
geprueften Token. Widerrufe und ihre Urheber werden im gemeinsamen Speicher
atomar protokolliert. Ein Widerruf erzeugt kein Verbot kuenftiger Neuanmeldungen;
Benutzerabschaltung ist ein anderer Vertrag.

`identity_context` traegt die verifizierte Identitaet auch durch interne Aufrufe
und Arbeits-Threads und entfernt sie beim Ende der Anfrage. Das Modul ist kein
Ersatz fuer Mandate, Fachrechte oder Objektpruefungen. Die Agenten- und
Ressourcenvertraege werden daran angebunden und separat abgenommen.


## Administrative Integration (in Arbeit)

Die `tenants`-Wege verwenden eine ausdrückliche Mandanten-/Plattformberechtigung.
Journalhistorie verhindert physische Löschung; `POST /tenants/{target_id}/block`
erhält Buchungen und sperrt Zugriffe über die gemeinsame Sitzungsgrenze.
Administrative Zielauswahl verändert den aktiven Mandanten nicht.

`GET /identity/budgets`, `POST /identity/budgets/root`,
`POST /identity/budgets/allocate` und `GET /identity/consumption-ledger` bilden
technische, hierarchische Kontingente ab. Der native Maskenweg
`POST /identity/budgets/actions/{action_key}` prüft Vorschau und Ausführung
gegen dieselben Identitäts-/Kapazitätsregeln. Eine Vorschau schreibt keine
Kontingente und kein Verbrauchsereignis. Jede Vergabe besitzt einen Urheber.

[Abnahmestand und offene Verbrauchs-/Provider-/Handbuchintegration](../../../quality-assurance/identity-administration-20261012.md).


## Studio-Fachdialog (2026-10-15)

`GET /studio/catalog` erweitert den vorhandenen Katalog um versionierte fachliche Eingabevertraege. `POST /studio/dialogue` klaert Anforderungen und erzeugt ausschliesslich einen serverseitig kataloggebundenen Vorschlag. Der optionale Modellmodus nutzt den konfigurierten LLMGateway und das bestehende eigene Tokenkontingent; fehlende Mittel oder ungeklärte Anbieterabschluesse eroeffnen keinen Bypass. `POST /studio/harvest-preview` berechnet manuelle Testeingaben ueber den Agrar-Domain-Service ohne Datenbank-, Buchungs-, Bestands- oder externe Wirkung. Beide POST-Wege verlangen die vorhandene Beleg-Bearbeitungsrolle; der Dialog verwendet den verifizierten Mandantenkontext.

Entwurfsspeicherung bleibt ausschliesslich im bestehenden versionierten, idempotenten Studio-Speicher. Der Vorschauvertrag wird nicht als durch grain.v1 abgenommene produktive Prozessvariante veroeffentlicht. Neue MCP-/CLI-Schreibwerkzeuge werden daraus nicht freigeschaltet. [Architekturentscheidung](../../../adr/adr-studio-semantic-contracts.md), [QA](../../../quality-assurance/studio-semantic-20261015.md).


## Getrennte Qualitaetsbewertung im Studio

Der manuelle Vorschauvertrag ergaenzt quality_limit_pct unabhaengig von impurities_free_pct. Die Antwort kennzeichnet quality_limit_exceeded dreistufig (unbekannt/eingehalten/ueberschritten) und settlement_authorized immer false. Diese Angaben erteilen keine Vertragsfreigabe. [Fachlicher Kontrollvertrag](../../harvest-deduction-contract-standard.md).

## Versionierte native Studio-Ausgangsfassungen (2026-10-16)

GET /studio/native-sources liefert einen begrenzten, durchsuchbaren Katalog eigener verfuegbarer nativer Masken mit Quellhash. POST /studio/native-imports verlangt bestehende Beleg-Bearbeitungsrechte, angezeigten Quellhash und UUID-Idempotenzschluessel. Der Server sichert die Ausgangsfassung im bestehenden revisionsgebundenen Studio-Speicher; Mandant und Urheber stammen ausschliesslich aus der Anmeldung. Importierte Entwuerfe aktivieren keine Maske und erzeugen keinen Simulations- oder Freigabenachweis. [Schrittweise Migration](../../studio-native-migration.md).

Snapshot-Lesewege unter /read-models/snapshots verwenden ebenfalls den geprueften Mandanten; ein Queryparameter waehlt keinen anderen Mandanten. Alle generischen technischen Snapshot-Lese- und Schreibwege verlangen die vorhandene admin-Rolle.


## Personalakten: Identitaetsgrenze

GET /api/v1/personal/employee-files/{employee_ref} verlangt PERSONAL_LESEN, PERSONAL_BEARBEITEN, PERSONAL_ADMIN oder admin. actorRole ist ausschliesslich ein Ansichtsfilter nach dieser Berechtigung, keine Rollenvergabe. POST desselben Weges mit /documents verlangt PERSONAL_BEARBEITEN, PERSONAL_ADMIN oder admin; sein Urheber wird aus dem geprueften Token uebernommen. Der alte POST-Queryparameter actorRole ist entfernt und uebermittelt keine Rechte.

Die kanonische Metadatentabelle domain_hr.employee_file_documents wird durch hr_employee_files_20261019 angelegt. Fehlende oder fehlerhafte Persistenz antwortet generisch503, niemals mit einem erzeugten Demo-Dokument oder falschem201. Ungueltige Kalenderdaten und umgekehrte Gueltigkeitszeiträume werden vor SQL abgewiesen. Die Personalakten-Sichtbarkeitsklasse manager ist keine allgemeine Realm-Berechtigung. Selbstservice und zugelassene Vorgesetztenbeziehungen benoetigen eigene gepruefte Objektbeziehungen; dieser Vertrag erteilt sie nicht.
