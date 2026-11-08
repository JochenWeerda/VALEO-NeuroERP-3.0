---
title: Direkte YAML-Testabhaengigkeit fuer Workspace-Vertraege
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# YAML-Vertraege mit eingefrorener Installation

Die Workspace-Invarianten- und Aliasparitaetstests importieren js-yaml direkt.
Das Frontend deklariert deshalb die bereits im Lockfile vorhandene Version
4.3.2 als direkte Entwicklungsabhaengigkeit. Nur drei Importerzeilen kommen
im Lockfile hinzu; keine bestehende Paketversion wird geaendert.

Die getrennte eingefrorene Offlineinstallation war bereits mit 894 Paketen,
keinen Downloads und ohne Skriptausfuehrung erfolgreich. Installationen
anderer Worktrees bleiben unangetastet.

Vor Commit wurden Rootmanifest, Lockfile, beide unveraenderten Backportpatches
und die betroffenen Bibliotheksdateien der vorhandenen gepatchten PNPM-Pakete
gegen ihre Hashbindungen geprueft. Patch- und Bibliotheksdateien werden fuer
den Windowsvergleich auf LF normalisiert; Patchinhalt entspricht HEAD.
Ausschliesslich die Bindung an den neuen Lockhash aendert sich. Reviewdaten
und Frist 28.10.2026 bleiben unveraendert; keine Fristverlaengerung.
