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

Nutzerpraezisierung: Gruppentitel zeigen ausschliesslich den funktionalen Gruppennamen, ohne wiederholten Oberbereich wie Handel & CRM. Der Oberbereich bleibt im Suchindex und semantischen Abschnittskontext erhalten.

## Funktionsbezogene Symbole

Auf Nutzerwunsch zentrale Zuordnung nach kanonischen Katalogidentitaeten:
Angebot/Anlage, Auftrag, Lieferung und Rechnung verwenden unterschiedliche
Symbole; weitere fuer Waage, Lager, Labor, Kontrakte, Produktion und Finanzen.
Vorhandene Navigationssymbole bleiben Fallback fuer neue Eintraege, erst danach
das neutrale Raster. Keine heuristische Rollen- oder Befehlsentscheidung.
34 Tests des zusammenhaengenden Launcher-Satzes, volle Typpruefung und sechs
finale Theme-/Desktopansichten nach dieser Ergaenzung bestanden.
Der erste eigene Build wurde fuer die Nutzerpraezisierungen gezielt abgebrochen;
keine parallelen oder fremden Builds beendet. Finale Quelle folgt im Nachlauf.

## Lokal bereitgestellt

Finale Quelle745cca250, Frontendimage
sha256:b72327848a9b21ed8020fe0eaac0d07ec51f7915abca838e20d4cb50f1253d22.
Ausschliesslich den vorhandenen Frontend-Container ersetzt. Backend,
Frontend und Keycloak healthy; keine Migration oder Backend-Neustart.
Anschliessende echte SSO-Klicks auf3000/3001 bestanden: Discovery200,
sichtbare Provider-Anmeldung und null fehlgeschlagene Browseranfragen.
Keine persoenlichen Zugangsdaten eingegeben.

Der Launcher selbst ist mit den echten Komponenten synthetisch visuell und
funktional geprueft; eine persoenliche ERP-Anmeldung wird daraus nicht
abgeleitet. PR149 baut auf148 und147 auf. Lokal aktiv und nach GitHub
gepusht; main-/develop-Integration steht separat aus.
