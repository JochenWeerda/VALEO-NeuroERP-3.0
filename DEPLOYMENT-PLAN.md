# VALEO-NeuroERP 3.0 - Deployment-Plan

**Version:** 3.0.0  
**Deployment-Datum:** [TBD]  
**Deployment-Fenster:** [TBD] - [TBD]  
**Deployment-Typ:** Blue-Green mit Zero-Downtime

---

## 📅 Timeline

### T-7 Tage: Vorbereitung
- ✅ Alle TODOs abgeschlossen (31/31)
- ✅ Code-Review durchgeführt
- ✅ Security-Scans bestanden
- [ ] Stakeholder-Approval eingeholt
- [ ] Maintenance-Window geplant
- [ ] On-Call-Team informiert

### T-3 Tage: Staging-Deployment
- [ ] Deploy to Staging (siehe [STAGING-DEPLOYMENT.md](./STAGING-DEPLOYMENT.md))
  ```powershell
  .\scripts\staging-deploy.ps1
  ```
- [ ] Smoke-Tests durchführen
  ```bash
  ./scripts/smoke-tests-staging.sh
  ```
- [ ] Performance-Tests durchführen
- [ ] UAT mit Key-Users (Test-User: test-admin, test-user, test-readonly)
- [ ] Findings dokumentieren
- [ ] Staging-URLs verifizieren:
  - Frontend: http://localhost:3001
  - Backend Modul: http://localhost:8001
  - Keycloak: http://localhost:8180

### T-1 Tag: Final-Check
- [ ] PRE-DEPLOYMENT-CHECK.md durchgehen
- [ ] Rollback-Plan verifizieren
- [ ] Backup erstellen
- [ ] Emergency-Contacts aktualisieren
- [ ] Go/No-Go-Meeting

### T-0 (Deployment-Tag)

#### 08:00 - Vorbereitung
- [ ] On-Call-Team on standby
- [ ] Monitoring-Dashboards geöffnet
- [ ] Emergency-Contacts bereit
- [ ] Final Backup erstellt

#### 09:00 - Database-Migration
```bash
# 1. Safety Backup
./scripts/backup-db.sh

# 2. Apply Migrations
alembic upgrade head

# 3. Verify Tables
psql -h $DB_HOST -U $DB_USER -d valeo_erp -c "\dt"
```

#### 10:00 - Staging-Deploy (Final Test)
```bash
helm upgrade --install valeo-erp-staging ./k8s/helm/valeo-erp \
  --namespace staging \
  --set image.tag=3.0.0 \
  --wait
```

#### 10:30 - Smoke-Tests auf Staging
```bash
# Run automated smoke tests
npm run test:smoke:staging
```

#### 11:00 - Go/No-Go-Decision
**Meeting mit:**
- Technical Lead
- Business Owner
- On-Call-Team

**Decision Criteria:**
- ✅ Staging-Tests passing
- ✅ Database-Migration successful
- ✅ No critical bugs
- ✅ On-Call-Team ready

#### 11:30 - Production-Deploy (Blue-Green)

**Step 1: Deploy Green**
```bash
# Deploy new version as "green"
helm upgrade --install valeo-erp-production ./k8s/helm/valeo-erp \
  --namespace production \
  --set image.tag=3.0.0 \
  --set replicaCount=3 \
  --set labels.version=green \
  --wait
```

**Step 2: Verify Green**
```bash
# Health-Checks
kubectl get pods -n production -l version=green
curl https://erp-green.valeo.example.com/healthz
curl https://erp-green.valeo.example.com/readyz

# Smoke-Tests on Green
npm run test:smoke:production-green
```

**Step 3: Cutover Traffic (12:00)**
```bash
# Switch traffic from Blue to Green
kubectl patch service valeo-erp -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Verify Traffic
curl https://erp.valeo.example.com/healthz
```

**Step 4: Monitor (12:00 - 13:00)**
- Watch Metrics (Error-Rate, Latency, Connections)
- Watch Logs (Errors, Warnings)
- Monitor SSE-Reconnections
- Check User-Feedback

**Step 5: Cleanup Blue (13:00)**
```bash
# If Green stable for 1h → Remove Blue
kubectl delete deployment valeo-erp-blue -n production
```

#### 14:00 - Post-Deployment-Verification
- [ ] All services running
- [ ] Metrics normal
- [ ] No errors in logs
- [ ] SSE-Connections stable
- [ ] User-Feedback positive

#### 15:00 - Sign-Off & Communication
- [ ] Deployment-Report erstellt
- [ ] Stakeholder informiert
- [ ] Post-Mortem geplant (in 1 Woche)

---

## 🚨 Rollback-Procedure

### Rollback-Trigger
**Immediate Rollback wenn:**
- Error-Rate > 5%
- P95-Latency > 2000ms
- Critical Bug (Data-Loss, Security)
- Service Down > 5 Minuten

### Rollback-Steps

**Option 1: Helm Rollback (bevorzugt)**
```bash
# 1. Rollback to previous version
helm rollback valeo-erp-production -n production

# 2. Verify
kubectl get pods -n production
curl https://erp.valeo.example.com/healthz

# 3. Database Rollback (falls nötig)
alembic downgrade -1
```

**Option 2: Blue-Cutover (schnell)**
```bash
# 1. Switch traffic back to Blue
kubectl patch service valeo-erp -n production \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# 2. Verify
curl https://erp.valeo.example.com/healthz
```

**Option 3: Full Restore (Notfall)**
```bash
# 1. Restore Database from Backup
./scripts/restore-db.sh /backups/postgresql/daily/pre_deployment.sql.gz

# 2. Deploy old version
helm upgrade --install valeo-erp-production ./k8s/helm/valeo-erp \
  --namespace production \
  --set image.tag=2.9.0 \
  --wait
```

### Rollback-Communication
1. **Immediate:** Slack-Alert in #valeo-erp-alerts
2. **Within 15min:** Email an Stakeholder
3. **Within 1h:** Post-Mortem-Meeting planen

---

## 📊 Success-Criteria

### Technical-Success
- ✅ All pods running (3/3)
- ✅ Error-Rate < 1%
- ✅ P95-Latency < 500ms
- ✅ SSE-Connections stable
- ✅ No memory-leaks
- ✅ Database-Migration successful

### Business-Success
- ✅ Zero-Downtime achieved
- ✅ All critical workflows functional
- ✅ User-Feedback positive
- ✅ No data-loss

### Compliance-Success
- ✅ GDPR-Compliance verified
- ✅ Audit-Trail functional
- ✅ Security-Scans passed
- ✅ Backups working

---

## 📞 Communication-Plan

### Pre-Deployment (T-3 Tage)
**Email an:**
- All Users
- Stakeholders
- Support-Team

**Inhalt:**
- Deployment-Datum & Zeit
- Erwartete Downtime (0 Minuten)
- Neue Features
- Known-Issues

### During-Deployment (T-0)
**Slack #valeo-erp-status:**
- 09:00: "Deployment started"
- 10:00: "Database migration completed"
- 11:30: "Green deployment started"
- 12:00: "Traffic cutover to green"
- 13:00: "Blue cleanup completed"
- 14:00: "Deployment successful"

### Post-Deployment (T+1 Tag)
**Email an:**
- All Users
- Stakeholders

**Inhalt:**
- Deployment erfolgreich
- Neue Features verfügbar
- Dokumentation-Links
- Support-Kontakte

---

## 🔍 Monitoring-Checklist

### Erste Stunde (kritisch)
- [ ] Error-Rate < 1%
- [ ] P95-Latency < 500ms
- [ ] SSE-Connections: 100+ aktiv
- [ ] Memory-Usage: < 1 GB pro Pod
- [ ] CPU-Usage: < 50%

### Erste 24 Stunden
- [ ] No critical bugs
- [ ] No data-loss
- [ ] Backups successful
- [ ] User-Feedback positiv

### Erste Woche
- [ ] System stable
- [ ] Performance normal
- [ ] No regressions
- [ ] Support-Tickets normal

---

## 📝 Post-Deployment-Tasks

### Sofort
- [ ] Deployment-Report erstellen
- [ ] Stakeholder informieren
- [ ] Known-Issues dokumentieren

### In 1 Tag
- [ ] User-Feedback auswerten
- [ ] Quick-Fixes priorisieren
- [ ] Metrics analysieren

### In 1 Woche
- [ ] Post-Mortem-Meeting
- [ ] Lessons-Learned dokumentieren
- [ ] Process-Improvements identifizieren
- [ ] Next-Sprint planen

---

## ✅ Sign-Off

**Deployment-Plan reviewed by:**

- [ ] Technical Lead: _______________
- [ ] Business Owner: _______________
- [ ] On-Call-Lead: _______________
- [ ] Security Officer: _______________

**Date:** _______________

---

**🚀 Ready for Deployment! 🚀**

---

## 🐳 Docker Production Ready Configuration

### ✅ 1. Network Isolation
- **Status:** ✅ Konfiguriert
- Alle Services werden über `docker compose up` aus dem gleichen Compose-Projekt gestartet
- Automatisches Landing im gleichen Default-Netzwerk (`valeo-network`)
- Postgres ist NICHT separat (extern) gestartet, sondern als Service in docker-compose.yml

### ✅ 2. Rollen & Connection Strings
- **Status:** ✅ Konfiguriert
- `POSTGRES_USER`: `valeo_dev` (nicht `postgres`)
- `POSTGRES_PASSWORD`: `valeo_dev_2024`
- **Im Container:** Host immer **Service-Name** (`postgres`)
- **Vom Host aus:** Host immer `localhost` (wenn Port gemappt)

**Connection Strings:**
- Backend: `postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp`
- Redis: `redis://redis:6379/0`

### ✅ 3. Health Checks
- **Postgres:** `pg_isready` mit korrektem User/DB
- **Keycloak:** `/health/ready` Endpoint via curl
- **Backend:** `/api/v1/health` Endpoint inkl. Alembic-Migrationscheck

### ✅ 4. Abhängigkeiten (depends_on)
- Backend startet erst wenn Postgres UND Redis `service_healthy` sind
- Keycloak startet erst wenn Postgres `service_healthy` ist

### ✅ 5. Schema-Version-Check
- Backend Health-Check prüft `alembic_version` Tabelle:
  - Existenz der Tabelle
  - Mindestens ein Migrationseintrag
  - Aktuelle Version wird im Health-Response angezeigt

### ⚠️ Hinweis zu Ports
- Postgres Port 5432 ist nur gemappt wenn Host-Zugriff nötig ist
- Für rein interne Docker-Kommunikation kann `ports:` entfernt werden

### 🚀 Schnellstart
```bash
# Start aller Services (inkl. Postgres)
docker compose up -d

# Status prüfen
docker compose ps

# Logs
docker compose logs -f backend

# Health-Check
curl http://localhost:8000/api/v1/health
```

---

**🚀 Ready for Docker Deployment! 🚀**


