---
title: Service-Security-Gates und CRM-AI-Betriebsabnahme
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-14
---

# Service-Security-Gates und CRM-AI-Betriebsabnahme

## Umfang

Slice `SERVICE-SECURITY-GATES-20260914` schliesst die fehlende automatische
Abdeckung der 23 Service-Manifeste und prueft die bestehende CRM-AI-Simulation
bis zum Datenbank-/Serverstart. Die von Cursor gelieferten FastAPI-/Starlette-
Pins, PaginatedResponse und Depends-Korrekturen werden nicht neu implementiert.
Die aktiven Manifest-Slices bleiben bei Cursor; diese Abnahme aendert keine Pins.

## Gate

`.github/workflows/service-security.yml` entdeckt alle `services/**/requirements.txt`
dynamisch, auch verschachtelte Finance-Dienste. Der vorhandene Import-Pin-Check
ist blockierend eingebunden. Jede Audit-Matrixzelle loest das originale Manifest
mit transitiven Abhaengigkeiten auf und fuehrt pip-audit 2.10.1 aus. Arbeitsverzeichnis
ist der Dienstordner, damit lokale editable Finance-Pakete korrekt aufgeloest werden.

Die [pip-audit-Dokumentation](https://github.com/pypa/pip-audit) beschreibt den
verwendeten Requirements-Modus, `--strict` und `--skip-editable`. Lokale editable
Workspace-Distributionen selbst haben keinen oeffentlichen Advisory-Eintrag;
ihre aufgeloesten Drittanbieter-Abhaengigkeiten werden mitgeprueft. Keine
`--no-deps`-Verkuerzung, keine neuen Ignore-Eintraege. Jeder Befund blockiert,
auch ohne Fixversion. Timeout, fehlender/leerer Bericht und Sammelfehler
blockieren ebenfalls. Matrixzellen laufen trotz anderer Fehler weiter;
JSON-Berichte, Logs und Status werden immer als Artefakte gesichert.

Der zusammenfassende Job verlangt Erfolg aller drei Bereiche: Inventar,
Dependency-Audit und CRM-AI-Imageabnahme. Die bestehende Branch-Protection wird
nicht geaendert; der neue Job muss dort gegebenenfalls separat als Pflichtcheck
konfiguriert werden. Bestehende Root-Gates bleiben bestehen.

## CRM-AI-Korrekturen

- Batch- und Trainingsantworten hatten ungueltige UUID-Werte; die HTTP-Aufrufe
  scheiterten trotz erfolgreichem Healthcheck. Nun schema-konforme UUIDs.
- CLV-Batches meldeten Erfolge ohne Ergebnisse. Nun dieselben simulierten
  CLV-Werte wie im Einzelpfad; unbekannte Vorhersagetypen ergeben HTTP 400.
- Alembic erhielt keine URL aus der Umgebung. Nun wird DATABASE_URL verwendet,
  einschliesslich korrekter Behandlung prozentkodierter Passwortzeichen.
- Die initiale Migration erzeugte Enum-Typen explizit und erneut implizit bei
  Tabellenanlage. Die drei Spaltentypen verwenden die zuvor erzeugten Typen.
  Es werden keine bestehenden Tabellen oder Daten umgeschrieben.
- Der Entrypoint verschwieg Migrationsfehler. Nun verhindert jeder Fehler den
  Serverstart; Uvicorn startet ohne Entwicklungs-Reload.

## Nachweise

- Audit-Runner: sieben Tests gruen (Entdeckung verschachtelter/neuer Manifeste,
  Fehler-/Timeout-Verhalten, fehlende/veraltete Berichte und Befunde).
- Import-Pins: 23 Manifeste, keine fehlenden Pflichtimporte. Hinweise auf
  optionale/lazy Imports und lokale Auth-Pakete bleiben sichtbar.
- CRM-AI HTTP: vor Korrektur sieben Tests mit fuenf Teilfehlern, danach sieben
  Tests gruen; alle zehn Fachendpunkte, Health/OpenAPI und negative Eingaben.
- Vorab-Startnachweis im isolierten Testimage: echte frische PostgreSQL-Datenbank,
  fuenf Tabellen, erwartete Alembic-Revision, wiederholter Upgrade-Lauf,
  Nicht-Root-Ausfuehrung und HTTP 200; falsche Zugangsdaten verhindern Start.
- Gesamtaudit-Zwischenstand: 14 von 23 Manifesten geprueft, zehn ohne Befund;
  ai, crm-gdpr, crm-marketing und crm-security mit Befunden. crm-ai ohne Befund.
- Vollstaendiger Dockerfile-Neubau und restliche Audits laufen noch. Das
  gestartete Build-Snapshot liegt vor den API-/Migrationsfixes; nach Abschluss
  werden die Code-Layer aktualisiert und beide Image-Pruefer erneut ausgefuehrt.

## Grenzen

CRM-AI bleibt eine Simulation, kein ausgeliefertes trainiertes Modell und kein
persistenter Trainings-/Feedback-Dienst. Keine Aussage ueber produktive
Mandanten-/Auth-Freigabe; kein Deployment und keine produktive Migration.
Der Gate darf bei echten verbliebenen Advisories rot sein. Die technische
Fertigstellung der Pruefung ist keine Behauptung, alle Dependencies seien frei
von Schwachstellen.

Lokale Nachweise: `artifacts/service-security/`, `crm-ai-contracts-before.log`,
`crm-ai-contracts-after.log`, `crm-ai-startup-test.log` und
`crm-ai-security-build.log` unter `artifacts/`.
