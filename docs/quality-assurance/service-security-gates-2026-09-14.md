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
verwendeten Requirements-Modus und `--strict`. Lokale editable Workspace-
Distributionen selbst haben keinen oeffentlichen Advisory-Eintrag. Da pip-audit
im Requirements-Modus die Editable-Herkunft verliert, werden deren statische
PEP-621-Abhaengigkeiten aus pyproject.toml vor der vollstaendigen Aufloesung
expandiert. Dynamische oder ungueltige Metadaten blockieren; nichts wird still
ausgelassen. Das expandierte Manifest bleibt im Audit-Artefakt erhalten. Keine
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

- Audit-Runner: neun Tests gruen (Entdeckung verschachtelter/neuer Manifeste,
  Fehler-/Timeout-Verhalten, fehlende/veraltete Berichte und Befunde).
- Import-Pins: 23 Manifeste, keine fehlenden Pflichtimporte. Hinweise auf
  optionale/lazy Imports und lokale Auth-Pakete bleiben sichtbar.
- CRM-AI HTTP: vor Korrektur sieben Tests mit fuenf Teilfehlern, danach sieben
  Tests gruen; alle zehn Fachendpunkte, Health/OpenAPI und negative Eingaben.
- Vorab-Startnachweis im isolierten Testimage: echte frische PostgreSQL-Datenbank,
  fuenf Tabellen, erwartete Alembic-Revision, wiederholter Upgrade-Lauf,
  Nicht-Root-Ausfuehrung und HTTP 200; falsche Zugangsdaten verhindern Start.
- Gesamtaudit inklusive Finance-Nachlauf: alle 23 Manifeste erfasst; 16 ohne
  Befund und sieben mit Befunden. Finance-Root ist nach korrekter Expansion
  sauber; fibu-core und fibu-gateway melden reale pyasn1-/ecdsa-Befunde.
  crm-ai ist ohne Befund. Keine verbleibenden lokalen Paket-Aufloesefehler.
- Befundgruppen: services/ai (chromadb 0.5.23, click 8.2.1, pyasn1 0.4.8,
  transformers 4.46.3, ecdsa 0.19.2); crm-gdpr, crm-marketing, crm-security,
  fibu-core und fibu-gateway (pyasn1 0.4.8, ecdsa 0.19.2); dms-adapter
  (ecdsa 0.19.2). Der Scanner nennt Fixversionen fuer click, pyasn1 und
  mehrere transformers-Befunde, nicht fuer chromadb/ecdsa. Service-Pins
  bleiben im aktiven Dateibesitz von Cursor.
- Vollstaendiger Dockerfile-Neubau laeuft noch. Das
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
