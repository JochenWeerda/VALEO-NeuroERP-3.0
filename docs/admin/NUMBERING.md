# Nummernkreise konfigurieren

## Überblick

VALEO-NeuroERP unterstützt flexible Nummernkreise mit Multi-Tenant und Jahreswechsel-Support.

## Konfiguration

### Environment-Variablen

```bash
# Nummernkreis-Präfixe
NUMBERING_SALES_PREFIX=SO-
NUMBERING_PURCHASE_PREFIX=PO-
NUMBERING_INVOICE_PREFIX=INV-

# Nummernkreis-Breite (Anzahl Stellen)
NUMBERING_WIDTH=5

# Jahreswechsel aktivieren
NUMBERING_YEARLY_RESET=true

# Multi-Tenant aktivieren
NUMBERING_MULTI_TENANT=true
```

### Beispiele

**Standard (ohne Jahreswechsel):**
- `SO-00001`, `SO-00002`, `SO-00003`, ...

**Mit Jahreswechsel:**
- 2025: `SO-2025-00001`, `SO-2025-00002`, ...
- 2026: `SO-2026-00001`, `SO-2026-00002`, ...

**Multi-Tenant:**
- Tenant A: `SO-A-00001`, `SO-A-00002`, ...
- Tenant B: `SO-B-00001`, `SO-B-00002`, ...

**Multi-Tenant + Jahreswechsel:**
- Tenant A, 2025: `SO-A-2025-00001`
- Tenant B, 2025: `SO-B-2025-00001`

## Datenbank-Schema

```sql
CREATE TABLE number_series (
  domain VARCHAR(50) NOT NULL,
  tenant_id VARCHAR(50) DEFAULT 'default',
  year INTEGER DEFAULT NULL,
  prefix VARCHAR(20) NOT NULL,
  counter INTEGER DEFAULT 0,
  width INTEGER DEFAULT 5,
  PRIMARY KEY (domain, tenant_id, year)
);
```

## API-Endpoints

### Nächste Nummer generieren

```bash
POST /api/numbering/next
Content-Type: application/json

{
  "domain": "sales",
  "tenant_id": "A",
  "year": 2025
}

# Response
{
  "ok": true,
  "number": "SO-A-2025-00001"
}
```

### Aktuellen Stand abfragen

```bash
GET /api/numbering/status?domain=sales&tenant_id=A&year=2025

# Response
{
  "ok": true,
  "domain": "sales",
  "tenant_id": "A",
  "year": 2025,
  "prefix": "SO-A-2025-",
  "counter": 42,
  "next_number": "SO-A-2025-00043"
}
```

### Nummernkreis zurücksetzen

```bash
POST /api/numbering/reset
Content-Type: application/json

{
  "domain": "sales",
  "tenant_id": "A",
  "year": 2025
}

# Response
{
  "ok": true,
  "message": "Number series reset for sales/A/2025"
}
```

⚠️ **Achtung:** Reset nur in Ausnahmefällen verwenden!

## Jahreswechsel-Procedure

### Automatisch (empfohlen)

Nummernkreise werden automatisch beim ersten Request im neuen Jahr erstellt.

### Manuell (optional)

```bash
# Alle Nummernkreise für 2026 initialisieren
curl -X POST https://erp.valeo.example.com/api/numbering/init-year \
  -H "Content-Type: application/json" \
  -d '{"year": 2026}'
```

## Troubleshooting

### Problem: Doppelte Nummern

**Ursache:** Race-Condition bei hoher Last

**Lösung:** PostgreSQL-Locking ist implementiert, sollte nicht auftreten

**Verifikation:**
```sql
SELECT domain, tenant_id, year, COUNT(*) 
FROM documents_header 
GROUP BY domain, tenant_id, year, number 
HAVING COUNT(*) > 1;
```

### Problem: Lücken in Nummernkreis

**Ursache:** Transaktion wurde abgebrochen nach Nummern-Generierung

**Lösung:** Lücken sind normal und erlaubt (steuerrechtlich kein Problem)

### Problem: Falsches Präfix

**Ursache:** Environment-Variable falsch gesetzt

**Lösung:**
```bash
# Check current config
kubectl get configmap valeo-erp-config -n production -o yaml

# Update config
kubectl edit configmap valeo-erp-config -n production

# Restart pods
kubectl rollout restart deployment valeo-erp -n production
```

## Best Practices

1. **Präfixe kurz halten:** Max. 5 Zeichen (z.B. `SO-`, `INV-`)
2. **Width konsistent:** Alle Domains gleiche Breite (z.B. 5 Stellen)
3. **Jahreswechsel aktivieren:** Für bessere Übersicht
4. **Multi-Tenant nur bei Bedarf:** Overhead nur wenn nötig
5. **Kein Reset in Production:** Nur in Ausnahmefällen

## Migration von altem System

```python
# Skript: scripts/migrate-numbering.py
import psycopg2

# Connect to old system
old_conn = psycopg2.connect("postgresql://old_system")
old_cur = old_conn.cursor()

# Get max numbers from old system
old_cur.execute("SELECT MAX(order_number) FROM orders;")
max_order = old_cur.fetchone()[0]

# Update new system
new_conn = psycopg2.connect("postgresql://valeo_erp")
new_cur = new_conn.cursor()
new_cur.execute("""
  UPDATE number_series 
  SET counter = %s 
  WHERE domain = 'sales' AND tenant_id = 'default';
""", (max_order,))
new_conn.commit()

print(f"Migrated: Sales counter set to {max_order}")
```

## Support

Bei Fragen: admin@valeo-erp.com

