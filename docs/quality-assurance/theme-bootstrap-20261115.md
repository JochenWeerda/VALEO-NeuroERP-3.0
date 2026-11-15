---
title: Globale Theme-Initialisierung
status: in arbeit
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

Noch offen: Frontend-Image neu bauen, auf beiden lokalen Ports bereitstellen und
Anmeldung in beiden Darstellungen im echten Browser erneut pruefen. Der zuvor
bereitgestellte Stand 2338578d0 enthaelt diese Korrektur noch nicht.
