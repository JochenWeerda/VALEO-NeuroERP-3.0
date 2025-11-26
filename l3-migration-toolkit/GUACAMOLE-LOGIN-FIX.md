***REMOVED*** 🔐 Guacamole Login-Problem - Schnelle Lösung

**Problem:** `guacadmin` / `guacadmin` funktioniert nicht

**Ursache:** DB-Init-Script wurde nicht korrekt ausgeführt

---

***REMOVED******REMOVED*** ⚡ Schnellste Lösung (Copy-Paste):

```powershell
***REMOVED*** 1. Container stoppen
cd C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit
docker compose down

***REMOVED*** 2. Volume löschen (DB neu initialisieren)
docker volume rm l3-migration-postgres-data

***REMOVED*** 3. Neu starten
docker compose up -d

***REMOVED*** 4. Warten (wichtig!)
Start-Sleep -Seconds 40

***REMOVED*** 5. DB-Init ausführen
docker exec l3-guacamole /opt/guacamole/bin/initdb.sh --postgres > initdb.sql
Get-Content initdb.sql | docker exec -i l3-postgres psql -U guacamole_user -d guacamole_db

***REMOVED*** 6. Guacamole neu starten
docker restart l3-guacamole
Start-Sleep -Seconds 15

***REMOVED*** 7. Browser öffnen
Start-Process "http://localhost:8090/guacamole"
```

**Dann Login:**
- User: `guacadmin`
- Pass: `guacadmin`

---

***REMOVED******REMOVED*** 🔍 Alternative: Logs prüfen

```powershell
***REMOVED*** Guacamole-Logs ansehen
docker logs l3-guacamole

***REMOVED*** PostgreSQL-Logs
docker logs l3-postgres

***REMOVED*** Tabellen prüfen
docker exec l3-postgres psql -U guacamole_user -d guacamole_db -c "\dt"
```

**Erwartete Tabellen:**
- guacamole_user
- guacamole_entity
- guacamole_connection
- guacamole_connection_parameter
- ... (ca. 20+ Tabellen)

---

***REMOVED******REMOVED*** 🎯 Wenn immer noch Probleme:

**Manuelles SQL-Schema laden:**

```powershell
***REMOVED*** Schema aus Container exportieren
docker exec l3-guacamole cat /opt/guacamole/postgresql/schema/001-create-schema.sql > schema-001.sql
docker exec l3-guacamole cat /opt/guacamole/postgresql/schema/002-create-admin-user.sql > schema-002.sql

***REMOVED*** In DB laden
Get-Content schema-001.sql | docker exec -i l3-postgres psql -U guacamole_user -d guacamole_db
Get-Content schema-002.sql | docker exec -i l3-postgres psql -U guacamole_user -d guacamole_db

***REMOVED*** Guacamole neu starten
docker restart l3-guacamole
```

---

**Versuchen Sie die "Schnellste Lösung" - das sollte funktionieren!** ✅

