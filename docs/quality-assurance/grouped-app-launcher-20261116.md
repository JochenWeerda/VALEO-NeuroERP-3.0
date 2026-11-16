---
title: Funktional gruppierter App-Launcher
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-16
version: 1.0.0
description: Launcher statt Dashboard als Standardstart, mit erhaltenen Studio-Arbeitsbereichen.
---

# Gruppierter App-Launcher

Die vom Nutzer gezeigten Bilder sind Layoutreferenzen. Deren Beispielzahlen,
Statusanzeigen und Beschreibungstexte sind keine echten VALEO-Daten und wurden
nicht als Funktion oder Telemetrie uebernommen.

Die bestehende LaunchpadBoard-Komponente bietet eine Launcher-Praesentation:
alle vorhandenen sichtbaren Gruppen mit kompakten Symbolstartern, Labels,
Direktlinks und lokalem Filter ueber Gruppen, Stichworte und Namen. Symbole
kommen aus der kanonischen Navigation, unbekannte Symbole verwenden ein
neutrales Raster. Themefarben bleiben zentral. Doppelte Zielrouten pro Gruppe
werden erst nach dem Suchabgleich entfernt, damit auch Aliasbegriffe das
richtige Ziel finden. Keine neuen Fachrouten oder Berechtigungen.

Der bisherige Anpassungseditor arbeitet weiterhin mit denselben persoenlichen
Overlays. Die operative Arbeitsuebersicht bleibt bewusst oeffenbar; bei
Rueckkehr zum Launcher wird sie demountet. Der Standardstart mountet keine
Prioritaets-, Agrar-, Inbox- oder Dispositionsabfragen. Das ist mit einem
negativen API-Aufrufnachweis getestet.

## Geprueft

32 Tests in fuenf betroffenen Dateien bestanden, darunter echte Zielrouten,
Suche, Leerzustand, Gruppierung, Anpassungsmodus, Moduswechsel und die
unveraenderte operative Komposition. Der ergaenzte Such-Aliasfall wurde danach
gezielt erneut geprueft. Vollstaendige Frontend-Typpruefung bestanden.

Sechs frische synthetische Chrome-Komponentenansichten (1366x768, 1440x900,
1920x1080, jeweils hell/dunkel) bestanden: keine Kontrastverletzung oder
unentscheidbare Kontraststelle, keine Laufzeitfehler, externen Anfragen oder
horizontalen Ueberlaeufe. Echte Komponenten und Styles, keine persoenliche
Anmeldung oder Datenbank. Evidenz: artifacts/app-launcher-visual-20261116,
ignoriert. Beispielkatalog im Harness zeigt 101 Einstiege; dies ist keine
Behauptung, alle Masken-/Fachketten seien damit abgenommen.

Lokale Image-Aktivierung folgt im Betriebsnachlauf. Keine Datenbanken,
Migrationen oder neuen Container fuer diese Abnahme.
