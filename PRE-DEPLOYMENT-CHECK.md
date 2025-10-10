# Pre-Deployment-Check für VALEO-NeuroERP 3.0

**Datum:** 2025-10-09  
**Version:** 3.0.0  
**Ziel-Environment:** Production

---

## ✅ Phase 1: Code & Build

### 1.1 Code-Qualität
- [x] **Alle Tests passing**
  - Unit-Tests: ✅
  - E2E-Tests: ✅ 30+ Playwright-Tests
  - Load-Tests: ✅ k6 (API + SSE)
  - Contract-Tests: ✅ OpenAPI-Validator

- [x] **Linter-Clean**
  - TypeScript: ✅ 0 Errors
  - Python: ✅ Type-Hints vorhanden
  - ESLint: ✅ No Warnings

- [x] **Security-Scans**
  - OWASP ZAP: ✅ Workflow konfiguriert
  - Trivy: ✅ Container-Scan
  - Bandit: ✅ Python-Security
  - Safety: ✅ Dependency-Check
  - Grype: ✅ Vulnerability-Scan

### 1.2 Build-Artefakte
- [x] **Docker-Image**
  - Multi-stage Build: ✅
  - Non-root User: ✅
  - Hardened: ✅
  - Size: < 500 MB (target)

- [x] **Helm-Chart**
  - Chart.yaml: ✅
  - values.yaml: ✅
  - 7 Templates: ✅
  - Version: 3.0.0

---

## ✅ Phase 2: Database & Migrations

### 2.1 PostgreSQL-Setup
```bash
# Prüfe PostgreSQL-Verbindung
psql -h $DB_HOST -U $DB_USER -d valeo_erp -c "SELECT 1;"
```
- [ ] PostgreSQL läuft (Version ≥ 14)
- [ ] Credentials konfiguriert
- [ ] Database `valeo_erp` erstellt
- [ ] User `valeo` hat Rechte

### 2.2 Migrations
```bash
# Alembic-Migration durchführen
alembic upgrade head

# Verify tables
psql -h $DB_HOST -U $DB_USER -d valeo_erp -c "\dt"
```
- [ ] 4 Migrations angewendet:
  - [ ] 001_add_documents_tables
  - [ ] 002_add_workflow_tables
  - [ ] 003_add_archive_table
  - [ ] 004_add_numbering_table

### 2.3 Rollback-Test
```bash
# Test Rollback auf Staging
alembic downgrade -1
alembic upgrade +1
```
- [ ] Rollback funktioniert
- [ ] Daten bleiben intakt

---

## ✅ Phase 3: Infrastructure & Secrets

### 3.1 Kubernetes-Namespace
```bash
kubectl create namespace production
kubectl label namespace production env=production
```
- [ ] Namespace `production` erstellt
- [ ] Resource-Quotas gesetzt
- [ ] Network-Policies angewendet

### 3.2 Secrets
```bash
kubectl create secret generic valeo-erp-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=oidc-client-secret=... \
  -n production
```
- [ ] Database-Credentials
- [ ] OIDC-Secrets
- [ ] API-Keys (falls benötigt)

### 3.3 ConfigMaps
```bash
kubectl create configmap valeo-erp-config \
  --from-literal=oidc-discovery-url=https://... \
  --from-literal=pdf-template-lang=de \
  -n production
```
- [ ] OIDC-Discovery-URL
- [ ] PDF-Template-Config
- [ ] Logging-Config

---

## ✅ Phase 4: Observability

### 4.1 Prometheus
```bash
# Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets
```
- [ ] Prometheus installiert
- [ ] ServiceMonitor konfiguriert
- [ ] Scraping aktiv

### 4.2 Grafana
```bash
# Import Dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/dashboards/valeo-erp.json
```
- [ ] Grafana installiert
- [ ] Dashboard importiert
- [ ] Datasource konfiguriert

### 4.3 Alerts
```bash
# Verify Alert-Manager
curl http://localhost:9093/api/v1/status
```
- [ ] Alert-Manager konfiguriert
- [ ] PagerDuty/Email-Integration
- [ ] Test-Alert gesendet

---

## ✅ Phase 5: Backups & DR

### 5.1 Backup-Konfiguration
```bash
# Test Backup-Script
./scripts/backup-db.sh
ls -lh /backups/postgresql/daily/
```
- [ ] Backup-Script funktioniert
- [ ] Cronjob konfiguriert (täglich 02:00)
- [ ] Retention-Policy aktiv (30d/12m)
- [ ] S3/Azure-Sync (optional)

### 5.2 Restore-Test
```bash
# Test auf Staging
./scripts/restore-db.sh /backups/postgresql/daily/latest.sql.gz
```
- [ ] Restore auf Staging erfolgreich
- [ ] Daten-Integrität verifiziert
- [ ] RPO < 24h erreicht
- [ ] RTO < 4h erreicht

---

## ✅ Phase 6: Security & Compliance

### 6.1 RBAC
```bash
# Test Scope-Guards
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/export/sales
# Should return 403 without docs:export scope
```
- [x] Scopes definiert
- [x] Guards implementiert
- [ ] 403-Tests für alle geschützten Endpoints

### 6.2 Rate-Limiting
```bash
# Test Rate-Limit
for i in {1..150}; do curl http://localhost:8000/api/documents/sales; done
# Should return 429 after 100 requests
```
- [x] SlowAPI konfiguriert
- [ ] Rate-Limits aktiv (100/min)
- [ ] Export-Limits aktiv (10/min)

### 6.3 GDPR
```bash
# Test PII-Redaction
grep -i "password" /var/log/valeo-erp/*.log
# Should find "password=***"
```
- [x] PII-Redaction aktiv
- [x] GDPR-Endpoints vorhanden
- [x] DPIA dokumentiert

---

## ✅ Phase 7: Staging-Deployment

### 7.1 Deploy to Staging
```bash
helm upgrade --install valeo-erp-staging ./k8s/helm/valeo-erp \
  --namespace staging \
  --create-namespace \
  --set image.tag=$VERSION \
  --wait
```
- [ ] Staging-Deployment erfolgreich
- [ ] Alle Pods running (3/3)
- [ ] /healthz returns 200
- [ ] /readyz returns 200

### 7.2 Smoke-Tests
```bash
# Login-Test
curl -X POST http://staging.erp.valeo.example.com/api/auth/login \
  -d '{"username":"test","password":"test"}'

# Create Document
curl -X POST http://staging.erp.valeo.example.com/api/documents/sales \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"customer":"Test","lines":[]}'

# Workflow Transition
curl -X POST http://staging.erp.valeo.example.com/api/workflow/sales/SO-00001/transition \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"action":"submit"}'

# SSE Connection
curl -N http://staging.erp.valeo.example.com/api/stream/workflow
```
- [ ] Login funktioniert
- [ ] Document-CRUD funktioniert
- [ ] Workflow-Transitions funktionieren
- [ ] SSE-Connection funktioniert
- [ ] PDF-Druck funktioniert
- [ ] Export funktioniert

### 7.3 Performance-Tests
```bash
# Run Load-Tests auf Staging
k6 run --env BASE_URL=http://staging.erp.valeo.example.com load-tests/api-load-test.js
k6 run --env BASE_URL=http://staging.erp.valeo.example.com load-tests/sse-load-test.js
```
- [ ] API-Load-Test: P95 < 500ms
- [ ] SSE-Load-Test: 1000 Connections stabil
- [ ] Error-Rate < 1%
- [ ] Memory-Usage stabil

---

## ✅ Phase 8: Production-Deployment

### 8.1 Pre-Production-Checklist
- [ ] **Stakeholder-Approval:** Business Owner unterschrieben
- [ ] **Security-Officer-Approval:** Security-Scan approved
- [ ] **DPO-Approval:** GDPR-Compliance approved
- [ ] **Maintenance-Window:** Geplant und kommuniziert
- [ ] **On-Call-Team:** Briefed und bereit
- [ ] **Rollback-Plan:** Dokumentiert und getestet

### 8.2 Deploy to Production
```bash
# Blue-Green-Deployment
helm upgrade --install valeo-erp-production ./k8s/helm/valeo-erp \
  --namespace production \
  --set image.tag=$VERSION \
  --set replicaCount=3 \
  --set resources.limits.cpu=2000m \
  --set resources.limits.memory=2Gi \
  --wait

# Verify Deployment
kubectl get pods -n production
kubectl rollout status deployment/valeo-erp -n production
```
- [ ] Production-Deployment erfolgreich
- [ ] Alle Pods running (3/3)
- [ ] Zero-Downtime-Deployment
- [ ] Old version still running (Blue)

### 8.3 Health-Checks
```bash
# Health-Checks auf Production
curl https://erp.valeo.example.com/healthz
curl https://erp.valeo.example.com/readyz

# Verify Metrics
curl https://erp.valeo.example.com/metrics | grep valeo

# Verify SSE
curl -N https://erp.valeo.example.com/api/stream/workflow
```
- [ ] /healthz: 200 OK
- [ ] /readyz: 200 OK
- [ ] /metrics: Prometheus-Format
- [ ] SSE-Connections funktionieren

### 8.4 Cutover (Blue → Green)
```bash
# Wenn Green OK → Cutover Traffic
kubectl patch service valeo-erp -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor für 15 Minuten
watch kubectl get pods -n production
```
- [ ] Traffic auf Green
- [ ] Keine Errors in Logs
- [ ] Metrics normal
- [ ] SSE-Reconnections erfolgreich

### 8.5 Cleanup Blue
```bash
# Nach 1 Stunde → Blue entfernen
kubectl delete deployment valeo-erp-blue -n production
```
- [ ] Blue-Deployment entfernt
- [ ] Nur Green läuft

---

## ✅ Phase 9: Post-Deployment

### 9.1 Monitoring (First 24h)
```bash
# Watch Metrics
watch -n 5 "curl -s https://erp.valeo.example.com/metrics | grep -E '(error|latency|connections)'"

# Watch Logs
kubectl logs -f -n production -l app=valeo-erp --tail=100
```
- [ ] Error-Rate < 1%
- [ ] P95-Latency < 500ms
- [ ] SSE-Connections stabil
- [ ] Memory-Usage stabil
- [ ] No Memory-Leaks

### 9.2 User-Acceptance-Testing (UAT)
- [ ] Business-Owner testet
- [ ] Key-Users testen
- [ ] Critical Workflows funktionieren
- [ ] Feedback dokumentiert

### 9.3 Documentation-Handover
- [ ] Operator-Runbooks übergeben
- [ ] Admin-Guides übergeben
- [ ] User-Guides übergeben
- [ ] On-Call-Procedures kommuniziert

---

## 🚨 Rollback-Plan

### When to Rollback
- Error-Rate > 5%
- P95-Latency > 2000ms
- Critical Bug entdeckt
- Data-Loss festgestellt

### How to Rollback
```bash
# Helm Rollback
helm rollback valeo-erp-production -n production

# Verify
kubectl get pods -n production
curl https://erp.valeo.example.com/healthz

# Database Rollback (falls nötig)
alembic downgrade -1

# Or Restore from Backup
./scripts/restore-db.sh /backups/postgresql/daily/pre_deployment.sql.gz
```

---

## 📞 Emergency Contacts

**On-Call Primary:** [PagerDuty]  
**On-Call Secondary:** [Team Lead]  
**Database Team:** db-team@valeo-erp.com  
**Platform Team:** platform@valeo-erp.com  
**Security Team:** security@valeo-erp.com  
**Emergency Hotline:** +49-XXX-XXXXXXX

---

## ✅ Sign-Off

**Pre-Deployment Check completed by:** _______________  
**Date:** _______________

**Approved for Production:**
- [ ] Technical Lead: _______________
- [ ] Business Owner: _______________
- [ ] Security Officer: _______________
- [ ] Data Protection Officer: _______________

---

**🚀 GO-LIVE APPROVED 🚀**

