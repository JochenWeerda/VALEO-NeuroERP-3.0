---
title: Arbeitsplatz-Einstieg und zentrale Designkaskade
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-16
version: 1.0.0
description: Ruhiger Start, progressive Studio-Komposition und reale Kontrastnachweise.
---

# Arbeitsplatz-Einstieg

Der Nutzer fand den Start mit internen Reasoncodes, UUIDs, doppelten Cockpits,
vollstaendiger Disposition und langen Betriebslisten unbenutzbar. Der bestehende
Studio-Kompositionshost bietet eingebettet jetzt zunaechst zugaengliche
Oeffnen-Schaltflaechen; die echten registrierten Komponenten werden erst dann
gemountet. Studio selbst behaelt seine direkte Vorschau. Ansichts-Pins und
Start-Fix bleiben ueber Arbeitsbereich anpassen erreichbar. Das native
Rollen-Cockpit bleibt ueber einen getrennten Einstieg verfuegbar.

Die vorhandenen Fachlinks, Navigation und Autorisierung bleiben erhalten.
Priorisierte Aufgaben erklaeren sich mit menschlichen Texten, gruppierte
Kontraktaufgaben behalten alle Ziele. Geschaeftliche Referenzen werden erhalten,
nur technische UUID-Praefixe werden ersetzt. Agrarprozessdetails liegen unter
einem explizit oeffenbaren Ueberblick. Gleiche Betriebszustandsanzeigen werden
mit ihrer Anzahl zusammengefasst, Eintraege ohne Datum/Detail bleiben getrennt.
Zunaechst fuenf Gruppen, weitere bewusst aufklappen. Keine Geschaeftsdaten
werden geloescht oder erfunden; nicht verfuegbare Daten bleiben als Fehler
kenntlich und werden nicht als leere Erfolge dargestellt.

## Zentraler Befund

Der erste reale Komponentenlauf zeigte trotz gesetzter Klassen nur 16px
Seitentitel, leere --text-2xl/--radius und einen unentscheidbaren kbd-Kontrast.
PostCSS registrierte base vor theme, weil Token-Imports vorher standen.
Emittierte Theme-Selbstreferenzen gewannen dadurch gegen die Basiswerte.
Die explizite Layer-Reihenfolge vor den Imports behebt die Ursache zentral.
Keine individuellen Style-Ausnahmen oder Abschwaechung der Kontrastpruefung.

## Nachweise

67 Verhaltenstests in sieben betroffenen Dateien bestanden, darunter
Studio-Preview, bewusstes Slot-Mounten, Pin-/Sortierung, Agrar-Readmodels,
Fachlinks und Informationsverlust-freie Darstellung. Keine neuen Datenbanken,
Container oder lokalen Fachtest-Schreibdaten.

Der isolierte Browserpruefstand verwendet die echte Startseite mit produktiven
Styles und Komponenten, aber ausschliesslich synthetischen Read-Daten und
blockierten Schreibmethoden. Frische Chrome-Kontexte: 1366x768, 1440x900 und
1920x1080, jeweils hell/dunkel. Vor der zentralen Korrektur sechs rote
Kontrastfaelle; danach sechs bestanden mit nichtleeren Designwerten, ohne
horizontales Ueberlaufen, Laufzeitfehler oder externe Anfragen. Vollstaendige
Axe-Berichte samt Incomplete, Screenshots und Report liegen in
artifacts/workspace-home-visual-20261116 (ignoriert). Das belegt die
Komposition und zentrale Darstellung; keine angemeldete reale Fachketten-
oder Rechte-Gesamtfreigabe. Persoenliche Konten wurden nicht verwendet.

Vollstaendige Frontend-Typpruefung bestanden. Image-Aktivierung folgt im Betriebsnachlauf unten.
