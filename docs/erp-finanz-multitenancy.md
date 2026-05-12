# ERP-Domain: Mandantenisolierung für Finanz-Stammdaten und Bestellungen

**Stand:** operative Umsetzung im Repo (Meilenstein M-04, FiBu-/ERP-Follow-up).
**Verbindlicher API-/Tenant-Vertrag:** [ADR: Auth- und Tenant-Kontext](architecture/adr-2026-04-24-auth-tenant-context.md) (M-01), Ergänzung [AUTH- und Tenant-Konzept](AUTH-AND-TENANT-CONCEPT.md).

---

## 1. Ziel

- **Finanz-Stammdaten** im PostgreSQL-Schema `finanz` (Konten, Bankkonten, Debitoren, Kreditoren, Buchungen) sind **mandantenisoliert**: jede Liste und jeder Zugriff per ID erfolgt nur im Kontext eines Tenants (`tenant_id`).
- **Bestellungen (Purchase Orders)** werden bei **Lesen einzelner Datensätze**, **Änderungen**, **Freigabe/Storno** und **Soft-Delete** zusätzlich über **`tenant_id`** abgesichert (kein Zugriff auf fremde Mandanten per ID-Raten).

---

## 2. Datenbank

### 2.1 Schema `finanz`

Die Tabellen werden durch die Migrationen unter [`migrations/sql/erp/`](../migrations/sql/erp/README.md) angelegt bzw. erweitert.

| Migration (Auszug) | Inhalt |
|----------------------|--------|
| `001_finance_core.sql` | Legt Schema `finanz` und Kern-Tabellen ohne `tenant_id` an (`CREATE TABLE IF NOT EXISTS`). |
| `003_finanz_tenant_id.sql` | Fügt `tenant_id VARCHAR(255) NOT NULL DEFAULT '_legacy'` hinzu; ersetzt globale UNIQUE-Constraints durch **tenant-lokale** Unique-Indizes (z. B. `(tenant_id, kreditor_nr)`). |

### 2.2 Bestand Daten (`tenant_id`)

- Nach `003_*` erhält **jede bestehende Zeile** automatisch **`tenant_id = '_legacy'`** (Default beim `ALTER COLUMN`).
- Neue Einträge aus der Anwendung erhalten **`tenant_id` aus dem Request-Kontext** (`resolveTenantId`), nicht aus beliebigen Body-Feldern.

### 2.3 Einordnung anderer Datenbanklayouts

Kommt bei euch z. B. nur **`domain_finance`** vor und noch kein Schema **`finanz`**, ist zuerst **`001_finance_core.sql`** auszuführen, danach **`003_finanz_tenant_id.sql`** (siehe [README im Migrationsordner](../migrations/sql/erp/README.md)).

---

## 3. SQL-Migrationen ausführen

### 3.1 Tool: `tools/migration/run_sql_migration.ts`

Lädt `.env` mit `dotenv` und führt eine oder mehrere `.sql`-Dateien mit `pg` aus.
**Pfadreihenfolge:** zuerst **Repo-Wurzel-`.env`**, dann (falls anderer Pfad) **`.env` im aktuellen Arbeitsverzeichnis** (`override`).

**Verbindungs-URL** ( erste Treffer ohne `--url` / `--env` ):

1. `ERP_DATABASE_URL`
2. `DATABASE_URL`
3. `CRM_DATABASE_URL`

Explizit: `--url "postgresql://…"` oder `--env MEINE_DB_URL_VARIABLE`.

Beispiele (Repo-Wurzel, PowerShell):

```powershell
# .env enthält ERP_DATABASE_URL oder DATABASE_URL
npx ts-node tools/migration/run_sql_migration.ts `
  --file migrations/sql/erp/001_finance_core.sql `
  --file migrations/sql/erp/003_finanz_tenant_id.sql

# oder explizite Variable
npx ts-node tools/migration/run_sql_migration.ts --env ERP_DATABASE_URL `
  --file migrations/sql/erp/003_finanz_tenant_id.sql
```

Siehe auch [CRM_TOOLKIT – SQL Migration Runner](../tools/migration/CRM_TOOLKIT.md).

**Kurzweg (Repo-Wurzel):** `pnpm migrate:erp-finanz` bzw. `npm run migrate:erp-finanz` – führt dieselben beiden `--file`-Migrationen wie oben aus (`.env`-Laden wie oben).

### 3.2 Alternative: `psql`

```powershell
psql $env:ERP_DATABASE_URL -v ON_ERROR_STOP=1 -f migrations/sql/erp/003_finanz_tenant_id.sql
```

---

## 4. Anwendungscode (`packages/erp-domain`)

### 4.1 Request-Kontext

- **`packages/erp-domain/src/presentation/utils/request-context.ts`**
  - `resolveTenantId(req)` – Header `x-tenant-id`, sonst `req.user.tenantId`; in Prod fehlend → Fehler mit `statusCode` **400** (siehe ADR).
  - Dev/Test-Fallback über `ERP_ALLOW_MISSING_TENANT` / `NODE_ENV` (siehe ADR).

### 4.2 Finanz-HTTP-Router

- Unter [`presentation/controllers/`](../packages/erp-domain/src/presentation/controllers/) die Builder `buildFinanz*Router`:
  - Listen: `parseFinanzListQuery`, dann `service.listPaged(tenantId, …)`.
  - Detail / CRUD: `service.findById(id, tenantId)`, `create(tenantId, …)`, `update/remove` mit Tenant.
- Gemeinsamer Listen-/JSON-Contract: [`presentation/utils/finanz-http.ts`](../packages/erp-domain/src/presentation/utils/finanz-http.ts).

### 4.3 Schichten Finanz

- **Entities:** `tenant_id` in den Props; `tenantId`-Getter wo vorgesehen.
- **Repositories:** alle SQL-Filter inkl. `tenant_id`; Inserts schreiben `tenant_id`; Updates/Deletes mit `WHERE … AND tenant_id = $n`.
- **Services:** erster Parameter bzw. explizites `tenantId` pro Use-Case (keine Mandantenwahl allein durch Client-Body).

### 4.4 Purchase Orders

- **Repository:** `findById(id, tenantId)`, `delete(id, tenantId)` (Soft-Delete nur bei passendem Mandanten); fehlender Treffer beim Delete wirkt mit **`404`** über `statusCode` am Fehler.
- **Service/Controller:** `resolveTenantId` für GET by ID und alle Mutationspfade.

---

## 5. API-Verhalten kurz

| Bereich | Tenant-Quelle | Fehler bei fehlendem Tenant |
|--------|----------------|------------------------------|
| Finanz-Stammdaten-Routen | `resolveTenantId(req)` | 400 (wie ADR/Kontext) |
| Purchase Order (Liste war schon nach Tenant) | unverändert mit Tenant-Liste | wie oben |
| Purchase Order Detail/Mutation | `resolveTenantId` + Abgleich in DB | 404 wenn nicht gefunden/falscher Tenant |

Frontend: weiterhin konsistent **`X-Tenant-ID`** setzen ([AUTH- und Tenant-Konzept](AUTH-AND-TENANT-CONCEPT.md)).

---

## 6. Referenzen

| Dokument / Pfad |
|-----------------|
| [migrations/sql/erp/README.md](../migrations/sql/erp/README.md) |
| [tools/migration/run_sql_migration.ts](../tools/migration/run_sql_migration.ts) |
| [packages/erp-domain/README.md](../packages/erp-domain/README.md) |
| [docs/AUTH-AND-TENANT-CONCEPT.md](AUTH-AND-TENANT-CONCEPT.md) |
| [docs/architecture/adr-2026-04-24-auth-tenant-context.md](architecture/adr-2026-04-24-auth-tenant-context.md) |
