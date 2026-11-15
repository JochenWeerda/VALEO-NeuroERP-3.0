---
title: Globale Theme-Initialisierung
status: lokal abgenommen
owner: Codex
last_reviewed: 2026-11-15
---

# Globale Theme-Initialisierung

Die Anmeldung mountet keine TopBar. Deshalb blieb die dort bisher erstmals
angewendete gespeicherte Dunkelwahl beim anonymen Einstieg wirkungslos.
Der zentrale Einstieg initialisiert nun dieselbe Theme-Logik vor dem ersten
React-Render. Es gibt keine abweichende Login-Darstellung oder Maskendefinition.
Gesperrter Browserspeicher faellt auf die Systempraeferenz zurueck und unterbricht
auch einen spaeteren Theme-Wechsel nicht.

Nachweis: Vor der Korrektur waren fuenf von sieben Bootstrapfaellen rot.
Nach der Korrektur bestehen acht Bootstrap-/Speicherfaelle sowie 78 bestehende
Studio-Kontrastfaelle (86 insgesamt), mit einem Vitest-Prozess.
Keine Datenbank, Migration oder Rollenveraenderung fuer diesen Slice.

Zum damaligen Testzeitpunkt noch offen: Frontend-Image neu bauen, auf beiden lokalen Ports bereitstellen und
Anmeldung in beiden Darstellungen im echten Browser erneut pruefen. Der zuvor
bereitgestellte Stand 2338578d0 enthaelt diese Korrektur noch nicht.

## Auslieferungs- und Sichtnachweis

Frontend separat erfolgreich neu gebaut und nur bestehenden Frontendcontainer
ersetzt. Chrome bestaetigt auf Port 3000 beide gespeicherten Darstellungen vor
der Anmeldung: hell Text rgb(21,26,30) auf rgb(249,250,251), dunkel Text
rgb(231,235,239) auf rgb(18,24,33). Beide Screenshots visuell kontrolliert:
Titel, Hinweis und SSO-Schaltflaeche lesbar. Keine JavaScript-Fehler.
Anonyme Studio-Navigation fuehrt weiterhin nach /login; auch Port 3001 zeigt
korrekt die Anmeldung. Screenshots und maschinenlesbarer Laufnachweis liegen
lokal unter artifacts/local-runtime-2338578-20261115/. Keine persoenlichen Daten.

Damit ist dieser Theme-Slice lokal abgenommen. Ein umfassender Kontrastnachweis
aller dynamischen Maskeninhalte wird dadurch nicht behauptet.
