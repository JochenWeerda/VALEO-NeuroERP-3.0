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

# Kontraktprotokoll — Runtime-Migration (2026-10-28)

Die Definition verwendet die vertragsgebundene Auditquelle `/api/v1/kontrakte/{entity_id}/audit`, die sechs Auditspalten und das Auditprofil. Die beiden filterbaren Spalten steuern generisch die Eingaben. `NativeAuditListPage` nutzt Compiler und UniversalMaskRuntime mit vollständigem paginierten Projektorabruf sowie UniversalMaskRenderer. Die eingebettete Komponente übergibt die Vertragskennung; die eigenständige Route akzeptiert `contractId` oder `contract_id` als Abfrageparameter beziehungsweise einen Routenparameter `id`. Ohne Kennung erfolgt kein Datenabruf.

Der Fachendpunkt prüft bereits Leserechte und Mandantenzugehörigkeit. Sein `items`-Vertrag liefert Zeit, Akteur, Feld, alten und neuen Wert und Aktion; die bestehende Tabellenformatierung zeigt Datum/Zeit und Nullwerte an. Fehler des Projektors werden als Fehler angezeigt.

Gezielter Vitest `native-audit-runtime.test.tsx` wurde vorbereitet (fehlender Kontext, vollständiger mehrseitiger Transport, kombinierte Filter, Fehler). Der gezielte Test wurde anschließend vom Lead erfolgreich ausgeführt; eine Abnahme des realen Projektorwegs steht noch aus. Keine Datenbank, Migration oder Sicherheitsänderung.

## Renderer-Abnahme

Die Fixture `contract-audit-studio.fixture.json` wurde unmittelbar aus der Python-ScreenDefinition erzeugt. Der Test `contract-audit-studio.test.tsx` verwendet echte Runtime, Compiler und UniversalMaskRenderer; nur Transport, Anmeldungs-/Routenkontext und Overlay werden isoliert. Alle drei Tests bestehen. Der zuvor festgestellte leere Nullwert wird durch deklaratives `renderKind: text` für Alt- und Neuwert als Gedankenstrich dargestellt. Geprüft sind sechs Spalten, Datumsformat, Nullwert, kombinierte Filter über alle abgerufenen Seiten, eingebetteter Kontext, Standalone-Kontext per Query und Sperre ohne Kontext. Der Transport ist im Test isoliert; ein echter Projektor-/Browsernachweis bleibt separat offen. Keine DB/Migration/Container.

## Abschliessender Lead-Nachweis

Der reale SQL-/Kanalnachweis und die Browser-Komponentenabnahme sind nachgeholt;
siehe [gemeinsame Abnahme](studio-audit-template-20261028.md). Vorherige Hinweise
auf ausstehende Pruefungen beschreiben den damaligen Uebergabestand.
