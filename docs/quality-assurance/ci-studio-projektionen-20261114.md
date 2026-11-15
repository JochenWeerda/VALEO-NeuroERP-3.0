---
title: CI-Abgleich der Studio-Projektionen
status: aktiv
last_reviewed: 2026-11-14
---

# Studio-Projektionen und Identitaet

Die Generatoren fuer Maskenaktionen und Listenrouten wurden nach der
Sorten- und Zertifikatskorrektur regulaer ausgefuehrt. Die neue Sortenmaske
`agrar/saatgut/sorte` hat die kanonische Identitaet `name`; die explizite
Meridian-Erwartung nennt sie jetzt. Die Identitaets-Altlastliste wurde nicht
veraendert.

Der Aktionskatalog enthaelt 797 Aktionen fuer 405 Masken. Die Listenprojektion
hat 475 Routen; der Sortenstamm ist enthalten. `zertifikate/neu` steht jetzt
unter 57 Masken ohne Route: Die bisherige Zuordnung `/zertifikate` zeigte nach
der reparierten Seitenbindung tatsaechlich auf die Zertifikatsliste, nicht auf
die Neuanlage. Dieser offene Routenbefund ist sichtbar und keine funktionale
Neuanlageabnahme.

Gezielte datenbankfreie Pruefung mit `--noconftest -o addopts=''` und ohne
Plugin-Autoload: 10 Tests bestanden, darunter die drei gemeldeten CI-Faelle,
der gesamte Aktionskatalogtest und die Navigationsunitdatei. Andere Tests der
Meridian-Datei wurden wegen ihrer Datenbankfixtures nicht ausgefuehrt. Der
Windows-Python-Interpreter gab beim Beenden nach erfolgreichem Lauf eine
`pyreadline3`-Console-Meldung aus; das Testergebnis war Exit 0.
