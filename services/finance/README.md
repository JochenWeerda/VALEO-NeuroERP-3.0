# Finance Service (GoBD Foundations)

Dieser Service stellt die Python/FastAPI-Basis für die FiBu-Domain bereit, wie in `docs/specs/fibu_phase1_architecture.md` gefordert. Wichtige Eckpunkte:

- **Core Layer**: `app/core/config.py` und `app/core/database.py` kapseln Settings & SQLAlchemy. `app/core/logging.py` initialisiert Structlog-Logging.
- **Middleware**: `app/middleware/correlation.py` vergibt `X-Correlation-ID`, `app/middleware/metrics.py` liefert Prometheus-Metriken (`/metrics`).
- **Domain**: `app/domains/finance/` enthält SQLAlchemy-Modelle, Repositories, Services und den FastAPI-Router (`/api/v1/...`).
- **GoBD/Audit**: `finance_shared.gobd.audit_trail.GoBDAuditTrail` erzeugt Hash-Chains bei Journalbuchungen.

## Endpunkte (Phase 0)

- `GET /health` & `GET /ready`: Service- und DB-Status.
- `GET /api/v1/chart-of-accounts`: Seedet bei Bedarf Standardkonten und liefert sie zurück.
- `GET /api/v1/journal-entries`: Listet Journaleinträge je Tenant.
- `POST /api/v1/journal-entries`: Legt eine Buchung an (`userId` im Payload) und erstellt Audit-Hash.
- `GET /api/v1/open-items`: Liefert Demo-OPs (werden pro Tenant einmalig geseeded).

Alle API-Aufrufe akzeptieren optional den Header `X-Tenant-ID`, sonst greift `DEFAULT_TENANT` aus den Settings.

## Tests

```
python -m pytest services/finance/tests/unit/test_finance_api.py -q
```

Die Tests setzen die SQLite-Datenbank (`finance.db`) jedes Mal zurück und prüfen Health, Kontenliste sowie Journalbuchungen.

