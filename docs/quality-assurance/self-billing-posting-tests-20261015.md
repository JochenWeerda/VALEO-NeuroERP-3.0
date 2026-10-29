---
title: Self-Billing-Buchungsvertraege nachziehen
type: reference
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-15
---

# Kanonischer Eingangsvertrag statt alter Buchungserwartung

Sechs bisher rote Tests erwarteten die alte implizite Steuerkonfiguration, eine Lieferantenverbindlichkeit im Soll oder verschluckte Buchungsfehler. Der bereits abgenommene Fachweg verwendet einen ausdruecklichen mandantengebundenen Eingangssteuerschluessel und bucht Aufwand/Vorsteuer im Soll, Verbindlichkeit im Haben. Ein Buchungsfehler muss die aeussere Transaktion abbrechen koennen.

Die bestehenden Unit-Vertraege verwenden jetzt eine ausdruecklich benannte Steuerfixture und testen die korrekte Bruttogutschrift auf dem Verbindlichkeitskonto sowie ausgeglichene Soll-/Habensummen. Ohne Steuerkonfiguration wird auch ein Nullbeleg vor dem Journalzugriff abgewiesen. Dieser Negativfall bescheinigt keine allgemeine Zulaessigkeit von Nullbelegen. Fehler werden weitergegeben und es erfolgt kein Zwischencommit.

Alle 33 Buchungsintegration-Unitfaelle und die drei vorhandenen kanonischen Self-Billing-Vertraege bestanden: 36 bestanden, keine Skips. Keine Aenderung des Fachcodes, keine neue Datenbank oder Dockerinstanz. Die echten Transaktions-/Steuernachweise bleiben die bereits abgenommene grain.v1-Kette und ihre SQL-Vertraege.
