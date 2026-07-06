# ADR-038 — Kanonisches Adress-Value-Object

**Status:** Accepted
**Datum:** 2026-07-05
**Bezieht sich auf:** ADR-003 (Canonical Domain Model)

## Kontext

Adressen werden im System historisch uneinheitlich dargestellt:

- **Flache Spalten** — `domain_inventory.warehouses` (`address`/`city`/`postal_code`/`country`).
- **JSONB-Objekt** — `domain_shared.branches`, `customers`, `debitors`, `creditors`
  mit **inkonsistenten Alias-Keys**: `country`/`countryCode`/`country_code`,
  `postal_code`/`postalCode`/`zip`/`zipCode`/`plz`, `city`/`ort`, `street`/`strasse`.
- **Freitext-Strings** — Portal-/Lieferadressen (`"Hauptstrasse 123, 48143 Muenster"`).

Diese Divergenz kostete bereits: `warehouses.address` war in `001_initial_schema`
faelschlich JSONB (vom ORM-Modell als String erwartet) — Fresh-Install-Insert scheiterte
(Repair `runtime_sweep_repair_20260702`). Fuer Geo-/Kartenfeatures (Nominatim, `kunden_geo`),
Validierung, laenderspezifische Formatierung und Dublettenerkennung braucht es **eine**
kanonische Repraesentation.

## Entscheidung

Ein gemeinsames **Adress-Value-Object** `app/core/address.py::Address` mit kanonischen
Feldern (`street`, `house_no`, `postal_code`, `city`, `region`, `country`, `lat`, `lon`) ist
die kanonische Adress-Repraesentation. Dazu:

- `parse_address(value)` — Best-effort-Normalisierung aus dict (alle Alias-Keys), Freitext
  ("Strasse Nr, PLZ Ort") oder `Address`.
- `flat_to_address(...)` — Adapter fuer flache Spalten (Warehouse).
- `Address.to_jsonb()` / `Address.format_oneline()` — Serialisierung zurueck.

Neuer Code MUSS `Address` verwenden. Bestehende Entitaeten behalten zunaechst ihre
Speicherform; die Vereinheitlichung erfolgt schrittweise ueber Adapter an der Schema-Grenze
(kein Big-Bang-Umzug), damit Endpoints/Frontend/Tests nicht gleichzeitig brechen.

## Invariante

Set-Klauseln/Identifier aus Adress-JSONB duerfen nie roh in SQL interpoliert werden
(vgl. [AppSec-S608-Review](../../artifacts/appsec-s608-review.md)). JSONB-Adressen mit
`extra="allow"`-Modellen sind fuer Identifier-Interpolation tabu.

## Migrationsplan (Folgearbeit, P2)

1. **Read-Adapter (jetzt):** Response-Schemas exponieren `Address` via `parse_address(...)`
   aus vorhandener Speicherform — nicht-brechend.
2. **Write-Normalisierung:** JSONB-Schreiber auf `Address.to_jsonb()` (kanonische Keys)
   umstellen; Alias-Lese-Toleranz bleibt.
3. **Warehouse:** flache Spalten beibehalten oder auf JSONB `address`-VO heben — Entscheidung
   zusammen mit dem Frontend.
4. **Backfill-Migration:** bestehende JSONB-Alias-Keys idempotent auf kanonische Keys
   normalisieren; Geo-Anreicherung (`lat`/`lon`) aus `kunden_geo`.

## Konsequenzen

- **+** Eine Wahrheit fuer Adressen; Alias-Chaos gekapselt; testbar (`tests/test_address_value_object.py`).
- **+** Geokodierung/Validierung/Formatierung an einer Stelle.
- **−** Zwei Speicherformen koexistieren waehrend der schrittweisen Migration (Adapter-Schicht).
