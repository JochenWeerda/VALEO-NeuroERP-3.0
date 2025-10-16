# CRM-System produktionsreif starten

## 1. Docker-Services starten

```bash
# PostgreSQL, Redis, Keycloak starten
docker-compose up -d postgres redis keycloak

# Warten bis PostgreSQL bereit ist
docker-compose logs -f postgres
```

## 2. Datenbank-Migrationen ausführen

```bash
# Alembic-Migrationen anwenden
alembic upgrade head

# Verifizieren: Neue Tabellen sollten existieren
# - domain_crm.activities
# - domain_crm.farm_profiles
```

## 3. Backend starten (Python/FastAPI)

```bash
# In einem Terminal
python main.py

# Oder mit uvicorn direkt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Frontend starten

```bash
# In einem anderen Terminal
cd packages/frontend-web
pnpm install
pnpm dev
```

## 5. System testen

### CRM-Modul aufrufen:
- **Kontakte**: http://localhost:3000/crm/kontakte-liste
- **Leads**: http://localhost:3000/crm/leads
- **Aktivitäten**: http://localhost:3000/crm/aktivitaeten  
- **Betriebsprofile**: http://localhost:3000/crm/betriebsprofile

### API-Dokumentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API-Endpoints testen:

```bash
# Activities erstellen
curl -X POST "http://localhost:8000/api/v1/crm/activities" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "meeting",
    "title": "Jahresgespräch 2025",
    "customer": "Musterfirma GmbH",
    "contact_person": "Max Mustermann",
    "date": "2025-12-15T10:00:00Z",
    "status": "planned",
    "assigned_to": "Hans Mueller",
    "description": "Wichtiges Jahresgespräch"
  }'

# Activities abrufen
curl "http://localhost:8000/api/v1/crm/activities"

# Farm Profile erstellen
curl -X POST "http://localhost:8000/api/v1/crm/farm-profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_name": "Bio-Hof Schmidt",
    "owner": "Hans Schmidt",
    "total_area": 150.5,
    "crops": [
      {"crop": "Weizen", "area": 80},
      {"crop": "Gerste", "area": 45}
    ],
    "livestock": [
      {"type": "Milchkühe", "count": 60}
    ],
    "location": {
      "latitude": 52.520008,
      "longitude": 13.404954,
      "address": "Teststraße 123, 12345 Teststadt"
    },
    "certifications": ["Bio", "QS"],
    "notes": "Traditionsreicher Betrieb seit 1950"
  }'
```

## 6. Datenbank direkt prüfen

```bash
# Mit Docker exec in PostgreSQL
docker exec -it valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp

# SQL-Abfragen
\dt domain_crm.*
SELECT * FROM domain_crm.activities;
SELECT * FROM domain_crm.farm_profiles;
```

## 7. Playwright E2E-Tests

```bash
# Tests ausführen
npx playwright test playwright-tests/crm-crud.spec.js

# Mit UI
npx playwright test --ui
```

## Troubleshooting

### Problem: Migration-Fehler
```bash
# Migration zurücksetzen
alembic downgrade -1

# Neu migrieren
alembic upgrade head
```

### Problem: Schema existiert nicht
```bash
# Schemas manuell erstellen
docker exec -it valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp \
  -c "CREATE SCHEMA IF NOT EXISTS domain_crm;"
```

### Problem: Backend startet nicht
```bash
# Python-Dependencies installieren
pip install -r requirements.txt

# Environment-Variablen prüfen
cat .env
```

## Produktions-Features

✅ **Echte Datenbank**: PostgreSQL mit SQLAlchemy
✅ **Transaktionen**: Commit/Rollback bei Fehler
✅ **Migrationen**: Alembic für Schema-Änderungen
✅ **Filter & Suche**: Type, Status, Search-Term
✅ **Pagination**: Skip & Limit Parameter
✅ **Validierung**: Pydantic Schemas
✅ **Error Handling**: HTTP Exception Handling
✅ **JSONB**: Flexible Daten für Crops, Livestock, Location

## Nächste Optimierungen (Optional)

1. **Indizes hinzufügen**:
   ```sql
   CREATE INDEX idx_activities_date ON domain_crm.activities(date);
   CREATE INDEX idx_activities_status ON domain_crm.activities(status);
   CREATE INDEX idx_farm_profiles_owner ON domain_crm.farm_profiles(owner);
   ```

2. **Full-Text-Search**:
   ```sql
   CREATE INDEX idx_farm_profiles_search ON domain_crm.farm_profiles 
   USING gin(to_tsvector('german', farm_name || ' ' || owner));
   ```

3. **Connection Pooling**: SQLAlchemy Pool-Size optimieren
4. **Caching**: Redis für häufige Queries
5. **Background Jobs**: Celery für async Operationen

