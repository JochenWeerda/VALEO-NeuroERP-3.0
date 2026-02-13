# Modulaktivierung pro Mandant

Diese Dokumentation beschreibt die Aktivierung von vertikalen Modulen (z. B. `agrar`) auf globaler und mandantenspezifischer Ebene.

## 1. Globale Aktivierung

Globale Modulaktivierung erfolgt über `INSTALLED_MODULES`.

Beispiel `.env`:

```env
INSTALLED_MODULES=core,agrar
```

## 2. Mandantenspezifische Aktivierung

Für tenant-spezifisches Gating wird `TENANT_MODULE_FLAGS` verwendet.

Beispiel `.env`:

```env
TENANT_MODULE_FLAGS={"tenant-a":["core"],"tenant-b":["core","agrar"]}
```

Regeln:
- Falls ein Tenant in `TENANT_MODULE_FLAGS` vorhanden ist, überschreibt diese Liste die globale `INSTALLED_MODULES`-Liste.
- Falls kein Tenant-spezifischer Eintrag vorhanden ist, gilt `INSTALLED_MODULES`.

## 3. Runtime-Validierung

Folgende Endpunkte unterstützen Tenant-Kontext:

- `GET /api/v1/meta/modules?tenant_id=<tenant-id>`
- `GET /api/v1/meta/modules/{module_name}?tenant_id=<tenant-id>`

Beispiel:

```bash
curl "http://localhost:8000/api/v1/meta/modules?tenant_id=tenant-a"
```

## 4. CI-Guardrails

Die CI prüft Architekturregeln in `quality-gate.yml`:

- `scripts/guard-forbidden-paths.cjs` (forbidden artifacts)
- `scripts/check_no_core_contamination.py` (keine `modules.*`-Imports in `app/core`)

## 5. Operative Empfehlung

- Neue Module zuerst global deaktiviert einführen.
- Pro Pilot-Tenant über `TENANT_MODULE_FLAGS` aktivieren.
- Nach UAT-Freigabe in `INSTALLED_MODULES` übernehmen.
