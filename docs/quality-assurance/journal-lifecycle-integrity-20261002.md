---
title: Journalstatus unter Transaktionssperre
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-02
version: 1.0.0
---

# Journalstatus unter Transaktionssperre

## Vertrag und Umsetzung

Update/Delete/Post/Cancel/Reverse im FinanceTransactionService laden den
eigenen Journalkopf unter FOR UPDATE. populate_existing aktualisiert auch
ein bereits im ORM-Identitaetscache vorhandenes Objekt; no_autoflush verhindert
das vorgezogene Schreiben lokaler alter Werte vor der Sperre. Der Status-
Guard sieht erst danach den aktuellen Zustand. Vor Betrag-/Tenantpruefungen
werden vorhandene Zeilen frisch geladen und unter FOR SHARE gelesen.
Die Sperren gelten bis zum bestehenden Commit/Rollback, nicht nur fuer den
Moment der Abfrage. Read-only get_by_id bleibt ohne Mutationssperre.

Jeder vorhandene Stempelteil (Sequenz, aktueller Hash oder Vorgaengerhash)
sperrt physisches Delete eines Entwurfs. Ein gestempelter Entwurf kann
stattdessen cancelled werden; Zeilen und Kettenmetadaten bleiben bestehen.
Ungestempelte eigene Legacy-Entwuerfe sind weiterhin gezielt loeschbar.
Fremde/ungeklaerte Zeilentenant-Daten sperren auch deren Delete. Zeilen-Delete
ist explizit auf den Header und eigenen Tenant begrenzt. Eine Referenz darf
bei Draft-Update nicht leer gemacht werden. Actor-Lookup erfolgt vor der
Statuszuweisung beim Post, statt bei Lesefehler einen Teilzustand zu setzen.

## Nachweise

247 Tests bestanden (10.36 Sekunden), davon 16 neue echte PostgreSQL-Faelle.
Fuenf Parallelfaelle: Post/Post, Post/Cancel, Post/Update, Post/Delete und
Reverse/Reverse. Eine unabhaengige Verbindung weist die tatsaechlich wartende
Transaktion via pg_locks nach. Der zweite Schreiber hatte vorher bewusst das
alte ORM-Objekt geladen; nach dem ersten Commit sieht er den neuen Status
und wird abgewiesen. Kein zweiter Stornobeleg, kein verlorener Statuswechsel.

Delete-Guards fuer alle drei einzelnen Stempelteile bewahren Header und
Zeilen. Cancel bewahrt Sequenz/Hash/Zeilen. Ungestempelte Legacy-Entwuerfe
werden real geloescht, auch nach vorgeladener ORM-Zeilenbeziehung. Fremde
Zeilen/Tenant und leere Referenzen sind abgewiesen. Bestehende Journal-,
Betrags-, Konto-, Stempel-, Posting-, CRM-, Storno-, Agrar-, Harvest- und
Procurement-Vertraege bestanden. Ruff und Whitespace bestanden.
Lokaler Nachweis: artifacts/journal-lifecycle-tests.log.

Vorhandener valeo_probe, Revision eudr_uebermittlung_20261001, wiederverwendete
kleine Tabellenkopien/Fixtures aus dem Betragsvertrag. Nur eigene Schemas und
Testtransaktionen, gezieltes Cleanup; keine neue DB/Dockerinstanz, kein
Reset oder gemeinsamer Migrationslauf. Die Paralleltests committen ausschliesslich
Datensaetze in ihrer eigenen Schemakopie, damit die zweite Verbindung sie sieht.

## Noch offen

Die Journal-API verwendet weiterhin einen getrennten JournalEntryRepository-
Weg: insbesondere delete_journal_entry liest draft und ruft danach Repository-
Delete auf. Er delegiert nicht an diesen Service-Guard; die kanonische
Integration dieser weiteren Schreiber ist naechste Arbeit, keine globale
Delete-/Concurrency-Abnahme. Grundpersistenz/Audit beim Cancel ist noch
unvollstaendig: cancel_reason ist im Journal-ORM nicht gemappt, der bisherige
hasattr-Zweig kann den uebergebenen Grund nicht speichern. Kein GoBD-Gesamtbeleg.

Consumer-Atomizitaet, Schema-Komposit-FKs/Betragsdubletten, vollstaendiger
Hash-Payload und skalierbarer Kettenzustand, reale Produktionsbewertung,
Bank-Migrationsintegration und fremder Handbuch-Drift bleiben offen.
Minor-Bugfix im vorhandenen Service; keine neue API/DTO/Maske/Domain.
