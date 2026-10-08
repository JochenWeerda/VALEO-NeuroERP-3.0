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

Die übrigen 20 untypisierten Routen sind bestehender Restbestand und werden
durch diesen Meilenstein nicht als behoben ausgegeben. Maskenvertrag,
CRM-Smoke, Dependency-Security und XBRL/ERiC bleiben bis zu ihrer eigenen
Abnahme offen. Kein Datenbankzugriff für diese Tests, kein Reset, keine neue DB.

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
ist geöffnet und die Projektbegründung vorbereitet. Pflicht-Kontaktdaten
wurden angefragt; nichts abgesendet, keine Lizenz angenommen. Laut
[ELSTER](https://www.elster.de/elsterweb/infoseite/entwickler) folgt eine
Herstellerprüfung und Einrichtung des Zugangs innerhalb einiger Tage per
E-Mail. SDK und echte Empfangsquittung bleiben externe Voraussetzungen.
