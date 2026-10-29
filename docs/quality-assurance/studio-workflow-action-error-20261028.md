---
title: Flow-Spine-Aktion – Navigation nach fehlgeschlagenem Aufruf
type: verification
audience: [entwickler, agent, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: Gezielter Verhaltensnachweis für die Fehlerbehandlung von Prozessaktionen.
---

# Prozessaktion: Fehler verhindert Navigation

`FlowSpineWorkspace.handleAction` beendet die Aktion nach fehlgeschlagenem POST und zeigt weiterhin die bestehende Fehlermeldung. Nach erfolgreichem POST öffnet sie das Ziel; Aktionen ohne API-Pfad navigieren unverändert direkt. Rechte, Endpunkte und Entscheidungen sind unverändert. Dies ist eine isolierte Fehlerkorrektur und keine Studio-Migration der Prozessräume.

Der gezielte Komponentenlauf `flow-spine-order-to-cash.test.tsx` prüft den echten Workspace mit simuliertem API-Fehler, erfolgreichem POST und reinem Link sowie den bestehenden Seitenfall: **4 Tests bestanden**. Keine Datenbank, kein vollständiger Build oder vollständiger Typprüfungslauf für diesen Schritt.
