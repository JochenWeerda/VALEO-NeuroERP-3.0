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

Stand 2026-06-16: Der produktive Dependency-Blocker ist repo-seitig
geschlossen.

- `esbuild` ist auf die gepatchte Linie `^0.28.1` gepinnt.
- Vite baut und prebundelt explizit fuer `es2022`, weil der gepatchte
  `esbuild`-Pfad bei ES2020-Downleveling reproduzierbar an Destructuring
  scheiterte.
- `starlette`, `python-multipart` und `aiohttp` sind auf die von
  `pip-audit` geforderten Patch-Versionen angehoben.
- `pnpm audit --prod --audit-level high` meldet keine High/Critical-Befunde
  mehr; `pip-audit -r requirements.txt` meldet keine bekannten
  Schwachstellen mehr.

Der Response-Model-Check nutzt jetzt eine dateigenaue Baseline
(`docs/quality-assurance/response-model-baseline.json`). Das ist kein
Freibrief fuer untypisierte Routen: neue untypisierte FastAPI-Routen oder
per-Datei-Regressions schlagen fehl. Die bestehende Altlast von 140
untypisierten Routen bleibt transparent und muss inkrementell durch konkrete
`response_model`-Schemas abgebaut werden.

Gelernte Ursache: Die Fehler entstanden nicht durch fehlende Modulversionierung
allein, sondern durch eine Kombination aus Security-Pin ohne Build-Kompatibilitaetstest,
extern aktivierten GitHub-Security-Funktionen, fehlendem LFS-Objekt und einem
zu niedrig gesetzten globalen Threshold ohne versionierte Baseline. Kuenftig
muessen Major- oder Security-Patch-Linien immer als Paket aus Audit,
Frontend-Build, Dev-Server/WCAG und betroffenen Docker-Builds validiert werden.
