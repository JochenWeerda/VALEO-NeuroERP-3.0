---
title: CI-Vertragsreparaturen vom 8. Oktober 2026
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-08
version: 1.0.0
---

# CI-Vertragsreparaturen

## Meilenstein: OpenAPI und Secret-Scan

Ausgangsstand `5ca1039aa`: zwei fehlende OpenAPI-Beschreibungen und 22 statt
maximal 20 als untypisiert gezählte Routen. Die beiden kanonischen Lead-Aliase
ohne abschließenden Slash erhalten dieselben Beschreibungen wie ihre
Slash-Varianten. Zwei eBilanz-Dekoratoren enthielten bereits response_model,
jedoch nach einer verschachtelten Depends-Klammer, an der der vorhandene
Scanner seine Erkennung beendet. Das Modell steht jetzt vor den Dependencies;
Modell, Rollenprüfung und Laufzeitverhalten bleiben identisch.

GitHub Quality Gate `37726234233`, Job `113145315162`, meldete genau einen
generic-api-key-Fund in `tests/test_business_day_service_boundaries.py:80`.
Die Zeile enthielt ausschließlich künstliche SimpleNamespace-Werte für eine
Papier-Einwilligung. Aufteilung der Argumente beseitigt den Fehlalarm, ohne
Allowlist oder Regeln zu erweitern. Der Workflow verwendet bereits `--redact`;
Schlüsselwerte werden weder hier dokumentiert noch in Diagnoseausgaben gezeigt.

Abnahme auf isolierter HEAD-Quelle mit ausschließlich diesen Reparaturen:

- OpenAPI-Doku 3590/3590, null fehlende Beschreibungen, Schwelle weiterhin 0.
- Response-Model-Gate 20 untypisierte Routen, Schwelle weiterhin 20.
- 24 bestehende Kalender-/Fristverträge bestanden (2,44 Sekunden).
- Offizielles Gitleaks 8.30.1, HEAD-Snapshot plus korrigiertes Fixture:
  62,66 MB geprüft, null Funde, Exit 0. Kein zusätzlicher Docker-Container.
- OpenAPI zweimal deterministisch generiert: 3104 Pfade erhalten,
  ausschließlich die Beschreibung von `/api/v1/crm/leads` geändert.

Die damals noch gezählten 20 Routen wurden im folgenden Meilenstein einzeln
untersucht. Maskenvertrag, CRM-Smoke, Dependency-Security und XBRL/ERiC bleiben
bis zu ihrer eigenen Abnahme offen. Kein Datenbankzugriff für diese Tests,
kein Reset, keine neue DB.

## Meilenstein: Antwortvertrags-Gate und Manifest-Konsistenz

Der Regex-Scanner meldete neun Studio-Routen mit bereits von FastAPI aus dem
Returntyp abgeleiteten Modellen, sechs Policy-Dekoratoren mit verschachtelten
Dependencies sowie fünf Datei-/Text-/204-Antworten als untypisiert. Die
AST-Erkennung prüft jetzt jeden Dekorator einzeln. Importierte Response-Aliase,
typisierte Rückgaben und HTTP-Antworten ohne Body werden korrekt erkannt;
untypisierte JSON-Routen, Any/object/None-Rückgaben ohne expliziten Vertrag und
Syntaxfehler bleiben Fehler. Eine explizite response_model=None-Deklaration
behält den bisherigen technischen Ausnahmevertrag, gilt aber nur für ihre Route.
Kommentare und Ausnahmen benachbarter Routen können keine Lücken mehr verdecken.
Keine Endpoint-Modelle durch None oder Any ersetzt, kein Antwortinhalt verändert.

Abnahme: 3590/3590 Antwortverträge, null Lücken. Default und CI-Schwelle von
historisch 916 beziehungsweise 20 auf **0** verschärft. Tatsächliche FastAPI-
Registrierung bestätigt 9/9 Studio- und 8/8 Policy-Modelle. 15 neue Parser-
Regressionen plus bestehende Policy-/Studio-Verträge: 45 Tests grün (2,45 s).
OpenAPI-Beschreibungen weiterhin 3590/3590, null fehlend.

Neun direkte Manifeste deklarieren jetzt dieselben reparierten Versionen wie
die seit 07.10.2026 vorhandenen Overrides: i18next-http-backend 4.0.2 im
Frontend und instrumentation-pg 0.73.0 in acht Domänen. Der Lockfile bleibt
byteidentisch; frozen/offline-Prüfung aller 36 Workspaces bestanden. Sechs
bestehende Tests auf tatsächlichen Herstellerpaketen grün (4,54 s).
Production-Audit aller 2053 aufgelösten Abhängigkeiten: null Critical/Moderate/Low,
zwei High (node-forge und braces); Audit weiterhin Exit 1. Keine neue Ausnahme.
[node-forge](https://github.com/advisories/GHSA-86w9-cpqp-85rv) und
[braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) nennen am 08.10.2026
weiterhin keinen Herstellerfix. Versionsbasierte weitere Dependabot-Meldungen
sind keine Abnahme der tatsächlich gepatchten Laufzeit; Graph-Refresh ausstehend.

GitHub-Smoke des Masken-Meilensteins c59df8391, Lauf 37730263363: **alle fünf
Domänen einschließlich CRM erfolgreich**. OpenAPI, PostgreSQL, kritische E2E
und Doku ebenfalls erfolgreich. Quality-Lauf 37730263705 durch nachfolgenden
Push abgebrochen; das ist keine vollständige Quality-Abnahme.
Neun Improvement-Checks im geteilten Baum wurden wegen gleichzeitiger fremder
Änderungen nicht als Gesamtabnahme gewertet. Kalender-/Baseline-Drift betrifft
einkauf_lieferschein.py und den aktiven fremden Folgefund-Slice; kein Blind-Revert
oder Baseline-Anhebung. Eigene Parser-, Manifest- und Runtime-Abnahme isoliert.

## Meilenstein: native Lead-Anlage und Maskenberechtigungen

Der CRM-Smoke rief `/crm/lead/new` auf. Der Detail-Lader behandelte `new`
als vorhandene ID und erhielt 404. Der zentrale NativeDetail-Einstieg delegiert
`new` und `neu` jetzt an eine gemeinsame NativeCreate-Komponente. Der
ScreenDefinition-Vertrag deklariert den kanonischen POST `/api/v1/crm/leads`,
Defaults und die Detailroute. RenderPlan, UniversalMaskRenderer und
UniversalFormState bleiben die zentrale Kette; keine individuelle Ersatzmaske.
Ungespeicherte Datensätze laden keine Detailregister. Das Formular sendet nur
editierbare deklarierte Felder; Fehler bleiben sichtbar, Navigation erfolgt erst
nach einer echten Antwort mit ID. Mandant und Berechtigungen prüft der Server.

Die acht Logistik-Aktionen tragen in Backend und Frontend `logistics:read`
beziehungsweise `logistics:write`. Zentraler Capture-Host, NativeDetail und die
beiden Logistik-Seiten geben aus dem Auth-Kontext projizierte Rechte an Compiler,
Dispatcher und Renderer weiter. Schema-Metadaten verleihen keine Rechte.
Administratoren und die bestehenden CRM-Schreibrollen werden berücksichtigt;
unberechtigte Anlage wird gesperrt. Diese UI-Projektion ersetzt keine serverseitige
Autorisierung und behauptet keine neue Logistik-API-Sicherheitsabnahme.

Abnahme auf isolierter Quelle von `83a32d91f` plus eigenen Masken-Hunks:

- 834 bestehende Backend-Vertragstests bestanden (8,29 Sekunden).
- 12 React-Verträge für Neuanlage, Speicherfehler, Rechte und Detail-Ladezustände
  bestanden. Tatsächlicher Renderer und Form-State, kein Ersatzformular.
- Bestehender Chromium-Smoke zur Lead-Neuanlage unverändert bestanden;
  tatsächlicher Backend-ScreenDefinition-Vertrag im lokalen HTTP-Fixture.
- Command-Inventar: 99 native ScreenDefinitions, null bekannte Lücken.
- Godfile-Ratsche unverändert bestanden; keine Baseline angehoben.
- Keine neue Datenbank, kein Container, kein Reset. Windows-Prüfungen benötigen
  für lokale Sockets die üblichen Dateirechte außerhalb der Sandbox.

## ELSTER und Open-Source-Recherche

[Arelle](https://github.com/Arelle/Arelle) stellt einen XBRL-Prozessor mit
Python-API bereit; der Kern steht unter
[Apache-2.0](https://github.com/Arelle/Arelle/blob/master/LICENSE.md).
[Erica](https://github.com/digitalservicebund/erica) und
[PyEric](https://github.com/tech4germany/steuerlotse) demonstrieren ERiC-Anbindung.
Wrapper ersetzen die offizielle Bibliothek nicht. Einbindung wird erst nach
Prüfung der tatsächlichen Schnittstellen und aktuellen Version festgelegt.

Der Nutzer hat am 08.10.2026 die Entwicklerregistrierung und elektronische
Lizenzannahme beauftragt. Das
[Registrierungsformular](https://www.elster.de/elsterweb/registrierung-entwickler/form)
hat der Nutzer selbst abgesendet; die Versandbestätigung wurde am 08.10.2026
als echtes PDF über „PDF speichern“ heruntergeladen und zusammen mit einem
Browser-Screenshot ausschließlich unter dem ignorierten lokalen
`artifacts/elster/` gesichert. Personenbezogene Formulardaten werden nicht
versioniert. Der ERiC-Bereich leitet zur Entwickleranmeldung weiter;
freigeschaltete Zugangsdaten liegen noch nicht vor. Kein Lizenzvertrag wurde
angezeigt oder angenommen, kein SDK heruntergeladen oder als eingebunden
ausgegeben. Laut
[ELSTER](https://www.elster.de/elsterweb/infoseite/entwickler) folgt eine
Herstellerprüfung und Einrichtung des Zugangs innerhalb einiger Tage per
E-Mail. SDK und echte Empfangsquittung bleiben externe Voraussetzungen.
