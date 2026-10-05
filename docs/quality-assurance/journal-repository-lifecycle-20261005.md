---
title: Journal-Repository nutzt zentrale Lifecycle-Pruefungen
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
version: 1.0.0
---

# Journal-Repository-Lifecycle

## Ergebnis

Post/Reverse/Update/Delete verwenden FinanceTransactionService mit derselben
Repository-Session. Doppelte ungesperrte Statuswechsel und die alte Storno-
Implementierung ohne vollstaendige Betragsspalten/Sequenzstempel sind entfernt.
Get/Exists/Count benutzen mandantengebundene Journalspalten statt geerbter
is_active-/Soft-Delete-Annahmen, die dieses Modell nicht erfuellt.
Get-All verschluckt SQL-Fehler nicht mehr als leeres erfolgreiches Journal.
Nur echte EntityNotFound-Fehler erhalten das bestehende None/False-Ergebnis;
Validierungs- und Datenbankfehler propagieren. Arbitrary Updatefelder, Datum,
NULL-/Leerwerte und ueberlange Werte werden explizit abgewiesen.

## Abnahme

282 Tests bestanden in 17.51 Sekunden, davon 35 neue Repository-Vertraege
(27 echte PostgreSQL). Reale gespeicherte Betragsdubletten, Kopfsummen,
Fremdtenant und inaktive Konten sperren Post/Reverse. Stempel verhindern
physisches Delete; unstempelte eigene Entwuerfe werden vollstaendig geloescht.
Post/Reverse erzeugen spiegelgleiche Betragsspalten und einen neuen Stempel;
kein zweiter Post/Storno. Update eines gebuchten Belegs ist gesperrt.

Zwei weitere Konkurrenzfaelle durch den Repository-Einstieg (Post/Post,
Reverse/Reverse): pg_locks weist das echte Warten der zweiten Verbindung
nach. Trotz vorher geladener alter ORM-Identitaet sieht sie nach dem Commit
den neuen Status und wird abgewiesen. Die vorhandenen fuenf Service-
Konkurrenzfaelle sowie Betrags-, Konto-, Hash-, Posting-, CRM-, Agrar-,
Harvest-, Procurement- und Storno-Regressionen bestanden.

Pruefstandstatus vor Tests: vorhandener valeo_probe, Revision
 eudr_uebermittlung_20261001. Wiederverwendung der kleinen eigenen
Tabellenfixtures, nur eigene Schemas/Datensaetze/Transaktionen und gezieltes
Cleanup. Keine neue Datenbank, Dockerinstanz, gemeinsame Migration oder Reset.
Lokaler Nachweis: artifacts/journal-repository-tests.log.
Ruff: neuer Test und neue Repositoryanteile sauber. Gesamtes implementations.py
hat 13 bestehende Befunde ausserhalb des Slices und E401 im unangetasteten
Create-Helper. Kein behauptetes globales Lint-Gruen.

## Handoff und Grenzen

Claim d66f051bc. API/DTO nicht editiert: L3-JOURNAL-SOURCE-20260910 steht
weiter als fremd in arbeit im Workboard. Hier wird dieser Claim weder
uebernommen noch umgeschrieben. Keine neue API/Service/Domain-Grenze.

Die API faengt Domainfehler noch mit einem generischen HTTP-500-Zweig ab;
die korrekten Guards verhindern die Mutation, die HTTP-Abbildung bleibt
zu integrieren. Das Container-Repository hat weiterhin eine getrennte
Session. Audit/Anchor committen nach dem Journal und sind nicht atomar.
Repository-Create verwendet noch den konkurrierenden Hashweg und verwirft
nicht gemappte DTO-Felder. Diese Anlage-/API-Vertraege brauchen einen
eigenen abgestimmten Slice. Cancel-Grund fehlt im ORM. Kein vollstaendiger
GoBD-Beleg, keine globale Journal-Abnahme und kein Gesamtprojektabschluss.
