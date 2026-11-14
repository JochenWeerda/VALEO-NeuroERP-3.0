---
title: Studio-Dialogbeschreibungen
status: aktiv
last_reviewed: 2026-11-14
owner: Codex
---

# Studio-Dialogbeschreibungen

Eingabedialog, Listenbestaetigung und Leseansicht ueberlassen die Verknuepfung
zwischen `DialogContent` und `DialogDescription` dem Radix-Kontext. Feste IDs
verursachten Warnungen und Kollisionen bei mehreren Instanzen. Beschreibungen
und Bestaetigungsregeln bleiben erhalten. Andere Dialoge wurden nicht geaendert.

Gegenprobe vor Korrektur: neuer Test fuer zwei Eingabedialoge scheiterte, weil
beide dieselbe ID `action-input-beschreibung` hatten. Danach prueft er eindeutige
IDs, tatsaechlichen Beschreibungstext und das Ausbleiben der entsprechenden
Radix-Warnung. Die Bestellvorschlag-Tests pruefen zusaetzlich die zugaengliche
Beschreibung von Eingabe und Bestaetigung; der Leseansichtstest prueft seine
Beschreibung und bestehende Identitaets-/Rechtefaelle.

Gezielter Vitest-Lauf 14.11.2026: 26/26 bestanden in drei Dateien, 31,41 s,
maximal zwei Worker. Keine Beschreibung-Warnungen; der bestehende isolierte
Leseansichtstest meldet Router-Kontextwarnungen seiner Testumgebung. Keine
Browser-Gesamtabnahme, kein Build, keine Datenbank.
