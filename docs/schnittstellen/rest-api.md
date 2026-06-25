---
title: REST-API
type: reference
audience: [integrator, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# REST-API

Die vollständige REST-API ist als OpenAPI 3.1-Spezifikation hinterlegt und wird
unten interaktiv eingebettet. **Single Source of Truth ist der Code** — die Spec
wird aus der FastAPI-App generiert.

## Eckdaten

- **Format:** OpenAPI 3.1.0
- **Basis-Pfad:** `/api/v1`
- **Authentifizierung:** OIDC Bearer-Token (`Authorization: Bearer <token>`)
- **Mandant:** Header `X-Tenant-ID` (sonst Default-Tenant / Token-Claim)
- **Korrelation:** Header `X-Correlation-ID` (wird zurückgegeben)
- **Spezifikation:** [openapi.json](openapi.json) (Download)

## Generierung / Aktualisierung

Die Spec wird bewusst **entkoppelt vom Docs-Build** erzeugt (der App-Import ist
schwergewichtig). Aktualisieren:

```bash
VALEO_API_VERSION=3.0.0 python scripts/generate_openapi.py
# Drift-Pruefung (CI/lokal):
python scripts/generate_openapi.py --check
```

!!! note "Umfang"
    Die Spec umfasst die gesamte API-Oberfläche (alle Router). Das interaktive
    Rendering unten kann je nach Endpoint-Anzahl einen Moment laden.

## Interaktive Referenz

<swagger-ui src="openapi.json"/>
