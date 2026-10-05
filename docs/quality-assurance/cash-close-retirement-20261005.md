---
title: Kassenabschluss ohne Scheinbuchung
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
version: 1.0.0
---

# Kassen-Direktbuchung entfernt

## Befund und Vertrag

Der alte cash_close_day summierte alle posted-Tagesjournale des Tenants,
unabhaengig vom Kassenbezug, wandelte Geld in float und schrieb die Summen
erneut als posted-Header. Zwei Zeilen auf Kontonummer 1000 als account_id
hatten weder belegte Kontoidentitaet noch fachliche Gegenkontierung oder
kanonische Betragsspalten/Hashstempel. Leer-/Wiederholungsaufrufe konnten
Null-/Doppeljournale verursachen. Der Handler behauptete einen fertigen
Kassenabschluss ohne belegten Bestand oder Bewertungsvertrag.

Dieser Schreibweg ist vollstaendig entfernt. POST finance/cash/close-day
gibt 409 mit dem fehlenden Bestands-/Gegenkontierungsnachweis als Grund,
ohne SQL/DML/Commit/Rollback. Die noch konsumierte Aktion erzeugt keinen
Erfolg und kein Ersatzjournal. ADR-076 Proposed dokumentiert die bewusste
API-Aenderung, Domain Pack und eigener OpenAPI-Snapshot beschreiben 409.
Globale OpenAPI-Datei gehoert dem fremden OPENAPI-DRIFT-REFRESH-Claim;
sie wurde hier nicht geaendert. Keine Maske/Adapter/Archiv eingefuehrt.

## Nachweise

397 Regressionen bestanden in 23.02 Sekunden, danach 12 gezielte Cash-/
Finance-API-/Snapshotchecks in 3.65 Sekunden. Vier Cash-Vertraege: 409 ohne
Datenbankaufrufe/Erfolg, drei Wiederholungen gegen echte private Journal-
Tabellen erhalten exakte Header-/Zeilensnapshots, OpenAPI ohne 200 und
Abgleich des eigenen Routensnapshots mit der echten Router-Generierung.
Die bestehende Cash-Erfolgsannahme im Finance-Actions-Test wurde ersetzt;
sein Perioden-Testdouble bildet jetzt die bereits integrierten Isolation-
und Transaktionssperrabfragen explizit ab, keine Produktions-Testfallausnahme.
Alte Cash-SQL-Testdouble-Pfade und unbenutzte Testimporte entfernt.

Weitere Journal-/Betrag-/Konto-/Status-/Stempel-/Perioden-/Transaktions- und
Posting-/CRM-/Closing-/Agrar-/Harvest-/Procurement-Regressionen bestanden.
Vor Tests vorhandener valeo_probe Revision wiegung_kanonisch_20261005.
Keine neue DB/Dockerinstanz, gemeinsame Migration oder Reset; kleine eigene
Tabellenfixtures und gezieltes Cleanup. Logs:
artifacts/cash-close-retirement-tests.log und cash-close-contract-tests.log.

C4-Render-Check, Architekturindex --require-complete, Containerinventar und
strict Drift bestanden; keine neuen Endpoints/Prefixe/Container. Agent-
Handbuch: alle fuenf Artefakte aktuell. Neue Cash-/Testanteile Ruff-sauber;
vier bestehende Modulbefunde ausserhalb des Cashhandlers bleiben offen.
Bestehende Starlette/httpx-TestClient-Deprecation ist eine Warnung, kein Test-
fehler. Keine globale CI-/Security-/UI-Gruenbehauptung.

## Handoff und Grenzen

Claim a41ba8833. Bestehende Masken-Fehlerbehandlung in finance/kasse.tsx
liest HTTP-Fehlerdetail und erreicht bei 409 keinen positiven Abschluss-
Toast oder Erfolgspfad. Dies wurde am Code geprueft; keine Browser-/Masken-
Abnahme und keine fremden UI-Edits. Keine fremden Godfile-Baselines angehoben.

Ein echter Kassenabschluss braucht belegten Bestand/Beleg, Tenant/Konten,
Bewertung/Gegenkonto und eine gemeinsame Journal/Perioden/Audit-Transaktion.
Diese Fachfunktion bleibt offen. Andere rohe Journal-Schreiber, Source-
Whitelist im fremden DTO-Claim, API/Audit/Anchor-Atomizitaet und Schema/Hash
bleiben offen. Gespeicherter Altbestand/fremde Daten wurden nicht geloescht.
