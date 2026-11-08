---
title: Studio Audit- und Vorlagenmigration
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Funktionale Audit- und Vorlagenmigration mit echten SQL- und Runtime-Nachweisen.
---

# CRM-Kampagnenvorlage: technischer Teilnachweis

Die Route verwendet die native Definition `crm/campaign-template` für bestehende
Datensätze und `new`/`neu`. Die Definition beschreibt die vom Backend tatsächlich
unterstützten Felder Name, Beschreibung, Kampagnentyp, Betreff, Nachricht und
Aktivstatus. Metadaten sind systemseitige Daten und werden durch die menschliche
Bearbeitung nicht überschrieben. Bearbeiten und Duplizieren sind für Agenten
gesperrt und verwenden den ausdrücklich deklarierten Resource-Response-Adapter.

Die Template-Endpunkte serialisieren JSON-Metadaten korrekt und begrenzen ihre
Rückleseabfragen auf den Mandanten. Der enge Test
`tests/test_crm_campaign_template_slice.py` prüft den Definitionsvertrag,
JSON-Nutzlasten, den Mandantenfilter und 404 bei fremden oder fehlenden Objekten
mit einer injizierten Fake-Session, ohne Datenbank. Ergebnis: 4 bestanden.

Die gezielte React-Abnahme `campaign-template-studio.test.tsx` nutzt die echte
Detail- und Create-Runtime samt Compiler und simuliert Transport, Anmeldung und
Navigation. Sechs Tests bestanden: Detailabruf und vorbefülltes Update,
Duplikatnavigation, Serverfehler, Berechtigungssperre, Neuanlage und Abbrechen.
Dies ist kein Browser- oder End-to-End-Nachweis gegen einen laufenden Server.

Die erste Implementierung wurde versehentlich außerhalb des akzeptierten
Migrationsquellbaums vorgenommen. Die betreffenden Änderungen wurden gezielt in
`artifacts/migration-repair-source` übertragen; die Tests wurden dort erneut
ausgeführt. Die ursprünglichen Änderungen außerhalb dieses Baums bleiben separat.

## Abschliessender Lead-Nachweis

Der reale SQL-/Kanalnachweis und die Browser-Komponentenabnahme sind nachgeholt;
siehe [gemeinsame Abnahme](studio-audit-template-20261028.md). Vorherige Hinweise
auf ausstehende Pruefungen beschreiben den damaligen Uebergabestand.
