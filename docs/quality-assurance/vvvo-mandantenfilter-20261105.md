---
title: VVVO und Sachkunde - Mandantenfilter im Service
type: reference
audience: [agent, entwickler, qa]
owner: Codex Lead
status: lokal abgenommen
last_reviewed: 2026-11-05
version: 1.0.0
---

# Mandantenfilter im VVVO-/Sachkundeservice

Der vorhandene nachtraegliche Pythonvergleich verhinderte regulaere Fremdaenderungen, las aber die Zeile zuerst ohne Mandantenfilter und gab bei fremden und unbekannten Datensaetzen verschiedene Fehler aus. Das folgende Update filterte nur nach ID.

Beide Einzelabfragen filtern jetzt ID und Mandant bereits in SQL. Auch das VVVO-Update filtert eigenstaendig auf den Mandanten; `RETURNING` bestaetigt eine tatsaechlich geaenderte Zeile. Verschwindet die Zeile oder wechselt ihr Mandant zwischen Lesen und Update, wird kein Erfolg gemeldet und kein Service-Commit ausgefuehrt. Fremde und unbekannte IDs haben denselben Nicht-gefunden-Vertrag. Bestehende Datumsberechnung und Rueckgabefelder bleiben erhalten.

## Pruefmethode und Grenzen

Der neue Verhaltenstest wertet die SQL-Anweisungen auf echten PostgreSQL-TEMP-Tabellen aus. Ein enger Testadapter ersetzt ausschliesslich die zwei qualifizierten Tabellenziele; Praedikate, Bindewerte und SQL-Auswertung bleiben erhalten. Eigene und fremde Zeilen liegen gemeinsam ohne RLS in der TEMP-Tabelle, damit RLS einen fehlenden SQL-Filter nicht verdeckt. Der simulierte Mandantenwechsel erfolgt kontrolliert vor dem Update, er ist kein Nachweis zweier nebenlaeufiger Verbindungen.

Sessions verwenden Savepoints innerhalb einer aeusseren Transaktion. Selbst der vorhandene Service-Commit persistiert dadurch keine Pruefdaten. Kein neues Schema, keine neue Datenbank, kein Container und keine Migration. Dies prueft Service-SQL und Persistenzwirkung, keine JWT-, Rollen-, reale Tabellen-FK- oder systemweite RLS-Abnahme.

Die Liste in domain_ops und der Pruefservice in domain_compliance sind weiterhin unterschiedliche fachliche Register. Deren Zusammenfuehrung, Erfassungswege, Audit-/Commandanbindung sowie ueberfaellige/fehlende Faelligkeitsdaten bleiben eigene Folgeaufgaben. Der ungenutzte operator wird durch diesen Slice nicht als Auditnachweis ausgegeben.

## Nachweise

- Neuer PostgreSQL-Test plus bestehende Servicetests: **21 passed in 2.40s**, Exit 0, keiner uebersprungen.
- Gegenprobe mit altem Service ausschliesslich im Arbeitsspeicher: **3 failed, 1 passed**. Fremd-/Fehl-ID fuer denselben Aufruf sowie das Update nach Mandantenwechsel fallen gezielt durch.
- Vor/nach jedem DB-Lauf: Revision `ruestlisten_tabelle_20261103`, fremde Clients 0. Rolle `valeo_agent`, nur eigene TEMP-Tabellen, vollstaendiger Rollback.
- Vollstaendiger Doc-Generator-Abgleich: Exit 0. Alle neun Verbesserungsscanner bestanden, Snapshot stabil. Doku-Code-Drift 0.
- Keine API-, Masken- oder Schemaaenderung; generierte Artefakte bleiben aktuell. Gesamt-CI auf dem PR steht aus.
