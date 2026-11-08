---
title: Agentenvorschlaege beim Speichern mandantengebunden
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-14
---

# Mandantengrenze beim Speichern eines Agentenvorschlags

AgentProposalRepository.save prueft vor jedem Schreibzugriff, dass der Vorschlag denselben Mandanten wie der Aufruf traegt. Wird eine vorhandene ID geladen, muss deren persistenter Mandant ebenfalls uebereinstimmen. Ein fremder Datensatz wird als nicht gefunden abgewiesen, bevor Reviewstatus, Kontext, Ergebnis oder Begruendung geaendert werden.

Die Luecke betraf den vorhandenen Vorschlagsweg des Gesamtziels: Lesen pruefte den Mandanten bereits, Speichern ueber eine bekannte ID tat dies nicht. Es wird kein zweites Vorschlagsregister eingefuehrt; die bestehende Repositorygrenze wird geschlossen. Die Pruefung ersetzt nicht die Token-/Rollenpruefung des aufrufenden Domainwegs.

Abnahme: 23 Tests bestanden, davon drei neue PostgreSQL-Faelle und 20 bestehende Operator-Agent-Faelle. Die SQL-Faelle verwenden den gemeinsamen valeo_probe und eine aeussere Transaktion mit Session-Savepoints. Eigene Inserts und Updates werden vollstaendig zurueckgerollt; kein neuer Container, keine neue Datenbank, kein Reset. Geprueft sind Fremd-ID ohne Aenderung, abweichender Proposal-Mandant ohne Insert sowie erlaubtes eigenes Update und verborgenes fremdes Lesen.

Offen bleiben transaktionale unveraenderliche Vorschlagshistorie, Idempotenz bei unklarem Commit-Ergebnis und die Studio-/Prozessvariantenanbindung. Der gemeldete mandantenlose Altbelegfilter im DocumentRepository ist separat offen. MCP-Schreibfunktionen werden durch diese Reparatur nicht freigeschaltet.
