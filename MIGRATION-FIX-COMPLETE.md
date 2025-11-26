# Migration-Problem behoben

## ✅ Problem gelöst

### Ursache:
- Datenbank hatte Version `001_initial_crm_sales_schema` (existiert nicht)
- Migration `1368e3f15650` versuchte, Tabelle `policy_rules` zu verschieben, die nicht existiert

### Lösung:
1. ✅ Datenbank-Version auf `001` gesetzt
2. ✅ Migration `1368e3f15650` korrigiert - prüft jetzt ob Tabelle existiert
3. ✅ Migration bis Head ausgeführt

### Änderungen:
- `alembic/versions/1368e3f15650_align_schema_with_domain__tables.py`:
  - Prüft jetzt ob `policy_rules` existiert, bevor sie verschoben wird
  - Verhindert Fehler wenn Tabelle nicht vorhanden ist

## 📊 Status

- ✅ Migration-Problem behoben
- ✅ Backend neu gestartet
- ⏳ API-Endpoints müssen getestet werden

## 🚀 Nächste Schritte

1. Backend-API testen:
   ```bash
   curl http://localhost:8000/api/mcp/documents/sales_offer?skip=0&limit=5
   ```

2. Dokumenten-Tabelle prüfen:
   ```sql
   SELECT * FROM documents LIMIT 5;
   ```

3. Frontend testen:
   - Angebote-Liste öffnen
   - Filter testen
   - CSV-Import testen

---

**Status:** ✅ **Migration-Problem behoben**

