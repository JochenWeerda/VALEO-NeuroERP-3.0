---
title: Agentic Studio Auftrag und CI-Nachlauf
type: reference
audience: [entwickler, agent, architect]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Abnahmeplan und ehrlicher Lieferstand

## CI-Nachlauf der Baselinesenkung

Gepruefter Commit: bd54b5cd5. Die unabhaengige Integritaetspruefung einschliesslich Godfile-Ratsche war erfolgreich. [Quality Gate](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745449) insgesamt fehlgeschlagen: Backend und Dependency Scan. Diese Fehler werden nicht durch Studio-Ausnahmen verdeckt.

Erfolgreich: [Docs Governance](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745165), [Docs Build](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745247), [PostgreSQL-Tests](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745104), [kritische semantische E2E-Pfade](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745364) und [E2E Smoke](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745100).

Fehlgeschlagen: [Service Security](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745074) und [Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745192). Der getrennte CI/CD-Lauf war beim Abruf noch nicht abgeschlossen. Kein Gesamt-Gruen-Nachweis. develop bleibt an der bereits dokumentierten privaten Identitaetspruefung eines fremden CI-Vorgaengers blockiert; kein Hook-Bypass.

## Etappe 1: Architekturauftrag

Nutzerplan als [STUDIO-SEMANTIC-001](../architecture/studio-semantic-standard.md) uebernommen und mit bestehender Governance verknuepft. Dies ist eine Dokumentationsetappe, kein Nachweis fertig implementierter Dialogfunktionen.

## Noch abzuarbeitende Funktionsabnahme

1. Bestehende Studio-Baseline im Browser: anlegen, bearbeiten, speichern, erneut oeffnen, validieren, Vorschau. Eingaben und Historie vergleichen; Wiederholung darf keine Zusatzversion erzeugen.
2. Fachkatalog: freigegebene Vertragskennungen, Versionen, fachliche Bezeichnungen, Synonyme, Einheiten, Wertebereiche, Fachverantwortung und Berechtigungen; fehlende Bindung sichtbar sperren.
3. Mehrstufiger Dialog: Getreideannahme-Anforderung, gezielte Rueckfrage zur Waage, nachvollziehbare Antwort, kontrollierte Entwurfsanpassung; nur freigegebene Katalogelemente.
4. Interaktive Referenzmaske: Lieferant, Kontrakt, Fahrzeug, Verwiegung und Qualitaet; bestehende Domain-Berechnung statt nachgebauter Geschaeftsmathematik. Ungueltige und nicht endliche Werte verweigern. Vorschau ohne produktive Nebenwirkungen.
5. Revisionstreue Prozesssimulation: erlaubte Eingaben, Rollen-/Mandantengrenzen, Wiederholung, Fehler und Korrektur; bestehender grain.v1-Nachweis gilt nicht automatisch fuer neue Varianten.
6. Freigabeuebergabe: exakte unveraenderte Revision, verwendete Vertraege, Historie und Artefaktsynchronisierung; unvollstaendige Nachweise sperren. Kein Agent darf selbst kritische Regeln aktivieren.

Echte Browserbilder und Pruefergebnisse werden erst nach Ausfuehrung ergaenzt. Keine fingierten Screenshots oder Testzahlen. Gemeinsamen Pruefstand wiederverwenden, keine neue Datenbank oder Container.
