---
title: Uebergabe zentraler Studio-Listendruck
type: reference
audience: [agent, entwickler]
owner: Codex Lead
status: abgeschlossen
last_reviewed: 2026-10-31
version: 1.0.0
description: Integrationsvertrag fuer die lokale Druckaktion der Runtime46-Listen.
---

# Zentraler Studio-Listendruck

Die NativeListPage unterstuetzt `localEffect: print` ohne commandEndpoint.
Eine funktionale Verkaufslistendefinition muss listExperience mit gueltigen
Exportspalten deklarieren; dieselbe gefilterte Gesamtmenge wird gedruckt.
Keine unfiltrierte Nachladung, keine neue Rechtefreigabe oder Fachmutation.
Fachbelegdruck mit commandEndpoint behaelt seinen Commandvertrag.

Besitz: nur NativeListPage-Druckzweig, eigener Komponententest und diese
Dokumentation. SALES-LISTS, Angebotsimport und INTAKE-WEIGHING wurden nicht
uebernommen. Die reine Druckvoraussetzung reduziert den Runtime46-Restumfang
nicht. [Vertrag und Nachweise](../../quality-assurance/studio-list-print-20261031.md).

Naechster Integrationsschritt: vorhandene Verkaufslisten-Unterclaims mit
Dateieingabe, atomarem Import und Arbeitsfokus zusammenfuehren, anschliessend
Fachparitaet und Gate E neu messen. Keine DB-/Container-/Migrationsaenderung.

Abnahme: 29 gezielte Frontendtests in 5 Dateien, Typpruefung und
Produktionsbuild gruen. ESLint und Doku-/Datenschutzchecks gruen.
