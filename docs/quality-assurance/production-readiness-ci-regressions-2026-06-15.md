# Production-Readiness CI-Regressions 2026-06-15

## Befunde

Die externen Prueferprofile wurden auf die GitHub-Laufzeitfehler angewendet.
Dabei wurden drei reproduzierbare Vertragsluecken gefunden:

1. Full-UAT erwartete eine nicht versionierte `.env.uat`.
2. Full-UAT installierte keine Python-Abhaengigkeiten und stellte keine
   migrierte PostgreSQL-Datenbank bereit.
3. Der geplante Erntepeak-Test verwendete ein fest verdrahtetes,
   nicht nachgewiesenes Staging-Ziel und lief dadurch rund 18 Minuten ohne
   verwertbaren HTTP-Datentransfer.

## Korrektur

- Full-UAT nutzt `.env.uat` nur optional und faellt auf `.env.example`
  beziehungsweise eine minimale CI-Konfiguration zurueck.
- PostgreSQL, Python-Abhaengigkeiten und Migrationen sind Teil des Jobs.
- Backend und Frontend muessen aktive Health-Probes bestehen; feste
  Wartezeiten gelten nicht als Startnachweis.
- Lasttests verwenden nur `workflow_dispatch.base_url` oder `STAGING_URL`.
- Ohne Ziel bleibt das externe Performance-Gate explizit offen.
- Ein konfiguriertes, aber unerreichbares Ziel bricht vor Installation und
  Ausfuehrung des Lasttests ab.

## Vermeidung

`tests/test_ci_workflow_regressions.py` prueft diese Eigenschaften als
versionierten Workflow-Vertrag. Modulversionierung allein reicht nicht:
entscheidend sind reproduzierbare Laufzeitvoraussetzungen, explizite externe
Gates und fail-fast Readiness-Pruefungen.

## Separater Security-Blocker

Der Produktions-Audit meldet `GHSA-gv7w-rqvm-qjhr` fuer `esbuild` aus
`packages/agrar-silo-materialfluss-studio`. Das Paket liegt im aktiven
Cursor-Slice `WM-AGRI-SILO-001`. Dieser Befund bleibt bis zum Upgrade auf eine
gepatchte Abhaengigkeitskette und einem erneut gruenen
`pnpm audit --prod --audit-level high` blockierend.
