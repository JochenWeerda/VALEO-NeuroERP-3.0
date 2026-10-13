---
title: Finale Maskenfehler sichtbar halten
type: reference
audience: [agent, entwickler]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Finale Maskenfehler sichtbar halten

Nach finalem execute loeschte resetDialogs sowohl Serverfehler als auch Feldvalidierungen. Dadurch verschwand eine Ablehnung beim Abschluss des Dialogablaufs.

UniversalNativeDetailPage schliesst nun den Dialogzustand vor execute. Abbruch setzt weiterhin die Meldungen zurueck; die finale Ausfuehrung behaelt ihre Fehlermeldungen. Im Begruendungsweg werden Aktion und Begruendung vor dem Schliessen gesichert.

Abnahme: 13 Vitest-Faelle in native-detail-preview.test.tsx und action-state.test.ts bestanden. Finale Serverfehler und Feldvalidierungen jeweils mit und ohne Begruendung, gesperrte direkte Aktionen und fehlgeschlagene Vorschau sind abgedeckt. HTTP-Ausfuehrung gemockt; keine Geschaeftsdaten veraendert. DocFlow-Command- und Approval-Adapter bleiben offen.
