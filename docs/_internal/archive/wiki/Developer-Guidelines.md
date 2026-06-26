# Entwickler-Leitfaden: Lessons Learned

> Aus der UUID v7 Migration und dem Full-Stack-Aufbau im Februar 2026 gewonnene Erkenntnisse.
> Diese Regeln gelten fuer ALLE kuenftigen DB-Erweiterungen, Masken-Entwicklungen und Seed-Skripte.

---

## Regel 1: SQLAlchemy-Modell = einzige Wahrheit (Single Source of Truth)

**Problem:** Pydantic-Schemas enthielten Felder (`currency`, `allow_manual_entries`), die im SQLAlchemy-Modell nicht existierten. Beim Lesen aus der DB fehlten diese Felder, was zu 500-Fehlern fuehrte.

**Regel:**
- Das **SQLAlchemy-Modell** definiert die DB-Struktur
- Das **Pydantic-Schema** muss eine Teilmenge des Modells sein
- Niemals Felder im Pydantic-Schema definieren, die nicht im SQLAlchemy-Modell existieren
- Wenn ein Feld im Schema auftaucht, MUSS es auch als Column im Modell existieren

```
FALSCH:
  SQLAlchemy Model:  account_number, account_name, account_type
  Pydantic Schema:   account_number, account_name, account_type, currency, allow_manual_entries  <-- FEHLER!

RICHTIG:
  SQLAlchemy Model:  account_number, account_name, account_type, currency, allow_manual_entries
  Pydantic Schema:   account_number, account_name, account_type, currency, allow_manual_entries
```

---

## Regel 2: Pydantic `from_attributes = True` bei SQLAlchemy-Objekten

**Problem:** `HarvestAcceptanceOut.model_validate(sqlalchemy_obj)` schlug fehl mit "Input should be a valid dictionary", weil `from_attributes` nicht gesetzt war.

**Regel:**
- JEDES Pydantic-Ausgabe-Schema, das mit `model_validate()` auf SQLAlchemy-Objekte angewendet wird, MUSS `from_attributes = True` haben:

```python
class MyEntityOut(BaseModel):
    model_config = {"from_attributes": True}   # <-- PFLICHT!
    id: str
    name: str
    ...
```

Alternativ die `BaseSchema` aus `app/api/v1/schemas/base.py` verwenden, die dies bereits konfiguriert hat.

---

## Regel 3: `updated_at` ist immer Optional

**Problem:** SQLAlchemy `onupdate=func.now()` setzt `updated_at` nur bei UPDATEs. Bei INSERTs ist der Wert NULL. Pydantic-Schema mit `updated_at: datetime` (required) fuehrte zu ValidationError.

**Regel:**
```python
# SQLAlchemy Modell
updated_at = Column(DateTime(timezone=True), onupdate=func.now())   # NULL bei INSERT!

# Pydantic Schema - IMMER Optional
updated_at: Optional[datetime] = None   # <-- PFLICHT
created_at: Optional[datetime] = None   # <-- SICHERHEITSHALBER auch Optional
```

---

## Regel 4: NOT NULL Boolean-Felder brauchen Defaults

**Problem:** Artikel hatten 15+ Boolean-Spalten (`lager_zentral`, `lager_silo`, etc.) als `NOT NULL` im Modell, aber Seed-Daten liessen sie weg. Ergebnis: NULL in DB, Pydantic `bool` Validierung scheiterte.

**Regel:**
- Jedes Boolean-Feld im SQLAlchemy-Modell MUSS `server_default` haben:

```python
# SQLAlchemy
is_active = Column(Boolean, nullable=False, server_default="true")
lager_zentral = Column(Boolean, nullable=False, server_default="false")

# Pydantic
is_active: bool = True
lager_zentral: bool = False
```

- Im Seed-SQL alle Boolean-Werte explizit angeben (niemals weglassen!)

---

## Regel 5: Enum-Validierung = English-Werte im DB-Schema

**Problem:** Seed-Daten verwendeten deutsche Kategorien (`Umlaufvermoegen`, `Personalaufwand`), aber der Pydantic-Validator erwartete englische Werte (`current_assets`, `operating_expenses`).

**Regel:**
- DB-Werte fuer validierte Enums MUESSEN den englischen Pydantic-Validator-Werten entsprechen
- Deutsche Bezeichnungen gehoeren in `description` oder `subcategory` Felder, nicht in validierte Enum-Spalten
- Bei Erweiterung eines Enum-Validators: Neuen Wert sowohl im Validator ALS AUCH in der Seed-Datei hinzufuegen

```sql
-- FALSCH
INSERT INTO finance_accounts (..., category, ...) VALUES (..., 'Umlaufvermoegen', ...);

-- RICHTIG
INSERT INTO finance_accounts (..., category, subcategory, ...) VALUES (..., 'current_assets', 'Liquide Mittel', ...);
```

---

## Regel 6: BusinessPartner PK ist `partner_id`

**Problem:** Nach UUID v7 Migration verwendet BusinessPartner `partner_id` als PK (nicht `id`). ForeignKeys auf `.id` fuehrten zu "column not found".

**Regel:**
```python
# FALSCH
supplier_id = Column(String, ForeignKey("domain_crm.business_partners.id"))

# RICHTIG
supplier_id = Column(String, ForeignKey("domain_crm.business_partners.partner_id"))
```

---

## Regel 7: Schemas muessen vor create_all() existieren

**Problem:** `Base.metadata.create_all()` scheiterte, weil Schemas (`domain_shared`, `domain_agrar`, etc.) noch nicht in PostgreSQL existierten.

**Regel:**
- Alle Domain-Schemas in `scripts/init.sql` anlegen
- `init.sql` wird beim ersten Docker-Start mit leerem Volume ausgefuehrt
- Bei neuem Schema: Zeile in `init.sql` UND manuelles `CREATE SCHEMA IF NOT EXISTS` bei bestehenden DBs

---

## Regel 8: ForeignKeys auf existierende Tabellen pruefen

**Problem:** `verkauf/models.py` hatte FKs auf `formulare.id`, `zinstabellen.id`, `rabatt_listen.id` - Tabellen, die nie angelegt wurden.

**Regel:**
- Vor dem Hinzufuegen eines ForeignKey pruefen: Existiert das Ziel-Modell als SQLAlchemy-Klasse?
- Kein FK auf Tabellen anlegen, die nur in Alembic-Migrationen existieren
- Wenn die Ziel-Tabelle noch nicht existiert: FK weglassen und als plain Column definieren

```python
# FALSCH (Ziel-Tabelle existiert nicht)
formular_id = Column(Integer, ForeignKey("formulare.id"))

# RICHTIG (Ziel-Tabelle existiert noch nicht, wird spaeter nachgezogen)
formular_id = Column(Integer, nullable=True)  # FK zu formulare - TODO: Tabelle anlegen
```

---

## Regel 9: Docker Healthcheck ohne curl

**Problem:** Python-Container haben kein `curl` installiert. Healthcheck `CMD curl -f ...` scheiterte immer.

**Regel:**
```yaml
# FALSCH
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

# RICHTIG
healthcheck:
  test: ["CMD-SHELL", "python3 -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\""]
```

---

## Regel 10: SQLAlchemy text() fuer Raw-SQL

**Problem:** `db.execute("SELECT 1")` funktioniert in SQLAlchemy 2.0 nicht mehr. Erfordert `text()` Wrapper.

**Regel:**
```python
from sqlalchemy import text

# FALSCH (SQLAlchemy 1.x Syntax)
db.execute("SELECT 1")

# RICHTIG (SQLAlchemy 2.0)
db.execute(text("SELECT 1"))
```

---

## Checkliste: Neue Tabelle/Maske hinzufuegen

1. [ ] SQLAlchemy-Modell in `app/infrastructure/models/` anlegen
2. [ ] Schema in `init.sql` pruefen (existiert `CREATE SCHEMA IF NOT EXISTS domain_xxx`?)
3. [ ] Pydantic-Schema erstellen mit `model_config = {"from_attributes": True}`
4. [ ] `updated_at: Optional[datetime] = None` setzen
5. [ ] Alle Boolean-Felder mit `server_default` im Modell und Default im Schema
6. [ ] Alle Enum-Felder: Englische Werte im Validator UND im Seed-SQL
7. [ ] ForeignKeys pruefen: Ziel-Tabelle existiert als SQLAlchemy-Klasse?
8. [ ] Seed-Daten: ALLE NOT NULL Felder explizit angeben
9. [ ] Alembic-Migration erstellen: `alembic revision --autogenerate -m "add xxx"`
10. [ ] Endpoint testen: GET liefert 200, POST liefert 201
