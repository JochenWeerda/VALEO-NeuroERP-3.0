# Generierte Spalten für Adress-Suche

**Datum:** 2026-02-17  
**Status:** ✅ Implementiert  
**Migration:** `add_customer_address_generated_columns_20260217.py`

## Problem

Die `address` Spalte in `domain_crm.customers` ist als JSONB definiert, was Flexibilität bietet, aber normale SQL-Filter und Indizes erschwert:

```sql
-- Langsam (ohne Index):
SELECT * FROM domain_crm.customers 
WHERE address->>'city' = 'Berlin';

-- Nicht möglich (keine direkte Indexierung):
CREATE INDEX ON customers (address->>'city');  -- Funktioniert nicht direkt
```

## Lösung: Generierte Spalten (Generated Columns)

PostgreSQL unterstützt seit Version 12 **STORED Generated Columns** - Spalten, die automatisch aus anderen Spalten berechnet werden.

### Implementierung

Wir extrahieren die häufigsten Suchfelder aus dem JSONB:

1. **`address_country`** - Länder-Code (z.B. "DE", "AT", "CH")
2. **`address_postal_code`** - Postleitzahl
3. **`address_city`** - Stadt

Diese Spalten werden automatisch aus dem JSONB-Feld berechnet und als normale Spalten gespeichert.

### Vorteile

✅ **Normale Indizes**: B-Tree Indizes auf generierten Spalten  
✅ **Schnelle Suche**: `WHERE address_city = 'Berlin'` ist sehr schnell  
✅ **Flexibilität bleibt**: JSONB-Feld bleibt unverändert für erweiterte Felder  
✅ **Keine Breaking Changes**: Bestehende Queries funktionieren weiterhin  
✅ **Automatische Synchronisation**: Spalten werden automatisch aktualisiert bei Änderungen am JSONB

### Indizes

```sql
-- Einzelne Indizes
CREATE INDEX idx_customers_address_country ON domain_crm.customers (address_country);
CREATE INDEX idx_customers_address_postal_code ON domain_crm.customers (address_postal_code);
CREATE INDEX idx_customers_address_city ON domain_crm.customers (address_city);

-- Composite Index für häufige Suchmuster
CREATE INDEX idx_customers_address_city_postal ON domain_crm.customers (address_city, address_postal_code);

-- GIN Index für komplexe JSONB-Queries
CREATE INDEX idx_customers_address_gin ON domain_crm.customers USING GIN (address);
```

### Verwendung

#### Schnelle Suche mit generierten Spalten:

```sql
-- Sehr schnell (mit B-Tree Index)
SELECT * FROM domain_crm.customers 
WHERE address_city = 'Berlin';

-- Schnell (mit Composite Index)
SELECT * FROM domain_crm.customers 
WHERE address_city = 'Berlin' AND address_postal_code = '10115';

-- Schnell (mit Index)
SELECT * FROM domain_crm.customers 
WHERE address_country = 'DE';
```

#### Komplexe Suche mit JSONB (GIN Index):

```sql
-- Für erweiterte Felder im JSONB
SELECT * FROM domain_crm.customers 
WHERE address @> '{"state": "Bayern"}';

-- Für mehrere Bedingungen
SELECT * FROM domain_crm.customers 
WHERE address->>'city' = 'Berlin' 
  AND address->>'district' = 'Mitte';
```

### JSONB-Feldstruktur

Die generierten Spalten unterstützen verschiedene JSONB-Feldnamen (für Kompatibilität):

```json
{
  "street": "Musterstraße 123",
  "city": "Berlin",              // → address_city
  "postalCode": "10115",         // → address_postal_code
  "postal_code": "10115",        // Alternative
  "zip": "10115",                // Alternative
  "country": "DE",               // → address_country
  "countryCode": "DE",            // Alternative
  "state": "Berlin",              // Bleibt im JSONB
  "district": "Mitte"             // Bleibt im JSONB
}
```

### Migration

```bash
# Migration ausführen
alembic upgrade head

# Prüfen
psql -c "SELECT address_country, address_postal_code, address_city FROM domain_crm.customers LIMIT 5;"
```

### Performance

**Vorher (ohne generierte Spalten):**
- Suche nach Stadt: **Sequential Scan** (langsam)
- Suche nach PLZ: **Sequential Scan** (langsam)

**Nachher (mit generierten Spalten):**
- Suche nach Stadt: **Index Scan** (sehr schnell)
- Suche nach PLZ: **Index Scan** (sehr schnell)
- Composite Suche: **Index Scan** (sehr schnell)

### Wartung

Die generierten Spalten werden automatisch aktualisiert, wenn das JSONB-Feld geändert wird:

```sql
-- Update JSONB
UPDATE domain_crm.customers 
SET address = '{"city": "München", "postalCode": "80331", "country": "DE"}'::jsonb
WHERE id = '...';

-- Generierte Spalten werden automatisch aktualisiert:
-- address_city = 'München'
-- address_postal_code = '80331'
-- address_country = 'DE'
```

### Best Practices

1. **Für einfache Suche**: Verwende generierte Spalten (`address_city`, `address_postal_code`)
2. **Für komplexe Suche**: Verwende JSONB-Operatoren (`address @> ...`)
3. **Für erweiterte Felder**: Bleibe im JSONB (`address->>'state'`)

### Beispiel-Queries

```sql
-- Alle Kunden in Berlin
SELECT * FROM domain_crm.customers 
WHERE address_city = 'Berlin';

-- Alle Kunden in Deutschland
SELECT * FROM domain_crm.customers 
WHERE address_country = 'DE';

-- Alle Kunden in Berlin mit PLZ 10115
SELECT * FROM domain_crm.customers 
WHERE address_city = 'Berlin' AND address_postal_code = '10115';

-- Alle Kunden in einem PLZ-Bereich (mit Index)
SELECT * FROM domain_crm.customers 
WHERE address_postal_code LIKE '10%';

-- Komplexe Suche mit JSONB (für erweiterte Felder)
SELECT * FROM domain_crm.customers 
WHERE address @> '{"city": "Berlin", "district": "Mitte"}';
```

---

**Hinweis**: Diese Lösung kombiniert die Vorteile von JSONB (Flexibilität) und normalisierten Spalten (Performance).

