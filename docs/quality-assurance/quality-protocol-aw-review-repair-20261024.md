---
title: Qualitaetsprotokoll – Reparatur der Reviewbefunde AW-R01/02/05/06
type: reference
owner: Codex
status: lokal-geprueft
last_reviewed: 2026-10-24
---

# Qualitaetsprotokoll: gesicherter Lese- und Finalisierungsweg

AW-R01: `POST .../{id}/approve|finalize` verwendet den `sub` des verifizierten
Tokens als `approved_by` und im Abschlussereignis. Ein `approved_by` im Body
oder `X-User-ID` kann den Urheber nicht bestimmen. Die bestehenden Fachrollen
bleiben an beiden Routen aktiv.

AW-R02: `QualityProtocolRepositoryImpl` verlangt einen Mandanten beim Aufbau.
Alle Protokollabfragen, Updates und Finalisierungen filtern nach diesem
Mandanten. Vor Erzeugung und Import eines Protokolls wird die referenzierte
Ernteannahme im selben Mandanten nachgewiesen. Die Versionssuche greift erst
nach exklusiver Sperre dieser Annahme auf mandantengebundene Protokolle zu;
damit erhalten konkurrierende Erzeugungen keine identische Folgeversion.
Eine unbekannte oder fremde Annahme liefert 404, ohne Fremddaten preiszugeben.

AW-R05: Update und Finalisierung sperren die Protokollzeile und laden ihren
Zustand aus der Datenbank neu, auch wenn die ORM-Session sie zuvor gelesen hat.
Nach `is_final=true` wird eine weitere Änderung oder Finalisierung abgelehnt.
Die Finalisierung spült ihre Änderung ohne eigenen Commit; Abschlussereignis
und Protokoll werden gemeinsam committed. Die Outbox wird erst nach Commit
über den dauerhaften Auslieferungsweg gespiegelt (`mirror_on_store=False`).

AW-R06: `GET /api/v1/agrar/quality-protocols` liefert eine mandantengebundene,
auf 200 Einträge begrenzte `protocols`-Liste für die Quality-Worklist.
Die weitere Studio-Maskenparitaet bleibt ein eigener Integrationsauftrag.

Abnahme im bestehenden `valeo_probe` nach Statusprüfung, ohne neue Datenbank
oder Reset: 4 PostgreSQL-Tests für Finalize-vs-Finalize,
Finalize-vs-Update mit vorgeladenem ORM-Objekt, fremden Protokollzugriff und
fremde referenzierte Ernteannahme. Ausschließlich eigene synthetische Zeilen
wurden danach gezielt gelöscht. Weitere 53 fokussierte Tests inklusive echter
RS256/JWKS-HTTP-Identität, Fremdmandant, manipulierter Body-/Header-Urheber,
Repository-Sperren und 45 Nullwertverträge bestanden. Eine vollständige
Browser-, NATS- oder Release-Abnahme ist damit noch nicht belegt.

Lead-Nachlauf: fuenfter echter PG-Fall bestaetigt gemeinsamen Rollback von
Finalisierung und Abschluss-Outbox. Drei weitere RSA/JWKS-HTTP-Faelle pruefen
invalides Token, fehlende Rolle und Tokenurheber trotz manipuliertem Body/Header.
Testdatenbankzugriff ist lokal auf valeo_probe beschraenkt; CI verwendet die
ausdruecklich konfigurierte Job-Datenbank, keine neue Instanz.
