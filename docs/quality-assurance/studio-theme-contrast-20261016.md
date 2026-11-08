---
title: Studio und zentrale Masken mit Theme-Kontrastvertraegen
type: reference
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Themeuebernahme und Lesbarkeit

Studio-Vorschauen verwenden UniversalMaskRenderer und die globalen Theme-Tokens. Es werden keine eigenen Farben je importierter Maske gespeichert. Dunkelansicht wird ueber useTheme am Dokument gesetzt und wie bisher gespeichert.

Die neue deterministische Suite liest die tatsaechlichen CSS-Farbdefinitionen und prueft sechs Paletten: Basis hell/dunkel, Warehouse, Meridian dunkel und Terra hell/dunkel. Normale Text-/Flaechenpaare einschliesslich Fehlertext muessen mindestens 4,5:1 erreichen; funktionale Eingabekonturen und Fokusfarbe mindestens 3:1. Dekorative Tabellenlinien werden nicht pauschal verdunkelt. Diese Palettepruefung laeuft als regulaerer Vitest-Vertrag und erfordert keine Datenbank.

Vorher wurden echte Unterschreitungen gemessen: unter anderem weisse Schrift auf der hellen Fehlerfarbe, Dunkelmodus-Schaltflaechen und kaum sichtbare Eingabekonturen. Spezifischere Meridian-/Terra-Regeln werden gesondert erfasst; die Browserpruefung hatte gezeigt, dass die allgemeinen .dark-Tokens allein den tatsaechlichen Meridian-Dunkelmodus nicht abbilden.

Korrektur ausschliesslich in zentralen Tokens; Checkbox verwendet fuer Kontur, Auswahl und Fokus die semantischen Eingabe-/Primaer-/Fokustokens statt fester Slatefarben. Fremde Schrift-/Typografiestufen in der physischen index.css werden nicht integriert.

## Nachweis und Grenzen

92 Kontrastfaelle bestanden: 78 neue Theme-Paare plus 14 bestehende Kachelvertraege. Reale lokale Studio-Anmeldung mit synthetischer Testkennung, Ausgangsfassung Duenger uebernommen und erneut aus der Liste geoeffnet. Vorschau, Pflichtbeschriftung, leere Eingaben, Fokus und Historie in Hell-/Dunkelansicht kontrolliert; kein Geschaeftsbeleg veraendert, keine Freigabe erteilt. Lokale Screenshots: artifacts/studio-theme-acceptance/studio-dark.jpg und studio-light.jpg.

Die rechnerische Palettepruefung ersetzt keine vollstaendige WCAG-Abnahme jeder Maske. Ueberlagerungen, Bilder, Transparenz, Hover-/Fehler-/Ladezustaende, native Browserauswahllisten, Zoom und alle Bildschirmgroessen benoetigen weiterhin konkrete Browserabnahme. Deaktivierte Elemente werden nicht als aktive Bedienelemente bewertet. Die vollstaendige Ablösung der bisherigen Belegmasken ist hiervon unabhaengig und weiterhin in Arbeit.
