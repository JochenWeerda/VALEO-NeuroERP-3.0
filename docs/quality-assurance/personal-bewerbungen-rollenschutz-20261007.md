---
title: Bewerbungs-API — Rollenschutz
type: reference
audience: [entwickler, qa, sicherheit]
owner: Codex
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
description: Rollenvertrag fuer alle Bewerbungs-, Aufbewahrungs- und Einwilligungswege.
---

# Bewerbungs-API — Rollenschutz

Alle 16 Wege in personal_bewerbungen.py verlangen jetzt eine passende Rolle
ueber die vorhandene app.auth.deps.require_roles-Factory. Token und Mandant
allein reichen nicht. Die Fachrollen folgen der vorhandenen
DOMAIN_LESEN/BEARBEITEN/ADMIN-Konvention; zuvor gab es keine Personalrollen.
Diese Entscheidung ist im Workboard vor Umsetzung ausdruecklich festgehalten.

| Zugriff | Rollen | Wege |
|---|---|---|
| Lesen | PERSONAL_LESEN, PERSONAL_BEARBEITEN, PERSONAL_ADMIN, admin, manager | alle acht GET-Wege |
| Bearbeiten | PERSONAL_BEARBEITEN, PERSONAL_ADMIN, admin, manager | Bewerbung erfassen, Stufe aendern, Einwilligung erteilen/widerrufen |
| Verwalten | PERSONAL_ADMIN, admin | Aufbewahrung setzen, endgueltiger Loeschlauf, Bewerbung loeschen, Fassung anlegen |

manager erhaelt keine Verwaltungsrechte. Fehlende Rollen, user und fachfremde
FUTTERMITTEL_ADMIN-Rollen werden abgewiesen. Der interne Widerruf verlangt
dieselbe Bearbeitungsrolle wie die Erteilung und weiterhin keinen Pflichtbody.
Ein Bewerber-Selbstwiderruf und rollenbezogene Maskensteuerung sind damit
nicht implementiert. Echte JWTs muessen die gewuenschten Fachrollen im
bestehenden roles-Claim enthalten; der bestehende Dev-Token ist bereits admin.

## Abnahme

161 neue Dispatch-Vertraege: Matrix aller 16 Wege mit acht Rollenfaellen,
fehlendem/ungueltigem Token und exakter Vollstaendigkeit des Routenkatalogs.
Unerlaubte Zugriffe enden vor dem Datenbankzugriff; erlaubte Rollen erreichen
eine explizite Testgrenze. Kein Datenbankzugriff in diesen Tests.

163 vorhandene Bewerbungs-, Loeschlauf-, Einwilligungs- und Fassungsvertraege
auf gemeinsamem valeo_probe bestanden. Zusammen 324 Tests ohne Skip, Exit 0
in 65,99 s. Eigene Testdatensaetze und vorhandene Fixtures; keine neue
Datenbank, Dockerinstanz, Migration oder gemeinsame Ruecksetzung.

Strukturvergleich bestaetigt unveraenderte Handlerkoerper, Signaturen,
Mandantenfilter und vorherige Decorator-Argumente. Vollstaendige main.app
prueft alle 16 geschuetzten Handler als tatsaechliche erste FULL-Matches.
3103 API-Pfade/Methoden, alle Response-/Request-/Parametervertraege und alle
DTO-Schemata exakt erhalten; render(build_spec()) kanonisch. 41 bereits
vorhandene Routerkonflikte bleiben offen. Artefakte stammen aus committed
cf87267da plus einzigem eigenen Backend-Hunk; fremde Arbeitsbaumfassungen
werden nicht veroeffentlicht.

## Diagnose und Grenzen

Erster eingeschraenkter Teststart hing; nur dessen eindeutig eigener
Pytest-Prozess wurde beendet. 161 Assertions bestanden anschliessend,
die globale Coverage-Konfiguration meldete fuer diese Teilsuite 7 statt 60
Prozent. Die gezielte Endabnahme laeuft ausdruecklich ohne globale Coverage;
der umfassende CI-Coverage-Gate bleibt unveraendert. Ein lokaler Python-3.11.0-
Absturz waehrend des zeitgesteuerten Faulthandler-Dumps beim grossen app.main-
Import wurde ohne diesen Diagnose-Timer erneut geprueft; die Endabnahme
besteht. Bestehende Starlette/httpx-Deprecation bleibt ein separater Befund.

GitHub-Abnahme steht aus. Frontend-/Security-/Smoke-Befunde bleiben getrennt;
dieser Slice schliesst ausschliesslich den serverseitigen Personal-Rollenschutz.
