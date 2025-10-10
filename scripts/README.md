***REMOVED*** VALEO NeuroERP - Scripts

Dieses Verzeichnis enthält Deployment-, Test- und Utility-Scripts für VALEO NeuroERP.

***REMOVED******REMOVED*** 📁 Staging-Deployment

***REMOVED******REMOVED******REMOVED*** Windows (PowerShell)

**Deployment-Script:** `staging-deploy.ps1`

```powershell
***REMOVED*** Standard-Deployment
.\scripts\staging-deploy.ps1

***REMOVED*** Clean-Deployment (alles neu)
.\scripts\staging-deploy.ps1 -Clean

***REMOVED*** Ohne Image-Build (schneller, nutzt existierende Images)
.\scripts\staging-deploy.ps1 -SkipBuild

***REMOVED*** Ohne Smoke-Tests
.\scripts\staging-deploy.ps1 -SkipTests

***REMOVED*** Hilfe anzeigen
.\scripts\staging-deploy.ps1 -Help
```

**Features:**
- ✅ Automatisches Setup aller Services
- ✅ Health-Checks für alle Container
- ✅ Database-Migration
- ✅ Pre-Deployment-Backup
- ✅ Smoke-Tests
- ✅ Detaillierte Fehlerbehandlung

***REMOVED******REMOVED******REMOVED*** Linux/macOS (Bash)

**Smoke-Tests:** `smoke-tests-staging.sh`

```bash
***REMOVED*** Alle Tests ausführen
./scripts/smoke-tests-staging.sh

***REMOVED*** Nur Health-Checks
./scripts/smoke-tests-staging.sh health

***REMOVED*** Nur Auth-Tests
./scripts/smoke-tests-staging.sh auth

***REMOVED*** Nur API-Tests
./scripts/smoke-tests-staging.sh api
```

**Features:**
- ✅ 15+ automatisierte Tests
- ✅ Health-Checks (PostgreSQL, Redis, Keycloak)
- ✅ OIDC-Konfiguration-Tests
- ✅ API-Endpoint-Tests
- ✅ Container-Status-Checks
- ✅ System-Resource-Checks

***REMOVED******REMOVED*** 🧪 Test-Kategorien

***REMOVED******REMOVED******REMOVED*** Infrastructure Tests
- PostgreSQL Health
- Redis Health
- Keycloak Health
- Container Status

***REMOVED******REMOVED******REMOVED*** Application Tests
- Backend API Health
- BFF Health
- Frontend Health
- API Documentation

***REMOVED******REMOVED******REMOVED*** OIDC/Auth Tests
- Realm Configuration
- Discovery Document
- JWKS Endpoint
- Token Flow (optional)

***REMOVED******REMOVED******REMOVED*** Data Layer Tests
- Database Tables
- Redis Read/Write
- Cache Operations

***REMOVED******REMOVED******REMOVED*** API Integration Tests
- CORS Headers
- Health Endpoints
- Customer API (optional)
- Sales Order CRUD (optional)

***REMOVED******REMOVED******REMOVED*** System Tests
- Disk Space
- Memory Usage
- Container Resources

***REMOVED******REMOVED*** 📊 Test-Ausgabe

**Erfolgreiche Tests:**
```
✅ PostgreSQL Health Check
✅ Redis Health Check
✅ Keycloak Health Check
...
🎉 All Smoke Tests Passed!
```

**Fehlgeschlagene Tests:**
```
✅ PostgreSQL Health Check
❌ Redis Health Check
⚠️  Some Smoke Tests Failed!
```

***REMOVED******REMOVED*** 🔧 Weitere Scripts

***REMOVED******REMOVED******REMOVED*** Database-Backup

```powershell
***REMOVED*** Manuelles Backup
docker exec valeo-staging-postgres pg_dump `
  -U valeo_staging `
  -Fc valeo_neuro_erp_staging `
  > backups/staging/manual-backup.dump
```

***REMOVED******REMOVED******REMOVED*** Database-Restore

```powershell
***REMOVED*** Backup wiederherstellen
docker exec -i valeo-staging-postgres pg_restore `
  -U valeo_staging `
  -d valeo_neuro_erp_staging `
  -c `
  < backups/staging/manual-backup.dump
```

***REMOVED******REMOVED******REMOVED*** Logs anzeigen

```powershell
***REMOVED*** Alle Services
docker-compose -f docker-compose.staging.yml logs -f

***REMOVED*** Einzelner Service
docker-compose -f docker-compose.staging.yml logs -f backend-staging

***REMOVED*** Letzte 100 Zeilen
docker-compose -f docker-compose.staging.yml logs --tail=100
```

***REMOVED******REMOVED******REMOVED*** Container neu starten

```powershell
***REMOVED*** Alle Container
docker-compose -f docker-compose.staging.yml restart

***REMOVED*** Einzelner Container
docker-compose -f docker-compose.staging.yml restart backend-staging
```

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Script-Ausführung blockiert (Windows)

```powershell
***REMOVED*** Execution-Policy temporär ändern
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\staging-deploy.ps1
```

***REMOVED******REMOVED******REMOVED*** Bash-Script nicht ausführbar (Linux/macOS)

```bash
***REMOVED*** Ausführbar machen
chmod +x scripts/smoke-tests-staging.sh
./scripts/smoke-tests-staging.sh
```

***REMOVED******REMOVED******REMOVED*** Docker-Fehler: "Cannot connect to Docker daemon"

```powershell
***REMOVED*** Docker Desktop starten (Windows)
***REMOVED*** Oder Docker-Service starten (Linux)
sudo systemctl start docker
```

***REMOVED******REMOVED******REMOVED*** Port bereits belegt

```powershell
***REMOVED*** Prüfen welcher Prozess Port 3001 nutzt
netstat -ano | findstr :3001

***REMOVED*** Prozess beenden (Windows)
taskkill /PID <PID> /F
```

***REMOVED******REMOVED*** 📚 Weitere Dokumentation

- [STAGING-DEPLOYMENT.md](../STAGING-DEPLOYMENT.md) - Vollständige Staging-Anleitung
- [DEPLOYMENT-PLAN.md](../DEPLOYMENT-PLAN.md) - Production-Deployment
- [PRODUCTION-AUTH-SETUP.md](../PRODUCTION-AUTH-SETUP.md) - Authentication-Setup

***REMOVED******REMOVED*** 🆘 Support

Bei Problemen:
1. Logs prüfen: `docker-compose -f docker-compose.staging.yml logs`
2. Container-Status: `docker-compose -f docker-compose.staging.yml ps`
3. Smoke-Tests: `.\scripts\smoke-tests-staging.sh`
4. Dokumentation: [STAGING-DEPLOYMENT.md](../STAGING-DEPLOYMENT.md)

---

**Version:** 3.0.0  
**Letzte Aktualisierung:** 2024-10-10
