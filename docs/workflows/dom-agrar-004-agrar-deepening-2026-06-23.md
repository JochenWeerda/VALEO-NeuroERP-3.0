# DOM-AGRAR-004 — Agrar-Domäne Vertiefung

**Slice:** DOM-AGRAR-004\
**Datum:** 2026-06-23\
**Owner:** Claude Code

---

## 1. Scope

| Sub-Slice | Fachgebiet | Kern-Endpunkt |
|---|---|---|
| .2 | Partie-Aggregation (Ernteannahmen → Partie) | `POST /agrar/partien` |
| .3 | Trocknungsabrechnung (Partie → Trocknung → Kosten) | `POST /agrar/partien/{id}/trocknung` |
| .4 | Selbstabrechnung-Lifecycle (Status-Maschine + Storno) | `POST /agrar/selbstabrechnung/{id}/issue`, `/storno` |
| .5 | E2E UAT | Playwright @smoke + Python-UAT-Script |

---

## 2. .2 Partie-Aggregation

### Soll-Prozess

1. Mehrere Ernteannahmen (harvest_acceptances) liegen im Status `accepted`.
2. Disponent ruft `POST /agrar/partien` auf mit `[acceptance_id, ...]`.
3. Service aggregiert: `total_gross_kg = sum(gross_kg)`, `total_net_kg = sum(net_kg)`,
   `avg_moisture_pct = gewichteter Mittelwert`, `avg_impurity_pct = gewichteter Mittelwert`.
4. Eindeutige `partie_number` wird generiert (`P-{YYYYMMDD}-{SEQ}`).
5. Partie-Links werden angelegt (eine Zeile pro Annahme).
6. Cross-Tenant-Guard: alle Annahmen müssen zum gleichen Tenant gehören.
7. Duplikat-Guard: Annahme darf nicht in zwei Partien sein.

---

## 3. .3 Trocknungsabrechnung

### Formel

```
trocknungsabzug_kg = brutto_kg * (moisture_in_pct - moisture_out_pct) / 100
trocknungskosten_eur = (brutto_kg / 1000) * (moisture_in_pct - moisture_out_pct)
                       * cost_eur_per_pct_ton
```

Default `cost_eur_per_pct_ton = 1.50 EUR` (konfigurierbar via Backend-Config).

### Fail-Closed-Regeln

- `moisture_out_pct >= moisture_in_pct` → 422 (keine Trocknung nötig)
- Partie muss im Status `OFFEN` sein
- Idempotent: zweiter Aufruf gibt bestehende Abrechnung zurück

---

## 4. .4 Selbstabrechnung-Lifecycle

### Statusmaschine

```
DRAFT → ISSUED → PAID
      → CANCELLED
ISSUED → DISPUTED → RESOLVED
       → CANCELLED (via storno)
```

- `POST /issue`: DRAFT → ISSUED (fail-closed: nur aus DRAFT)
- `POST /storno`: DRAFT/ISSUED → CANCELLED + Gegenbuchungs-Record (idempotent)
- Jeder Übergang wird in `agrar_selbstabrechnung_status_log` gespeichert.

---

## 5. Datenmodell

### `agrar_partien` (neu)

```sql
CREATE TABLE domain_agrar.agrar_partien (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    partie_number VARCHAR(50) NOT NULL UNIQUE,
    article_id VARCHAR(64),
    campaign_id VARCHAR(36),
    total_gross_kg NUMERIC(14,3),
    total_net_kg NUMERIC(14,3),
    avg_moisture_pct NUMERIC(7,3),
    avg_impurity_pct NUMERIC(7,3),
    status VARCHAR(20) DEFAULT 'OFFEN',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `agrar_partie_links` + `agrar_trocknung_abrechnungen` + `agrar_selbstabrechnung_status_log`

Siehe Slice-YAML für vollständige Spaltenliste.

---

## 6. Nicht-Ziele

- Automatische Partie-Bildung bei Annahme (kein Hook in harvest_acceptance)
- MATIF-Preisbindung (gehört zu agrar_contracts)
- QS-Statusübergänge (WM-AGRI-QS-004, Cursor)
- Buchungsintegration in FIBU (Folge-Slice)
