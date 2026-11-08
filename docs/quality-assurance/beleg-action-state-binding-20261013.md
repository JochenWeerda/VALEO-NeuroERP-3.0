---
title: Belegaktionen an Serverzustand binden
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: Serverbedingungen wirken im gemeinsamen Renderer und direkten NativeDetail-Dispatch.
---

# Belegaktionen: Serverzustand im gemeinsamen Runtime

Die von BELEG-020 Teil 2b bereitgestellten enabledWhen-Bedingungen wurden bisher
nicht ausgewertet: UniversalNativeDetailPage uebergab keinen screenContext. Dieser
enthaelt jetzt runtime.entityData und die aufgeloesten Rechte, ohne lokale Policies,
die eine Serverentscheidung ueberschreiben koennten. actionIsEnabled sperrt bedingte
Aktionen bei fehlender Wurzel; unbedingte Aktionen bleiben erhalten.

Der NativeDetail-Wrapper prueft Recht und aktuellen Zustand vor dem direkten
Aktionshandler und nochmals vor execute. Gesperrte/fehlende/disabled Aktionen
rufen keinen ActionRuntime-Dispatch auf; der vorhandene aktionshinweis des Servers
wird angezeigt. Keine eigene Beleg-Statusmatrix oder Freigaberegel im Frontend.
Der Server bleibt fuer Mutation, Versionskonflikt, Mandant und Freigaben verantwortlich.

37 Vitest-Faelle in fuenf Dateien bestanden. Neue Faelle: fehlende/abgelehnte
Serverbedingung, positive Entscheidung, explizites disabled, direkter Aufruf ohne
Aktionszustand und sichtbarer Stornogrund. Vorherige Rechte-/Human-Form-/Vorschau-
Abbruchvertraege bleiben gruen. Tests betreffen den Clientvertrag, keine Buchung/DB.

Reale Browserpruefung mit genehmigter Einkaufsrolle und Referenzmandant: Rechnung
REF-EK-RE-STORNO geladen, Status Gegengebucht/Buchung storniert; Buchen, Freigeben und
Einkaufsgutschrift erstellen alle deaktiviert. Hinweise zu Aktionen zeigt
„Einkaufsgutschrift erstellen: Der Beleg ist storniert.“ Kein Knopf ausgeloest und
keine Geschaeftsdaten veraendert. Screenshot lokal:
artifacts/beleg-storno-actions-disabled-20261013.png.

Offen bleiben der versionierte DocFlow-/Approval-Command-Adapter, Eingaben und
Ergebnisnormalisierung, positive freigabepflichtige Abläufe, alle Belegvarianten,
Lageransicht ohne Preise und die vollstaendige systemweite MCP-Schreibabnahme.
Die Screenshotabnahme dieses stornierten Belegs ist keine Freigabe zum Buchen.
