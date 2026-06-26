# OpenAPI / Swagger Dokumentation

## Live Endpunkte
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON (live): `/api/v1/openapi.json`

## Versioniertes Artefakt
- Datei: `docs/api/openapi.json`
- Erzeugung: `python scripts/export_openapi.py`

## Pflegeprozess
1. Backend-Endpunkte ändern.
2. `python scripts/export_openapi.py` ausführen.
3. `docs/api/openapi.json` diff prüfen.
4. Änderungen mit Commit mitführen.
