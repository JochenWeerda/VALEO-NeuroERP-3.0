# Zoll- & Exportkontrollservice

Microservice für Sanktionslistenscreening, Genehmigungsverwaltung und Präferenzkalkulation.

## Features

- Screening-Engine gegen lokale/remote Sanktionslisten (EU, OFAC) (`/api/v1/screening/matches`) – publiziert Events `export.screening.cleared|review|failed`
- Exportgenehmigungen CRUD (`/api/v1/permits`)
- Präferenzkalkulation (`/api/v1/preference/calculate`)
- Event-Bus (NATS) zur Integration mit Workflow-Hooks (`compliance.zoll.*`)
- Scheduler lädt Sanktionslisten periodisch nach (`ZOLL_SANCTIONS_REFRESH_URL`, `OFAC_API_URL`, `EU_API_URL`) inkl. Delta-Merge und Backoff
- Prometheus-Metriken (`zoll_sanctions_refresh_total`, `zoll_screening_status_total`, `zoll_sanctions_refresh_backoff_minutes`)
- Workflow `export_clearance` wird beim Start beim Workflow-Service registriert

## Lokal starten

```bash
uvicorn main:app --reload --port 5300
```

## Tests

```bash
pytest services/compliance/zoll/tests
```

## Konfiguration

Wichtige Variablen:
- `ZOLL_SANCTIONS_REFRESH_URL`, `ZOLL_OFAC_API_KEY`, `ZOLL_EU_API_KEY`
- `ZOLL_SANCTIONS_REFRESH_INTERVAL_MINUTES`
- `ZOLL_SANCTIONS_REFRESH_BACKOFF_MINUTES`
- `ZOLL_SANCTIONS_REFRESH_MAX_BACKOFF_MINUTES`
- `ZOLL_WORKFLOW_TENANT`

## TODO

- Erweiterte Workflow-Policies (rollenspezifische Reviews) im Workflow-Service UI ausrollen
- Präferenz- und Permit-APIs mit Frontend verbinden
