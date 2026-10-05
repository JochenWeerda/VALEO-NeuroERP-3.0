---
title: Journal-Service mit expliziter aeusserer Transaktion
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
version: 1.0.0
---

# Aeussere Journaltransaktion

## Vertrag

FinanceTransactionService(db, tenant_id, commit_on_success=False) fuehrt
Create/Update/Delete/Post/Cancel/Reverse ohne eigenen Commit aus. Ein
zentraler Abschlusshelfer flusht alle Aenderungen und refresht die betroffenen
Header. Zeilen-/Kopf-/Kettensperren bleiben bis zum aeusseren Abschluss bestehen.
Der Aufrufer besitzt Commit und Rollback, etwa ueber Session.begin().
Validierungs-/SQL-Fehler werden weitergegeben; sie koennen gemeinsam mit
vorher erfolgreichen Schritten zurueckgerollt werden. Der Service faengt
keinen Fehler als erfolgreichen Teilschritt ab.

Default commit_on_success=True erhaelt das vorhandene Verhalten. Bestehende
Consumer sind hier nicht implizit umgestellt. Beide Modi benutzen exakt
dieselben Konto/Betrag/Tenant/Status/Stempelguards und dieselben Mutationen.
Keine neue API/Domain/Spalte/Migration oder neue Fachfunktion.

## Abnahme

337 Tests bestanden in 22.17 Sekunden, davon 16 neue echte PostgreSQL-Faelle:
Alle sechs Mutationen jeweils Commit und Rollback, Create/Post/Reverse in
einer gemeinsamen Transaktion mit beiden Abschluessen sowie spaeterer
Domain- und Datenbankfehler nach erfolgreicher Anlage/Buchung. Der SQL-
Fehler ist ein echter UniqueViolation-Fehler aus derselben privaten Tabelle.

Eine unabhaengige Session liest Header und Zeilen einschliesslich kompletter
row_to_json-Snapshots. Vor aeusserem Commit bleiben sie unveraendert; erst
danach sind alle Aenderungen sichtbar. Rollback stellt den exakten Anfangs-
snapshot wieder her, einschliesslich Sequenz/Hash/Status/Zeilen. Ein Commit-
Spy weist zusaetzlich nach, dass keine Mutation intern committet. Bestehende
321 Vertrage inklusive Sperrwartebelegen und selbst committendem Default
bestanden. Ruff fuer Service/Test und eigenes Whitespace-Gate sauber.
Log: artifacts/journal-transaction-tests.log.

Vor Tests war der vorhandene valeo_probe auf Revision
genossenschaft_mitgliederregister_20261005. Nur kleine eigene Tabellenfixtures,
eigene Datensaetze/Transaktionen und gezieltes Schema-Cleanup. Keine neue
DB/Dockerinstanz, gemeinsame Migration oder Reset. Keine fremden Godfile-
Dateien/Baselines editiert und keine gruene Gesamt-CI behauptet.

## Integrationshinweis und Grenzen

Claim d65ab10ea. Die Faehigkeit ist Voraussetzung fuer Journal/Audit/Anchor-
Atomizitaet, keine abgeschlossene Consumer-Integration. Repository und API
verwenden weiterhin den Default. log_fibu_audit committet und verschluckt
Fehler; dieser Helper ist ungeeignet fuer den aeusseren Modus. Anchor-
Repository und weitere Consumer muessen Commit und Pflichtfehlerbehandlung
an dieselbe Unit-of-Work abgeben. Kein Helper mit eigenem Commit darf
innerhalb einer behaupteten atomaren Transaktion aufgerufen werden.

Die API/DTO-Dateien behalten ihren fremden Workboard-Besitz. NULL-Waehrung,
Datum/Laengen/Hash, Cancel-Grund und weitere SQL-Schreiber bleiben offen.
Neu priorisierter Codebefund: optionale Create-Periode kann die Pruefung
umgehen; Post/Reverse haben keine Periodenpruefung. Eigener offener Folge-
Slice JOURNAL-PERIOD-ENFORCEMENT-20261005, keine ungepruefte Freigabe.
