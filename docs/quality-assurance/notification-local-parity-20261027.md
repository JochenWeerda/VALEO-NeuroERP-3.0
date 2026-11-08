---
title: Studio Benachrichtigungsaktion
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Gezielte Reparatur mit dokumentierten Abnahmegrenzen.
---

# Benachrichtigungen: lokaler Lesestatus (2026-10-27)

Die ScreenDefinition deklariert eine lokale Zeilenaktion. Der zentrale Renderer projiziert das Feld nur fuer die gewaehlte stabile Zeilen-ID in seinem fluechtigen Zustand. Beim Verlassen der Maske geht dieser Zustand verloren; die Maske weist darauf hin. Es gibt keinen Server-Write und keine behauptete Persistenz. Zeilen ohne stabile ID werden nicht lokal veraendert.

Gezielter Vitest: `crm-fibu-logistik-uix.test.ts -t "stellt Benachrichtigungen lokal als gelesen"`: 1 bestanden, 28 andere Faelle durch Filter uebersprungen. Zwei ungelesene Zeilen, Touch-Ziel, isolierter Klick, kein Request und Reset durch Unmount/Neumount geprueft. Keine Gesamt-CI-Abnahme.
