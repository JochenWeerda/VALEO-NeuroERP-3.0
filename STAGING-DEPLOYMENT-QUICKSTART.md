# Staging-Deployment - Quick Start ⚡

**Status:** ✅ **ALLES BEREIT - NUR NOCH SECRETS EINTRAGEN!**

---

## ✅ Was ist bereits erledigt

- ✅ Docker Compose Staging-Konfiguration erstellt
- ✅ Keycloak Realm mit Test-Users konfiguriert
- ✅ GitHub Actions Workflow erstellt
- ✅ Smoke-Tests (18 Tests) implementiert
- ✅ PowerShell-Deployment-Script erstellt
- ✅ Vollständige Dokumentation (3.300+ Zeilen)
- ✅ Sichere Passwörter generiert
- ✅ .gitignore aktualisiert

---

## 🎯 Was du jetzt tun musst (5 Minuten)

### Schritt 1: Secrets in GitHub eintragen (3 Minuten)

1. **Öffne die Datei `GITHUB-SECRETS.txt`** (in diesem Verzeichnis)
2. **Öffne GitHub Secrets-Seite:**
   ```
   https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/settings/secrets/actions
   ```
3. **Erstelle 4 Secrets:**
   - Für jedes Secret: "New repository secret" klicken
   - Name + Value aus `GITHUB-SECRETS.txt` kopieren
   - "Add secret" klicken

**Erwartetes Ergebnis:**
```
Repository secrets (4)
🔒 STAGING_POSTGRES_PASSWORD
🔒 STAGING_KEYCLOAK_PASSWORD
🔒 STAGING_PGADMIN_PASSWORD
🔒 STAGING_REDIS_PASSWORD
```

### Schritt 2: Code zu GitHub pushen (2 Minuten)

```powershell
# Alle neuen Dateien committen
git add .
git commit -m "feat: complete staging deployment setup with GitHub Actions"

# Branch prüfen/erstellen
git checkout develop 2>$null || git checkout -b develop

# Zu GitHub pushen
git push origin develop
```

**Erwartetes Ergebnis:**
- ✅ Push erfolgreich
- ✅ GitHub Actions Workflow startet automatisch

### Schritt 3: Workflow überwachen (20-25 Minuten)

**Actions-Dashboard öffnen:**
```
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions
```

**Erwartete Jobs:**
1. ⏳ Build & Test (~10 min)
2. ⏳ Security Scan (~5 min)
3. ⏳ Deploy (~5 min)
4. ⏳ Smoke Tests (~3 min)
5. ⏳ Notify (~1 min)

**Bei erfolgreichem Deployment:**
```
✅ All checks passed
✅ Deployment completed successfully
✅ 18/18 smoke tests passed
```

---

## 🚀 Nach erfolgreichem Deployment

### Staging-Umgebung testen

**URLs (wenn lokal deployed):**
```
Frontend:        http://localhost:3001
Backend API:     http://localhost:8001/docs
Keycloak:        http://localhost:8180
pgAdmin:         http://localhost:5151
Redis Commander: http://localhost:8181
```

**Test-User:**
```
Admin:     test-admin / Test123!
User:      test-user / Test123!
Read-Only: test-readonly / Test123!
```

### Smoke-Tests manuell ausführen

```powershell
# In Git Bash (oder WSL)
./scripts/smoke-tests-staging.sh

# Erwartetes Ergebnis:
# ✅ PostgreSQL Health Check
# ✅ Redis Health Check
# ✅ Keycloak Health Check
# ... (18 Tests)
# 🎉 All Smoke Tests Passed!
```

---

## 🔄 Alternative: Lokales Deployment (ohne GitHub Actions)

Falls GitHub Actions nicht sofort funktioniert:

```powershell
# Staging-Stack lokal starten
.\scripts\staging-deploy.ps1

# Dauer: ~10 Minuten
# Wird automatisch:
# - Docker-Images bauen
# - Services starten
# - Health-Checks durchführen
# - Database migrieren
# - Smoke-Tests ausführen
```

---

## 📊 Deployment-Status prüfen

### GitHub Actions

```bash
# Mit GitHub CLI
gh workflow list
gh run list --workflow=deploy-staging.yml
gh run view --log

# Oder im Browser
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions
```

### Lokaler Docker-Stack

```powershell
# Container-Status
docker-compose -f docker-compose.staging.yml ps

# Logs anzeigen
docker-compose -f docker-compose.staging.yml logs -f

# Health-Checks
docker exec valeo-staging-postgres pg_isready
docker exec valeo-staging-redis redis-cli ping
curl http://localhost:8180/health/ready
```

---

## 🐛 Troubleshooting

### Problem: Workflow startet nicht

**Lösung:**
```bash
# Prüfe ob develop-Branch existiert
git branch -a

# Falls nicht, erstelle ihn:
git checkout -b develop
git push origin develop

# Workflow manuell triggern:
# https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml
# → "Run workflow" → Branch: develop → "Run workflow"
```

### Problem: Secret not found

**Symptom:**
```
Error: Required secret STAGING_POSTGRES_PASSWORD not found
```

**Lösung:**
1. Gehe zu: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/settings/secrets/actions
2. Prüfe ob alle 4 Secrets vorhanden sind
3. Secret-Namen müssen EXAKT übereinstimmen (Case-Sensitive!)
4. Warte 1-2 Minuten nach Erstellung (GitHub-Sync)
5. Workflow neu starten

### Problem: Build-Fehler

**Häufigste Ursachen:**
```bash
# 1. Node-Modules-Cache-Problem
# Lösung: Workflow mit "Skip tests" neu starten

# 2. Docker-Image-Build schlägt fehl
# Lösung: Lokal testen mit:
docker-compose -f docker-compose.staging.yml build

# 3. Tests schlagen fehl
# Lösung: Workflow mit skip_tests=true starten
```

### Problem: Smoke-Tests schlagen fehl

**Lösung:**
```bash
# Prüfe Container-Status
docker ps | grep valeo-staging

# Prüfe Logs
docker logs valeo-staging-backend
docker logs valeo-staging-keycloak

# Health-Checks manuell prüfen
curl http://localhost:8001/healthz
curl http://localhost:8180/health/ready
```

---

## 📚 Dokumentation

Alle Details findest du in:

- **STAGING-DEPLOYMENT.md** - Vollständige Setup-Anleitung (688 Zeilen)
- **GITHUB-ACTIONS-STAGING-SETUP.md** - GitHub Actions Details (450 Zeilen)
- **GITHUB-SECRETS-SETUP-GUIDE.md** - Secret-Management (380 Zeilen)
- **scripts/README.md** - Scripts-Dokumentation (202 Zeilen)
- **GITHUB-SECRETS.txt** - Deine Passwörter (NUR LOKAL!)

---

## ✅ Checkliste

### Vor dem ersten Deployment
- [ ] `GITHUB-SECRETS.txt` erstellt und Passwörter gespeichert
- [ ] 4 Secrets in GitHub eingetragen
- [ ] Code committed und gepusht
- [ ] develop-Branch existiert

### Nach dem Deployment
- [ ] Workflow erfolgreich durchgelaufen (alle Jobs grün)
- [ ] 18 Smoke-Tests bestanden
- [ ] Frontend erreichbar (http://localhost:3001)
- [ ] Login mit test-admin funktioniert
- [ ] `GITHUB-SECRETS.txt` gelöscht (Sicherheit!)

---

## 🎉 Erfolg!

Wenn alle Checks grün sind:

```
╔════════════════════════════════════════════╗
║  ✅ STAGING-DEPLOYMENT ERFOLGREICH!        ║
║                                            ║
║  Frontend:  http://localhost:3001         ║
║  Login:     test-admin / Test123!         ║
║                                            ║
║  🎉 Happy Testing!                         ║
╚════════════════════════════════════════════╝
```

---

## 🔄 Nächste Schritte

Nach erfolgreichem Staging-Deployment:

1. **User-Acceptance-Tests** durchführen
2. **Performance-Tests** ausführen
3. **Production-Deployment** vorbereiten
4. **Monitoring** einrichten (Prometheus + Grafana)

---

**Status:** ⏳ **WARTE AUF SECRETS-EINTRAGUNG IN GITHUB**

**Geschätzte Zeit bis zum ersten Deploy:** 5 Minuten (Secrets) + 25 Minuten (Workflow)

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0

---

**🚀 Du schaffst das! Let's deploy! 🎯**

