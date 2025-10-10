# Lokales Staging-Deployment - Quick Guide

**Datum:** 2024-10-10  
**Umgebung:** Windows/Docker Desktop  
**Dauer:** ~10 Minuten

---

## 🎯 Übersicht

Das Staging-Deployment läuft **lokal auf deinem Windows-PC** mit Docker Desktop.

**GitHub Actions** validiert nur den Code (Build & Test, Security Scan).  
**PowerShell-Script** deployt die Staging-Umgebung lokal.

---

## ✅ Voraussetzungen

**Installiert:**
- ✅ Docker Desktop für Windows (läuft)
- ✅ Git für Windows
- ✅ PowerShell 5.1+

**Hardware:**
- CPU: 4+ Cores
- RAM: 8+ GB
- Disk: 20+ GB frei

---

## 🚀 Staging-Umgebung starten

### Option 1: PowerShell-Script (Empfohlen)

```powershell
# Im Projektverzeichnis
.\scripts\staging-deploy.ps1
```

**Das Script:**
- ✅ Prüft Docker
- ✅ Erstellt Backup
- ✅ Baut Docker-Images
- ✅ Startet alle Services
- ✅ Wartet auf Health-Checks
- ✅ Führt Smoke-Tests aus

**Dauer:** ~10 Minuten

### Option 2: Manuell (für Experten)

```powershell
# Services starten
docker-compose -f docker-compose.staging.yml up -d

# Warten auf Services (~2 Minuten)
Start-Sleep -Seconds 120

# Smoke-Tests (Git Bash erforderlich)
./scripts/smoke-tests-staging.sh
```

---

## 🌐 Zugriff auf Staging

Nach erfolgreichem Start:

| Service | URL | Login |
|---------|-----|-------|
| **Frontend** | http://localhost:3001 | test-admin / Test123! |
| **Backend API** | http://localhost:8001/docs | - |
| **Keycloak** | http://localhost:8180 | admin / admin123! |
| **pgAdmin** | http://localhost:5151 | admin@valeo-staging.local / admin123! |
| **Redis Commander** | http://localhost:8181 | admin / admin123! |

### Test-User

| Username | Password | Rolle |
|----------|----------|-------|
| test-admin | Test123! | Administrator (alle Rechte) |
| test-user | Test123! | User (sales:read, sales:write) |
| test-sales-manager | Test123! | Sales Manager (+ approve) |
| test-readonly | Test123! | Read-Only (nur lesen) |

---

## 🧪 Funktions-Tests

### 1. Login-Test

```
1. Browser: http://localhost:3001
2. Klick "Mit SSO anmelden"
3. Login: test-admin / Test123!
4. ✅ Dashboard wird angezeigt
```

### 2. Sales-Order-Test

```
1. Navigation: Sales → Orders → New
2. Kunde auswählen (Lookup)
3. Artikel hinzufügen
4. Menge eingeben
5. Submit
6. ✅ Order erstellt
```

### 3. Policy-Test

```
1. Order öffnen
2. Preis auf 0 setzen
3. ✅ Warnung wird angezeigt (rot)
4. ✅ Submit-Button disabled
```

---

## 🛠️ Management

### Services stoppen

```powershell
docker-compose -f docker-compose.staging.yml down
```

### Services neu starten

```powershell
docker-compose -f docker-compose.staging.yml restart
```

### Logs anzeigen

```powershell
# Alle Services
docker-compose -f docker-compose.staging.yml logs -f

# Einzelner Service
docker-compose -f docker-compose.staging.yml logs -f frontend-staging
```

### Container-Status

```powershell
docker-compose -f docker-compose.staging.yml ps
```

**Erwartete Container:**
```
valeo-staging-postgres     Up (healthy)
valeo-staging-redis        Up (healthy)
valeo-staging-keycloak     Up (healthy)
valeo-staging-backend      Up
valeo-staging-bff          Up
valeo-staging-frontend     Up
valeo-staging-pgadmin      Up
valeo-staging-redis-commander Up
```

---

## 🐛 Troubleshooting

### Problem: "Docker is not running"

**Lösung:**
```
1. Docker Desktop öffnen
2. Warten bis "Engine running"
3. Script neu starten
```

### Problem: Port bereits belegt

**Symptom:**
```
Error: port 3001 already in use
```

**Lösung:**
```powershell
# Prozess finden
netstat -ano | findstr :3001

# Prozess beenden (Vorsicht: PID ersetzen!)
taskkill /PID <PID> /F

# Oder anderen Port verwenden (docker-compose.staging.yml anpassen)
```

### Problem: Keycloak startet nicht

**Lösung:**
```powershell
# Logs prüfen
docker logs valeo-staging-keycloak

# Neustart
docker-compose -f docker-compose.staging.yml restart keycloak-staging

# Warten (~60 Sekunden)
Start-Sleep -Seconds 60
```

### Problem: Frontend nicht erreichbar

**Lösung:**
```powershell
# Container-Status prüfen
docker ps | findstr frontend

# Neustart
docker-compose -f docker-compose.staging.yml restart frontend-staging

# Logs prüfen
docker logs valeo-staging-frontend
```

---

## 🔄 Update / Neu-Deployment

Nach Code-Änderungen:

```powershell
# 1. Änderungen pullen
git pull origin develop

# 2. Services stoppen
docker-compose -f docker-compose.staging.yml down

# 3. Neu deployen
.\scripts\staging-deploy.ps1
```

**Oder nur Images neu bauen:**

```powershell
# Images neu bauen
docker-compose -f docker-compose.staging.yml build --no-cache

# Services neu starten
docker-compose -f docker-compose.staging.yml up -d
```

---

## 📊 GitHub Actions CI/CD

**Workflow läuft automatisch bei Push auf `develop`:**

**Was wird geprüft:**
- ✅ Dependencies Installation
- ✅ TypeScript Compile
- ✅ Lint Checks
- ✅ Unit Tests
- ✅ Security Scan (Trivy, TruffleHog)

**Workflow-URL:**
```
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions
```

**Nach erfolgreichem CI/CD:**
```
✅ Code ist validiert
✅ Security-Checks bestanden
🚀 Bereit für lokales Deployment
```

---

## 💾 Backup & Restore

### Backup erstellen

```powershell
# Automatisches Backup (via Script)
.\scripts\staging-deploy.ps1  # Erstellt Pre-Deployment-Backup

# Manuelles Backup
docker exec valeo-staging-postgres pg_dump `
  -U valeo_staging `
  -Fc valeo_neuro_erp_staging `
  > backups/staging/backup-$(Get-Date -Format "yyyy-MM-dd-HHmmss").dump
```

### Backup wiederherstellen

```powershell
# Backup-Datei auswählen
$backupFile = "backups/staging/backup-2024-10-10-120000.dump"

# Wiederherstellen
Get-Content $backupFile | docker exec -i valeo-staging-postgres pg_restore `
  -U valeo_staging `
  -d valeo_neuro_erp_staging `
  -c
```

---

## 📚 Weiterführende Dokumentation

- **STAGING-DEPLOYMENT.md** - Vollständige Anleitung (688 Zeilen)
- **STAGING-DEPLOYMENT-QUICKSTART.md** - Quick-Start-Guide
- **GITHUB-ACTIONS-STAGING-SETUP.md** - GitHub Actions Details
- **scripts/README.md** - Scripts-Dokumentation

---

## 🎯 Checkliste

**Vor dem Start:**
- [ ] Docker Desktop läuft
- [ ] Genug Disk-Space (20+ GB)
- [ ] Ports frei (3001, 8001, 8180, etc.)

**Nach dem Start:**
- [ ] Alle 8 Container laufen
- [ ] Health-Checks grün
- [ ] Frontend erreichbar (http://localhost:3001)
- [ ] Login funktioniert (test-admin / Test123!)
- [ ] Smoke-Tests bestanden

---

## 🆘 Support

**Bei Problemen:**
1. Logs prüfen: `docker-compose -f docker-compose.staging.yml logs`
2. Container-Status: `docker-compose -f docker-compose.staging.yml ps`
3. Dokumentation: STAGING-DEPLOYMENT.md
4. Script neu starten: `.\scripts\staging-deploy.ps1 -Clean`

---

**🚀 READY FOR LOCAL STAGING DEPLOYMENT! 🎯**

**Nächster Schritt:**
```powershell
.\scripts\staging-deploy.ps1
```

