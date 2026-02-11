# Staging-Deployment - VALEO-NeuroERP

**Version:** 3.0.0  
**Umgebung:** Docker Desktop auf Windows  
**OIDC:** Shared Keycloak mit Realm-Isolation  
**CI/CD:** GitHub Actions

---

## 🎯 Übersicht

Vollständige Staging-Umgebung für VALEO-NeuroERP mit:
- ✅ Production-ähnliche Konfiguration
- ✅ Docker Compose auf Windows/Docker Desktop
- ✅ Shared Keycloak (separates Realm "valeo-staging")
- ✅ Automatisches Deployment via GitHub Actions
- ✅ Automatisierte Smoke-Tests
- ✅ Health-Checks für alle Services
- ✅ Einfache Rollback-Strategie

---

## 📋 Voraussetzungen

### Software-Requirements

**Erforderlich:**
- Windows 10/11 (64-bit)
- Docker Desktop für Windows (Version 4.x+)
- Git für Windows
- PowerShell 5.1+ (oder PowerShell Core 7+)
- Node.js 20.x (für lokale Tests)
- Python 3.11+ (für Backend-Tests)

**Optional:**
- VS Code mit Docker-Extension
- Postman oder curl für API-Tests

### Hardware-Requirements

**Minimum:**
- CPU: 4 Cores
- RAM: 8 GB
- Disk: 20 GB freier Speicher

**Empfohlen:**
- CPU: 8 Cores
- RAM: 16 GB
- Disk: 50 GB freier Speicher (SSD)

---

## 🚀 Quick-Start

### 1. Repository klonen

```powershell
git clone https://github.com/your-org/VALEO-NeuroERP-3.0.git
cd VALEO-NeuroERP-3.0
```

### 2. Environment-Config kopieren

```powershell
Copy-Item .env.staging .env.staging.local
# Optional: Anpassungen in .env.staging.local vornehmen
```

### 3. Staging-Stack starten

```powershell
.\scripts\staging-deploy.ps1
```

### 4. Keycloak konfigurieren

Erster Start - Realm importieren:
```powershell
# Warten bis Keycloak läuft (ca. 60 Sekunden)
Start-Sleep -Seconds 60

# Browser öffnen
Start-Process "http://localhost:8180"
# Login: admin / admin123!
# Realm importieren: config/keycloak/realm-staging.json
```

### 5. Smoke-Tests ausführen

```powershell
.\scripts\smoke-tests-staging.sh
```

### 6. Zugriff

- **Frontend:** http://localhost:3001
- **Backend-API:** http://localhost:8001
- **Keycloak:** http://localhost:8180
- **pgAdmin:** http://localhost:5151
- **Redis Commander:** http://localhost:8181

**Test-User:**
- Admin: `test-admin` / `Test123!`
- User: `test-user` / `Test123!`
- Read-Only: `test-readonly` / `Test123!`

---

## 📁 Dateistruktur

```
VALEO-NeuroERP-3.0/
├── docker-compose.staging.yml          # Staging-Stack
├── .env.staging                        # Environment-Template
├── .env.staging.local                  # Lokale Overrides (gitignored)
├── config/
│   └── keycloak/
│       └── realm-staging.json          # Keycloak-Realm-Export
├── .github/
│   └── workflows/
│       └── deploy-staging.yml          # CI/CD-Workflow
├── scripts/
│   ├── staging-deploy.ps1              # Windows Deploy-Script
│   └── smoke-tests-staging.sh          # Automatisierte Tests
└── logs/
    └── staging/                        # Log-Dateien (auto-created)
```

---

## 🔧 Manuelle Deployment-Schritte

### 1. Services stoppen (falls laufend)

```powershell
docker-compose -f docker-compose.staging.yml down
```

### 2. Images aktualisieren

```powershell
docker-compose -f docker-compose.staging.yml pull
```

### 3. Services starten

```powershell
docker-compose -f docker-compose.staging.yml up -d
```

### 4. Logs überwachen

```powershell
# Alle Services
docker-compose -f docker-compose.staging.yml logs -f

# Einzelner Service
docker-compose -f docker-compose.staging.yml logs -f frontend-web
```

### 5. Health-Checks prüfen

```powershell
# PostgreSQL
docker exec valeo-staging-postgres pg_isready -U valeo_staging

# Redis
docker exec valeo-staging-redis redis-cli ping

# Keycloak
curl http://localhost:8180/health/ready

# Frontend
curl http://localhost:3001/healthz

# Backend-API
curl http://localhost:8001/healthz
```

---

## 🔐 Keycloak-Setup (Initial)

### Schritt 1: Realm importieren

**Option A: Via Admin-Console (empfohlen für erste Setup)**

1. Browser: http://localhost:8180
2. Login: `admin` / `admin123!`
3. Master-Realm → Realm-Dropdown → "Create Realm"
4. "Browse" → `config/keycloak/realm-staging.json` auswählen
5. "Create" klicken
6. ✅ Realm "valeo-staging" erstellt

**Option B: Via Docker-Volume (automatisch)**

Realm-Import ist bereits in `docker-compose.staging.yml` konfiguriert:
```yaml
volumes:
  - ./config/keycloak/realm-staging.json:/opt/keycloak/data/import/realm-staging.json
command: start-dev --import-realm
```

### Schritt 2: Client verifizieren

1. Realm "valeo-staging" auswählen
2. Clients → "valeo-erp-staging"
3. Settings prüfen:
   - Client ID: `valeo-erp-staging`
   - Access Type: `public`
   - Valid Redirect URIs: `http://localhost:3001/callback`
   - Web Origins: `http://localhost:3001`

### Schritt 3: Test-User verifizieren

1. Users → Liste prüfen:
   - `test-admin` (Roles: admin)
   - `test-user` (Roles: user, sales:write)
   - `test-readonly` (Roles: user, sales:read)

2. User-Details → Credentials:
   - Passwort: `Test123!`
   - Temporary: `OFF`

### Schritt 4: Scopes verifizieren

1. Client Scopes → Liste prüfen:
   - `sales:read`
   - `sales:write`
   - `sales:approve`
   - `sales:post`
   - `policy:read`
   - `policy:write`
   - `admin:all`

---

## 🧪 Testing-Guide

### Automatisierte Smoke-Tests

```bash
# Alle Tests ausführen
./scripts/smoke-tests-staging.sh

# Einzelne Tests
./scripts/smoke-tests-staging.sh health
./scripts/smoke-tests-staging.sh auth
./scripts/smoke-tests-staging.sh api
```

**Erwartete Ausgabe:**
```
✅ PostgreSQL Health Check: OK
✅ Redis Health Check: OK
✅ Keycloak Health Check: OK
✅ Frontend Health Check: OK
✅ Backend Health Check: OK
✅ OIDC Login Flow: OK
✅ API Sales Order CRUD: OK
✅ Token Refresh: OK
✅ Policy Engine: OK

🎉 All Smoke Tests Passed!
```

### Manuelle Test-Szenarien

#### 1. OIDC Login-Flow

1. Browser: http://localhost:3001
2. Redirect zu /login
3. Klick "Mit SSO anmelden"
4. Redirect zu Keycloak (http://localhost:8180)
5. Login: `test-user` / `Test123!`
6. Redirect zurück zu /callback
7. Redirect zu /dashboard
8. ✅ User eingeloggt

#### 2. Sales Order erstellen

1. Navigation: Sales → Orders → New
2. Kunde auswählen (Lookup)
3. Artikel hinzufügen (Lookup mit Auto-Fill)
4. Menge eingeben
5. Policy-Check: Preis < EK → Warnung (gelb)
6. Submit → Order erstellt
7. ✅ Order in Liste sichtbar

#### 3. Policy-Check testen

1. Order öffnen
2. Artikel-Preis auf 0 setzen
3. Policy-Check: → Blockierung (rot)
4. Submit-Button disabled
5. ✅ Policy verhindert Submit

#### 4. Folgebeleg erstellen

1. Sales Order öffnen
2. Status: "Approved"
3. BelegFlowPanel: "Create Delivery" klicken
4. Delivery-Editor öffnet mit kopierten Daten
5. Submit → Delivery erstellt
6. ✅ Delivery verlinkt mit Order

#### 5. Token-Refresh testen

1. Browser-Console öffnen
2. `localStorage.getItem('access_token')` → Token vorhanden
3. Token manuell ungültig machen (oder 15min warten)
4. API-Call durchführen (z.B. Order laden)
5. Network-Tab: 401 → Refresh → 200
6. ✅ Token automatisch erneuert

---

## 📊 Monitoring

### Health-Check-Endpoints

| Service | Endpoint | Erwartete Response |
|---------|----------|-------------------|
| Frontend | http://localhost:3001/healthz | 200 OK |
| Backend | http://localhost:8001/healthz | 200 OK |
| Keycloak | http://localhost:8180/health/ready | 200 OK |
| PostgreSQL | `pg_isready` (Docker) | "accepting connections" |
| Redis | `redis-cli ping` (Docker) | "PONG" |

### Log-Files

**Location:** `./logs/staging/`

```
logs/staging/
├── frontend.log          # Frontend-Logs
├── backend.log           # Backend-API-Logs
├── keycloak.log          # Keycloak-Logs
├── postgres.log          # PostgreSQL-Logs
└── redis.log             # Redis-Logs
```

**Logs anzeigen:**
```powershell
# Live-Logs (alle Services)
docker-compose -f docker-compose.staging.yml logs -f

# Logs in Datei
docker-compose -f docker-compose.staging.yml logs > logs/staging/all-services.log
```

### Docker-Container-Status

```powershell
# Container-Status
docker-compose -f docker-compose.staging.yml ps

# Container-Resource-Usage
docker stats
```

**Erwartete Container:**
```
NAME                          STATUS
valeo-staging-postgres        Up (healthy)
valeo-staging-redis           Up (healthy)
valeo-staging-keycloak        Up (healthy)
valeo-staging-backend         Up
valeo-staging-bff             Up
valeo-staging-frontend        Up
```

---

## 🐛 Troubleshooting

### Problem: Keycloak startet nicht

**Symptom:**
```
ERROR: Keycloak container exited with code 1
```

**Lösung:**
```powershell
# Logs prüfen
docker logs valeo-staging-keycloak

# Häufige Ursachen:
# 1. PostgreSQL noch nicht bereit → Wait-Script fehlt
# 2. Port 8180 bereits belegt → Port ändern
# 3. Realm-Import-Fehler → realm-staging.json prüfen

# Container neu starten
docker-compose -f docker-compose.staging.yml restart keycloak
```

### Problem: Frontend lädt nicht

**Symptom:**
```
ERR_CONNECTION_REFUSED on http://localhost:3001
```

**Lösung:**
```powershell
# 1. Container-Status prüfen
docker ps | findstr frontend

# 2. Logs prüfen
docker logs valeo-staging-frontend

# 3. Port-Konflikt prüfen
netstat -ano | findstr :3001

# 4. Container neu starten
docker-compose -f docker-compose.staging.yml restart frontend-web
```

### Problem: OIDC-Login schlägt fehl

**Symptom:**
```
Error: invalid_redirect_uri
```

**Lösung:**
1. Keycloak Admin-Console öffnen
2. Clients → valeo-erp-staging → Settings
3. Valid Redirect URIs prüfen:
   - `http://localhost:3001/callback` muss vorhanden sein
4. "Save" klicken
5. Frontend neu laden

### Problem: Database-Connection-Error

**Symptom:**
```
sqlalchemy.exc.OperationalError: connection refused
```

**Lösung:**
```powershell
# 1. PostgreSQL-Status prüfen
docker exec valeo-staging-postgres pg_isready

# 2. ENV-Variablen prüfen
docker exec valeo-staging-backend env | findstr DATABASE

# 3. Database existiert?
docker exec valeo-staging-postgres psql -U valeo_staging -c "\l"

# 4. Migration ausführen
docker exec valeo-staging-backend alembic upgrade head
```

### Problem: Policy-Engine funktioniert nicht

**Symptom:**
```
Policy-Check zeigt keine Warnungen/Blockierungen
```

**Lösung:**
```powershell
# 1. Backend-Logs prüfen
docker logs valeo-staging-backend | findstr policy

# 2. Policy-DB prüfen
docker exec valeo-staging-backend sqlite3 /app/data/policies.db ".tables"

# 3. Policies vorhanden?
curl http://localhost:8001/api/policies | jq .

# 4. Seed-Script ausführen
docker exec valeo-staging-backend python scripts/seed_policies.py
```

---

## 🔄 Rollback-Strategie

### Automatischer Rollback (GitHub Actions)

GitHub Actions erkennt Deployment-Fehler automatisch:
- Smoke-Tests schlagen fehl → Auto-Rollback
- Health-Checks nicht OK → Auto-Rollback

### Manueller Rollback

**Option 1: Auf letzte Version zurück**
```powershell
# 1. Aktuelle Version stoppen
docker-compose -f docker-compose.staging.yml down

# 2. Git auf letzten stabilen Commit zurücksetzen
git log --oneline  # Letzten stabilen Commit finden
git checkout <commit-hash>

# 3. Neu deployen
.\scripts\staging-deploy.ps1
```

**Option 2: Spezifische Image-Version**
```powershell
# docker-compose.staging.yml anpassen
# image: valeo-erp-frontend:3.0.0 → :2.9.0

docker-compose -f docker-compose.staging.yml up -d
```

**Option 3: Database-Rollback**
```powershell
# 1. Backup-Liste anzeigen
ls backups/postgresql/staging/

# 2. Backup wiederherstellen
docker exec valeo-staging-postgres pg_restore \
  -U valeo_staging \
  -d valeo_neuro_erp_staging \
  /backups/pre_deployment.dump

# 3. Alembic auf alte Version
docker exec valeo-staging-backend alembic downgrade <revision>
```

---

## 🤖 GitHub Actions Workflow

### Automatisches Deployment

**Trigger:**
- Push auf `develop`-Branch
- Manuell via GitHub UI (workflow_dispatch)

**Jobs:**
1. **Build**: Docker-Images bauen & pushen
2. **Test**: Unit-Tests & Lint-Checks
3. **Deploy**: Docker Compose auf Staging-Server
4. **Smoke-Tests**: Automatisierte Funktions-Tests
5. **Notify**: Slack/Email bei Fehler

### Workflow manuell starten

1. GitHub → Actions → "Deploy Staging"
2. "Run workflow" → Branch auswählen
3. "Run workflow" klicken
4. ✅ Deployment startet

### Workflow-Status prüfen

```powershell
# Via GitHub CLI
gh run list --workflow=deploy-staging.yml

# Logs anzeigen
gh run view <run-id> --log
```

---

## 📦 Database-Backups

### Automatische Backups

**Schedule:** Täglich um 02:00 Uhr (via Cron in Docker)

**Location:** `./backups/postgresql/staging/`

```
backups/postgresql/staging/
├── daily/
│   ├── 2024-10-10.dump.gz
│   ├── 2024-10-09.dump.gz
│   └── ...
└── pre_deployment/
    └── 2024-10-10-pre-v3.0.0.dump.gz
```

### Manuelle Backups

```powershell
# Backup erstellen
docker exec valeo-staging-postgres pg_dump \
  -U valeo_staging \
  -Fc \
  valeo_neuro_erp_staging \
  > backups/postgresql/staging/manual-$(Get-Date -Format "yyyy-MM-dd-HHmmss").dump

# Backup wiederherstellen
docker exec -i valeo-staging-postgres pg_restore \
  -U valeo_staging \
  -d valeo_neuro_erp_staging \
  -c \
  < backups/postgresql/staging/manual-2024-10-10-120000.dump
```

---

## 🔐 Security-Best-Practices

### Secrets Management

**NIEMALS committen:**
- `.env.staging.local` (gitignored)
- Passwords in plain-text
- API-Keys
- JWT-Secrets

**Verwenden:**
- Environment-Variablen
- Docker-Secrets (Swarm-Mode)
- Azure Key-Vault / AWS Secrets Manager (Production)

### Keycloak-Security

**Staging-Realm:**
- ✅ Separate Realm (Isolation von Production)
- ✅ Test-Users (keine echten User-Daten)
- ✅ SSL/TLS für External-Access (via Ingress/Reverse-Proxy)
- ⚠️ Admin-Password ändern! (Default: `admin123!`)

**Production-Realm:**
- ✅ Strong Passwords
- ✅ Two-Factor-Authentication (TOTP)
- ✅ Rate-Limiting
- ✅ SSL/TLS mandatory

---

## 📝 Staging vs. Production

| Feature | Staging | Production |
|---------|---------|------------|
| **Umgebung** | Docker Desktop (Windows) | Kubernetes-Cluster |
| **Ports** | 3001, 8001, 8180, ... | 80, 443 (HTTPS) |
| **OIDC** | Keycloak Realm "valeo-staging" | Keycloak Realm "valeo-production" |
| **Database** | PostgreSQL (Docker-Volume) | PostgreSQL (Managed DB) |
| **SSL/TLS** | Optional (localhost) | Mandatory (Let's Encrypt) |
| **Backups** | Täglich (lokal) | Stündlich (Cloud-Storage) |
| **Monitoring** | Health-Checks, Logs | Prometheus, Grafana, Alerts |
| **Deployment** | GitHub Actions (auto) | Blue-Green (manual approve) |
| **Rollback** | Automatisch bei Fehler | Manuell mit Approval |

---

## ✅ Pre-Deployment-Checklist

Vor jedem Staging-Deployment prüfen:

### Code-Quality
- [ ] Alle Unit-Tests passing
- [ ] Lint-Checks passing (0 Errors)
- [ ] TypeScript-Compile erfolgreich
- [ ] Code-Review durchgeführt

### Environment
- [ ] `.env.staging.local` aktuell
- [ ] Keycloak-Realm importiert
- [ ] Database-Migration tested
- [ ] Secrets nicht committed

### Infrastructure
- [ ] Docker Desktop läuft
- [ ] Genug Disk-Space (min. 10 GB frei)
- [ ] Alle Ports verfügbar (3001, 8001, 8180, ...)
- [ ] Firewall-Regeln OK

### Testing
- [ ] Smoke-Tests vorbereitet
- [ ] Test-Users funktionieren
- [ ] Rollback-Strategie bereit
- [ ] Backup erstellt

---

## 🎯 Success-Criteria

Deployment gilt als erfolgreich wenn:

### Technical-Success
- ✅ Alle Container running (6/6)
- ✅ Health-Checks grün
- ✅ Smoke-Tests passing (100%)
- ✅ Keine Errors in Logs (erste 10 Minuten)
- ✅ Database-Migration erfolgreich

### Functional-Success
- ✅ OIDC-Login funktioniert
- ✅ Sales-Order-Workflow funktioniert
- ✅ Policy-Engine funktioniert
- ✅ Token-Refresh funktioniert
- ✅ Folgebeleg-Flow funktioniert

### Performance-Success
- ✅ Frontend-Load < 3 Sekunden
- ✅ API-Response-Time < 500ms
- ✅ Memory-Usage < 4 GB gesamt
- ✅ CPU-Usage < 50%

---

## 📞 Support-Kontakte

### Bei Problemen:

**Technical Lead:**  
Name: [TBD]  
Email: [TBD]  
Slack: @tech-lead

**DevOps-Team:**  
Email: devops@valeo-neuro-erp.com  
Slack: #valeo-erp-devops

**On-Call-Hotline:**  
Phone: [TBD]  
Verfügbar: 24/7

---

## 📚 Weitere Dokumentation

- [PRODUCTION-AUTH-SETUP.md](./PRODUCTION-AUTH-SETUP.md) - Production-Authentication
- [DEPLOYMENT-PLAN.md](./DEPLOYMENT-PLAN.md) - Production-Deployment
- [SECURITY.md](./SECURITY.md) - Security-Guidelines
- [GO-LIVE-CHECKLIST.md](./GO-LIVE-CHECKLIST.md) - Production-Readiness

---

## 🔄 Changelog

### v3.0.0 (2024-10-10)
- ✅ Initial Staging-Deployment-Setup
- ✅ Docker-Compose-Stack
- ✅ Keycloak-Realm-Integration
- ✅ GitHub-Actions-Workflow
- ✅ Automatisierte Smoke-Tests
- ✅ PowerShell-Deploy-Script

---

**🚀 Staging-Deployment: READY! 🚀**


