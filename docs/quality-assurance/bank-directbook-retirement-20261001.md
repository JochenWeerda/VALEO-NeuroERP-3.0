---
title: Bank-Direktbuchung entfernt
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
---

# Bank-Direktbuchung entfernt

## Ergebnis

Der Saldenvergleich schreibt keine Journale oder MATCHED-Zeilen mehr.
auto_book=true wird vor dem ersten Datenbankzugriff mit 409 abgewiesen;
interner Standardwert ist echtes False. Keine geratenen Gegenkonten,
keine booking_suggestions; can_be_booked ist im Ergebnis Literal False.
Die bestehende Maske entfernt Book, Textmuster-Zuordnung, Regelstatistik und
lokale Zuordnungseingaben. Save fuehrt nur den Vergleich aus.
Entwicklungsfreigabe fuer Altlasten steht verbindlich in AGENTS.md.

## Nachweise

62 Backend-Vertraege bestanden: acht neue Retirement-Vertraege, bestehende
Finance-Actions, Importdatum, Konto-/Replay-Vertraege und fuenf bestehende
Reconciliation-Modelltests. Drei neue Faelle
laufen auf vorhandenem valeo_probe und pruefen unveraenderte Bankzeilen,
keinen Commit und keine erzeugten Journale, auch beim internen Aufruf.
Zwei Maskentests pruefen Aktionsangebot, gesperrte Zuordnungscheckbox und
Save-Aufruf mit auto_book=false ohne Buchungsmeldung oder Weiterleitung.
Nach Fixture-Importbereinigung acht neue Vertraege erneut ausgefuehrt.
Ruff und ESLint der Maske bestanden (Testdatei von ESLint ausgeschlossen).
Business-Time-Ratchet (205/114), Agent-Handbuch und Architektur-Drift
(strict: 932 Routen/259 Services/448 Endpointmodule) bestanden.

Lokale Logs: artifacts/bank-directbook-tests.log,
artifacts/bank-directbook-frontend.log. Der fokussierte Typecheck ist rot
wegen bestehendem src/components/cti/CallWidget.tsx:54 (string | undefined).
Dieser fremde Fehler wird nicht als Gruen oder durch Grenzwertsenkung verdeckt.

## Grenzen und Handoff

Kein Nachweis fuer einen echten Hauptbuchabgleich. Der bestehende Lesepfad
braucht Mandanten-/Kontobindung, einen belegten GL-Link, eindeutige
Journalbetragsfelder, PARTIAL-/Vollstaendigkeitspruefung und sichtbare
Lesefehler. CSV-Buchungsstichtag ist kein bankseitiger Saldennachweis.
OpenAPI nur eigenes ReconciliationResult und Flag-Beschreibung integrieren;
der globale OPENAPI-DRIFT-REFRESH-Claim bleibt beim Owner. EUDR-Refresh und
bestehende doppelte Operation-IDs sind keine Retirement-Abnahme.
GitHub-CI und Deployment getrennt abnehmen; Gesamtziel bleibt offen.

## Ressourcen

Bestehender valeo_probe, Revision eudr_sorgfaltserklaerung_20261001 vor Lauf.
Nur eigene randomisierte Testdaten, Fixture-Cleanup. Kein Reset, keine
Migration, keine neue DB oder Dockerinstanz.
