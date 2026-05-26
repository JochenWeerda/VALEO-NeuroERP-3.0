# ADR-034 — Tenant-Isolation-Klassifizierungssystem

**Status:** Angenommen
**Datum:** 2026-05-26
**Kontext:** Wave A3 Tenant Isolation

---

## Kontext

44 Endpoint-Dateien ohne `tenant_id`-Verwendung wurden identifiziert. Eine Analyse ergab,
dass die meisten dieser Dateien auf Modelle zugreifen, die **by design keine `tenant_id`-Spalte**
haben (physische Infrastruktur wie Waagen und Fahrzeuge, geteilte Stammdaten).

## Entscheidung

Jede Endpoint-Datei wird in eine von vier Klassen eingeordnet, verwaltet in
`scripts/check_tenant_isolation.py`:

| Klasse | Bedeutung |
|--------|-----------|
| `tenant-isolated` | Queries filtern nach `tenant_id` (automatisch erkannt) |
| `shared-data` | Datenmodell hat keine `tenant_id`-Spalte; deliberate Design |
| `system-endpoint` | Statuslose / infrastrukturelle Endpoints; kein DB-Tenant-Kontext |
| `gap-tracked` | Modell hat `tenant_id`, Endpoint filtert noch nicht (bekannte Lücke) |

Neue Dateien ohne Klassifizierung blockieren CI.

## Behobene Lücke

`crm_account_hierarchy.py` queried `business_partners` (Modell mit `tenant_id`) ohne
Tenant-Filter → Cross-Tenant-Datenleck. Behoben durch Hinzufügen von
`X-Tenant-ID`-Header-Dependency und `AND tenant_id = :tid` in allen SQL-Queries.

## Bekannte Lücken (shared-data)

18 Dateien greifen auf Modelle zu, die noch keine `tenant_id`-Spalte haben:
Waage, Fahrzeug, FoerderAntrag, ZertifikatEintrag, DispositionPosition, u.a.
Die Tenant-Isolierung dieser Daten erfordert:
1. Alembic-Migration: `tenant_id`-Spalte hinzufügen
2. Repository-Update: Filter-Methoden
3. Endpoint-Update: Dependency + Filter

Diese Arbeit ist als separate Migration-Wave geplant.

## Begründung

- **Sichtbarkeit statt Unsichtbarkeit:** Gaps sind explizit dokumentiert und CI-überwacht.
- **Keine Breaking Changes:** Modelle ohne `tenant_id` werden nicht verändert.
- **Erweiterbarkeit:** `gap-tracked`-Klasse ermöglicht geordnetes Schließen von Lücken.

## Konsequenzen

- `scripts/check_tenant_isolation.py` muss bei jedem neuen Endpoint-File aktualisiert werden.
- Der CI-Gate in `.github/workflows/quality-gate.yml` stellt sicher, dass kein unkassifierter
  Endpoint-File unbemerkt hinzugefügt wird.
