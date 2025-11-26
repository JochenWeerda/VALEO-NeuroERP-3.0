# InfraStat Compliance Service

Microservice zur automatisierten Erstellung und Validierung von Intrastat/InfraStat-Meldungen.

## Features

- ETL-Pipeline für Wareneingänge/-ausgänge mit Validierungen gegen TARIC- und Länderreferenzen (automatischer Statuswechsel `COLLECTING → VALIDATING → READY/ERROR`)
- Persistenz in PostgreSQL (`infrastat_declaration_batches`, `infrastat_declaration_lines`, `infrastat_validation_errors`, `infrastat_submission_log`)
- REST-API (`/api/v1/ingestion/batch`, `/api/v1/batches`, `/api/v1/batches/{id}/submit`)
- Mandantenfähigkeit (Parameter `tenant_id`)
- Prometheus-Metriken (optional)
- XML-Generierung nach INSTAT-6.3 (siehe [Destatis XSD-Paket](https://erhebungsportal.estatistik.de/Erhebungsportal/api/assets/files?downloadId=e9bdf11f6d194fb1a61844093381da3d)) **und DatML-RAW-D/RES-D** (XStatistik 2.0)
- IDEV-Client mit Session-Handling & Zertifikatsunterstützung (Upload-Events, `intrastat.submission.completed`)
- Scheduler & EventBus (NATS) zur Integration mit Workflow-Sagas (`intrastat.batch.ready`)

## Lokal starten

```bash
uvicorn main:app --reload --port 5200
```

## Tests

```bash
pytest services/compliance/infrastat/tests  # Unit- und Integrationstests (inkl. API & Metrics Smoke-Test)
pytest services/compliance/infrastat/tests/integration  # benötigt docker-compose.integration.yml + workflow-mock (nur Testzweck)
```

## IDEV Produktivbetrieb

- Setze folgende Umgebungsvariablen/Secrets:
  - `INFRASTAT_SUBMISSION_USERNAME`
  - `INFRASTAT_SUBMISSION_PASSWORD`
  - `INFRASTAT_SUBMISSION_CLIENT_CERT` (Pfad zum Client-Zertifikat)
  - `INFRASTAT_SUBMISSION_CLIENT_KEY`
- Passen Sie `SUBMISSION_RETRY_ATTEMPTS` und `SUBMISSION_RETRY_DELAY_SECONDS` in `config.py` an die SLA mit Destatis an.
- Empfohlen: Prometheus-Alerting auf `infrastat_submission_failure_total` und `infrastat_validation_failure_total`.

## TODO

- Export/Saga-Anbindung an Workflow-Service (REST-Saga-Definition & Retry-Pfade)
- Automatisierte Einreichung (IDEV/ELSTER) inklusive Auth-Flow ([IDEV Hilfeportal](https://www-idev.destatis.de/idev/#/help))
- End-to-End-Tests und CI-Integration

