# ERP – SQL-Migrationen (`migrations/sql/erp`)

PostgreSQL-Skripte für das **`erp-domain`**-Umfeld und verwandte Dienste. Reihenfolge über **Dateipräfix** (`001_`, `002_`, …).

## Finanz-Schema `finanz` und Mandanten (`tenant_id`)

| Datei | Zweck |
|-------|--------|
| `001_finance_core.sql` | Erstellt Schema **`finanz`** und Tabellen **konten, bankkonten, debitoren, kreditoren, buchungen** (kernhaltig, `IF NOT EXISTS`). Basis für das TypeScript-Finanzmodul unter `packages/erp-domain`. |
| `003_finanz_tenant_id.sql` | Fügt **`tenant_id`** (Default **`_legacy`**) hinzu und ersetzt globale UNIQUE-Constraints durch Unique-Indizes **pro Mandant** (z. B. `(tenant_id, kontonummer)`). **Voraussetzung:** gleiche Tabellen wie nach `001_finance_core.sql` vorhanden. |

> **Hinweis:** `001_finance_schema.sql` kann andere Abhängigkeiten haben (z. B. `users`). Für das aktuelle **`FinanzKreditor`/…-Repository** ist die Kombination **`001_finance_core.sql`** + **`003_finanz_tenant_id.sql`** dokumentiert ([docs/erp-finanz-multitenancy.md](../../docs/erp-finanz-multitenancy.md)).

## Weitere Dateien im Ordner (Kurzüberblick)

- `001_erp_schema.sql` – ERP-Kernschema (je nach Projekt nutzen).
- `002_warehouse_schema.sql` – Lager.
- `003_project_schema.sql` – Projekte (nicht zu verwechseln mit `003_finanz_tenant_id.sql`).
- `004_purchasing_schema.sql` – Einkauf.
- `005_order_management_schema.sql` – Auftragsmanagement.

Die genaue Abhängigkeitsreihenfolge zwischen **allen** ERP-Skripten bitte gegen eure operative DB prüfen; für **nur** Finanz-Stammdaten gilt die obige Zwei-Schritt-Kette.

## Ausführung

### Variante A: Node-SQL-Runner (empfohlen)

Aus der **Repo-Wurzel**; Verbindungs-URL durch **`--url`** / **`--env`**, oder automatisch erste gesetzte Variable unter **`ERP_DATABASE_URL`** → **`DATABASE_URL`** → **`CRM_DATABASE_URL`**.

```powershell
npx ts-node tools/migration/run_sql_migration.ts `
  --file migrations/sql/erp/001_finance_core.sql `
  --file migrations/sql/erp/003_finanz_tenant_id.sql
```

**Alternativ:** `pnpm migrate:erp-finanz` bzw. `npm run migrate:erp-finanz` (gleiche Dateien; der Runner lädt `.env` aus Repo-Wurzel und optional `./.env` im aktuellen Arbeitsverzeichnis).

### Variante B: `psql`

```powershell
psql $env:ERP_DATABASE_URL -v ON_ERROR_STOP=1 -f migrations/sql/erp/003_finanz_tenant_id.sql
```

Details: [docs/erp-finanz-multitenancy.md](../../docs/erp-finanz-multitenancy.md), [tools/migration/CRM_TOOLKIT.md](../../tools/migration/CRM_TOOLKIT.md).
