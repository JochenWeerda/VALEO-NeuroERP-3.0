# VALEO NeuroERP - Scripts

Dieses Verzeichnis enthält Deployment-, Test- und Utility-Scripts für VALEO NeuroERP.

## 📁 Staging-Deployment

### Windows (PowerShell)

**Deployment-Script:** `staging-deploy.ps1`

```powershell
# Standard-Deployment
.\scripts\staging-deploy.ps1

# Clean-Deployment (alles neu)
.\scripts\staging-deploy.ps1 -Clean

# Ohne Image-Build (schneller, nutzt existierende Images)
.\scripts\staging-deploy.ps1 -SkipBuild

# Ohne Smoke-Tests
.\scripts\staging-deploy.ps1 -SkipTests

# Hilfe anzeigen
.\scripts\staging-deploy.ps1 -Help
```

**Features:**
- ✅ Automatisches Setup aller Services
- ✅ Health-Checks für alle Container
- ✅ Database-Migration
- ✅ Pre-Deployment-Backup
- ✅ Smoke-Tests
- ✅ Detaillierte Fehlerbehandlung

### Linux/macOS (Bash)

**Smoke-Tests:** `smoke-tests-staging.sh`

```bash
# Alle Tests ausführen
./scripts/smoke-tests-staging.sh

# Nur Health-Checks
./scripts/smoke-tests-staging.sh health

# Nur Auth-Tests
./scripts/smoke-tests-staging.sh auth

# Nur API-Tests
./scripts/smoke-tests-staging.sh api
```

**Features:**
- ✅ 15+ automatisierte Tests
- ✅ Health-Checks (PostgreSQL, Redis, Keycloak)
- ✅ OIDC-Konfiguration-Tests
- ✅ API-Endpoint-Tests
- ✅ Container-Status-Checks
- ✅ System-Resource-Checks

## 🧪 Test-Kategorien

### Infrastructure Tests
- PostgreSQL Health
- Redis Health
- Keycloak Health
- Container Status

### Application Tests
- Backend API Health
- BFF Health
- Frontend Health
- API Documentation

### OIDC/Auth Tests
- Realm Configuration
- Discovery Document
- JWKS Endpoint
- Token Flow (optional)

### Data Layer Tests
- Database Tables
- Redis Read/Write
- Cache Operations

### API Integration Tests
- CORS Headers
- Health Endpoints
- Customer API (optional)
- Sales Order CRUD (optional)

### System Tests
- Disk Space
- Memory Usage
- Container Resources

## 📊 Test-Ausgabe

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

## 🔧 Weitere Scripts

### Database-Backup

```powershell
# Manuelles Backup
docker exec valeo-staging-postgres pg_dump `
  -U valeo_staging `
  -Fc valeo_neuro_erp_staging `
  > backups/staging/manual-backup.dump
```

### Database-Restore

```powershell
# Backup wiederherstellen
docker exec -i valeo-staging-postgres pg_restore `
  -U valeo_staging `
  -d valeo_neuro_erp_staging `
  -c `
  < backups/staging/manual-backup.dump
```

### Logs anzeigen

```powershell
# Alle Services
docker-compose -f docker-compose.staging.yml logs -f

# Einzelner Service
docker-compose -f docker-compose.staging.yml logs -f backend-staging

# Letzte 100 Zeilen
docker-compose -f docker-compose.staging.yml logs --tail=100
```

### Container neu starten

```powershell
# Alle Container
docker-compose -f docker-compose.staging.yml restart

# Einzelner Container
docker-compose -f docker-compose.staging.yml restart backend-staging
```

## 🐛 Troubleshooting

### Script-Ausführung blockiert (Windows)

```powershell
# Execution-Policy temporär ändern
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\staging-deploy.ps1
```

### Bash-Script nicht ausführbar (Linux/macOS)

```bash
# Ausführbar machen
chmod +x scripts/smoke-tests-staging.sh
./scripts/smoke-tests-staging.sh
```

### Docker-Fehler: "Cannot connect to Docker daemon"

```powershell
# Docker Desktop starten (Windows)
# Oder Docker-Service starten (Linux)
sudo systemctl start docker
```

### Port bereits belegt

```powershell
# Prüfen welcher Prozess Port 3001 nutzt
netstat -ano | findstr :3001

# Prozess beenden (Windows)
taskkill /PID <PID> /F
```

## 📚 Weitere Dokumentation

- [STAGING-DEPLOYMENT.md](../STAGING-DEPLOYMENT.md) - Vollständige Staging-Anleitung
- [DEPLOYMENT-PLAN.md](../DEPLOYMENT-PLAN.md) - Production-Deployment
- [PRODUCTION-AUTH-SETUP.md](../PRODUCTION-AUTH-SETUP.md) - Authentication-Setup

## 🆘 Support

Bei Problemen:
1. Logs prüfen: `docker-compose -f docker-compose.staging.yml logs`
2. Container-Status: `docker-compose -f docker-compose.staging.yml ps`
3. Smoke-Tests: `.\scripts\smoke-tests-staging.sh`
4. Dokumentation: [STAGING-DEPLOYMENT.md](../STAGING-DEPLOYMENT.md)

---

**Version:** 3.0.0  
**Letzte Aktualisierung:** 2024-10-10
