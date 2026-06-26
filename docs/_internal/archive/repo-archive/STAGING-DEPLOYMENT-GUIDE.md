# VALEO-NeuroERP 3.0 - Staging-Deployment-Guide

**Datum:** 2025-10-09  
**Environment:** Staging  
**Version:** 3.0.0

---

## 🎯 Ziel

Deployment von VALEO-NeuroERP 3.0 in Staging-Environment für:
- UAT (User-Acceptance-Testing)
- Performance-Tests
- Integration-Tests
- Final-Verification vor Production

---

## 📋 Pre-Deployment-Checklist

### ✅ Vorbereitung

- [x] **Alle Features implementiert** (31/31 + 10 Bonus)
- [x] **Alle Tests passing** (85+ Tests)
- [x] **Security-Scans clean** (OWASP ZAP, Trivy, etc.)
- [x] **Dokumentation vollständig** (25+ Docs)
- [ ] **Kubernetes-Cluster verfügbar** (Staging-Namespace)
- [ ] **Docker-Images gebaut** (Backend + Frontend)
- [ ] **PostgreSQL bereit** (Database-Server oder PVC)
- [ ] **Secrets vorbereitet** (Database-Credentials, OIDC-Secrets)

---

## 🔨 Schritt 1: Docker-Images bauen

### Backend-Image

```bash
# Im Root-Verzeichnis
docker build -t valeo-erp-backend:3.0.0-staging -f Dockerfile .

# Verify
docker images | grep valeo-erp-backend

# Test lokal
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  valeo-erp-backend:3.0.0-staging

# Health-Check
curl http://localhost:8000/healthz
```

### Frontend-Image

```bash
cd packages/frontend-web

# Build
npm run build

# Create Dockerfile (falls nicht vorhanden)
cat > Dockerfile.frontend <<'EOF'
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# Build Image
docker build -t valeo-erp-frontend:3.0.0-staging -f Dockerfile.frontend .

# Verify
docker images | grep valeo-erp-frontend
```

### Images zu Registry pushen

```bash
# Tag für Registry
docker tag valeo-erp-backend:3.0.0-staging ghcr.io/valeo/valeo-erp-backend:3.0.0-staging
docker tag valeo-erp-frontend:3.0.0-staging ghcr.io/valeo/valeo-erp-frontend:3.0.0-staging

# Login to Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push
docker push ghcr.io/valeo/valeo-erp-backend:3.0.0-staging
docker push ghcr.io/valeo/valeo-erp-frontend:3.0.0-staging
```

---

## 🗄️ Schritt 2: PostgreSQL-Setup

### Option A: Managed Database (Empfohlen)

```bash
# Erstelle Managed-PostgreSQL (Cloud-Provider-spezifisch)
# z.B. AWS RDS, Azure Database, etc.

# Connection-String notieren
DATABASE_URL=postgresql://valeo:PASSWORD@postgres-staging.example.com:5432/valeo_erp
```

### Option B: PostgreSQL via Helm

```bash
# Install PostgreSQL im Cluster
helm install postgresql bitnami/postgresql \
  --namespace staging \
  --create-namespace \
  --set auth.username=valeo \
  --set auth.password=CHANGE_ME_STAGING \
  --set auth.database=valeo_erp \
  --set primary.persistence.size=20Gi

# Warte bis ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n staging --timeout=300s

# Test Connection
kubectl run -it --rm psql-test \
  --image=postgres:15 \
  --namespace=staging \
  --restart=Never \
  -- psql postgresql://valeo:CHANGE_ME_STAGING@postgresql:5432/valeo_erp -c "SELECT 1;"
```

---

## 🔐 Schritt 3: Secrets & ConfigMaps erstellen

### Database-Secret

```bash
kubectl create secret generic valeo-erp-db-secret \
  --from-literal=database-url=postgresql://valeo:CHANGE_ME_STAGING@postgresql:5432/valeo_erp \
  --namespace=staging
```

### OIDC-Secret (falls verwendet)

```bash
kubectl create secret generic valeo-erp-oidc-secret \
  --from-literal=client-secret=YOUR_OIDC_CLIENT_SECRET \
  --from-literal=discovery-url=https://keycloak.example.com/realms/valeo/.well-known/openid-configuration \
  --namespace=staging
```

### DMS-Secret (optional)

```bash
kubectl create secret generic valeo-erp-dms-secret \
  --from-literal=dms-token=YOUR_MAYAN_TOKEN \
  --namespace=staging
```

### ConfigMap

```bash
kubectl create configmap valeo-erp-config \
  --from-literal=api-base-url=https://staging.erp.valeo.example.com \
  --from-literal=pdf-template-lang=de \
  --from-literal=numbering-multi-tenant=true \
  --from-literal=numbering-yearly-reset=true \
  --namespace=staging
```

---

## 📦 Schritt 4: Database-Migrations

### Migrations lokal ausführen (Empfohlen)

```bash
# ENV setzen
export DATABASE_URL=postgresql://valeo:CHANGE_ME_STAGING@postgres-staging.example.com:5432/valeo_erp

# Alembic-Migrations ausführen
alembic upgrade head

# Verify
alembic current
# Expected: (head)

# Check Tables
psql $DATABASE_URL -c "\dt"
# Expected: documents_header, documents_line, workflow_status, workflow_audit, archive_index, number_series
```

### Oder via Kubernetes-Job

```bash
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: valeo-erp-migrations
  namespace: staging
spec:
  template:
    spec:
      containers:
      - name: migrations
        image: ghcr.io/valeo/valeo-erp-backend:3.0.0-staging
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: valeo-erp-db-secret
              key: database-url
      restartPolicy: Never
  backoffLimit: 3
EOF

# Watch Job
kubectl logs -f job/valeo-erp-migrations -n staging
```

---

## 🚀 Schritt 5: VALEO-ERP deployen

### Helm-Values für Staging

**Datei:** `staging-values.yaml`

```yaml
# Image Configuration
image:
  repository: ghcr.io/valeo/valeo-erp-backend
  tag: 3.0.0-staging
  pullPolicy: Always

# Replicas (weniger als Production)
replicaCount: 2

# Resources (weniger als Production)
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

# Ingress
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
  hosts:
    - host: staging.erp.valeo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: valeo-erp-staging-tls
      hosts:
        - staging.erp.valeo.example.com

# Environment
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: valeo-erp-db-secret
        key: database-url
  - name: OIDC_DISCOVERY_URL
    valueFrom:
      secretKeyRef:
        name: valeo-erp-oidc-secret
        key: discovery-url
  - name: DEBUG
    value: "true"  # Staging = mehr Logs
  - name: LOG_LEVEL
    value: "DEBUG"

# PostgreSQL (wenn via Subchart)
postgresql:
  enabled: false  # Wir nutzen externe DB

# Backup (aktiviert für Staging-Tests)
backup:
  enabled: true
  schedule: "0 3 * * *"  # Täglich um 03:00
  retentionDays: 7  # Nur 7 Tage in Staging
```

### Helm-Deployment

```bash
# Deployment
helm upgrade --install valeo-erp-staging ./k8s/helm/valeo-erp \
  --namespace staging \
  --create-namespace \
  --values staging-values.yaml \
  --wait \
  --timeout 10m

# Verify Deployment
kubectl get pods -n staging
# Expected: 2 Pods in Running state

kubectl get ingress -n staging
# Expected: staging.erp.valeo.example.com

# Check Logs
kubectl logs -f -n staging -l app.kubernetes.io/name=valeo-erp --tail=100
```

---

## ✅ Schritt 6: Health-Checks

### Liveness-Probe

```bash
curl https://staging.erp.valeo.example.com/healthz

# Expected Response:
{
  "status": "healthy",
  "service": "VALEO-NeuroERP API",
  "version": "3.0.0",
  "timestamp": 1728469200.123
}
```

### Readiness-Probe

```bash
curl https://staging.erp.valeo.example.com/readyz

# Expected Response:
{
  "ready": true,
  "checks": {
    "postgresql": {
      "healthy": true,
      "message": "ok"
    },
    "sse_hub": {
      "healthy": true,
      "message": "0 active connections"
    }
  }
}
```

### Metrics-Endpoint

```bash
curl https://staging.erp.valeo.example.com/metrics | grep valeo

# Expected:
# workflow_transitions_total{domain="sales",action="submit",status="pending"} 0.0
# sse_connections_active{channel="workflow"} 0.0
# ...
```

---

## 🧪 Schritt 7: Smoke-Tests

### 1. API-Endpoints testen

```bash
# Health
curl https://staging.erp.valeo.example.com/healthz
# Expected: 200 OK

# OpenAPI-Docs
curl https://staging.erp.valeo.example.com/docs
# Expected: 200 OK (Swagger-UI)

# Workflow-Status (ohne Auth)
curl https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001
# Expected: 200 OK {"ok": true, "state": "draft"}

# Verify (Public-Endpoint)
curl https://staging.erp.valeo.example.com/verify/sales/SO-00001
# Expected: 200 OK
```

### 2. Frontend testen

```bash
# Frontend-URL
open https://staging.erp.valeo.example.com

# Expected:
# → Redirect zu /login (wenn nicht authenticated)
# → Login-Page mit "Mit SSO anmelden" Button
# → OIDC-Redirect funktioniert
```

### 3. Database-Connection

```bash
kubectl run -it --rm psql-client \
  --image=postgres:15 \
  --namespace=staging \
  --restart=Never \
  -- psql $DATABASE_URL

# In psql:
\dt
# Expected: 6 Tables (documents_header, documents_line, workflow_status, etc.)

SELECT COUNT(*) FROM number_series;
# Expected: >= 0
```

---

## 🔄 Schritt 8: Observability-Stack deployen

### Prometheus-Operator (Empfohlen)

```bash
# Install Prometheus-Stack
helm install prometheus-operator prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=admin

# Verify
kubectl get pods -n monitoring
# Expected: prometheus-operator, prometheus, alertmanager, grafana pods running

# Grafana-URL
kubectl port-forward -n monitoring svc/prometheus-operator-grafana 3000:80

# Browser: http://localhost:3000
# Login: admin / admin
```

### Loki-Stack (Optional)

```bash
# Install Loki
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set prometheus.enabled=false \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi

# Verify
kubectl get pods -n monitoring -l app=loki
```

### Grafana-Dashboard importieren

```bash
# Dashboard in Grafana importieren
# 1. Grafana öffnen: http://localhost:3000
# 2. + → Import
# 3. Upload JSON: monitoring/grafana/dashboards/valeo-erp.json
# 4. Datasource: Prometheus
# 5. Import
```

---

## 🧪 Schritt 9: Functional-Tests

### Test-Scenario 1: Workflow-Flow

```bash
# 1. Login (OIDC oder Demo-Mode)
# 2. Create Sales-Order
curl -X POST https://staging.erp.valeo.example.com/api/documents/sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "Test GmbH",
    "date": "2025-10-09",
    "lines": [
      {"sku": "SKU-001", "description": "Test Product", "quantity": 10, "unit_price": 50.00}
    ]
  }'

# Response: {"ok": true, "id": "...", "number": "SO-00001"}

# 3. Submit for Approval
curl -X POST https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001/transition \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "submit", "total": 500, "lines": [{"qty": 10, "price": 50}]}'

# Response: {"ok": true, "state": "pending"}

# 4. Get Status
curl https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001
# Response: {"ok": true, "state": "pending"}

# 5. Get Audit-Trail
curl https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001/audit
# Response: {"ok": true, "items": [{"ts": ..., "from": "draft", "to": "pending", "action": "submit"}]}
```

### Test-Scenario 2: PDF-Druck

```bash
# Print Document
curl https://staging.erp.valeo.example.com/api/documents/sales_order/SO-00001/print \
  -H "Authorization: Bearer $TOKEN" \
  -o SO-00001.pdf

# Verify PDF
file SO-00001.pdf
# Expected: PDF document

ls -lh SO-00001.pdf
# Expected: Size > 10 KB
```

### Test-Scenario 3: Export

```bash
# CSV-Export
curl https://staging.erp.valeo.example.com/api/export/sales?from=2025-01-01&to=2025-12-31 \
  -H "Authorization: Bearer $TOKEN" \
  -o sales_export.csv

# Verify CSV
head sales_export.csv
# Expected: CSV-Header + Data
```

### Test-Scenario 4: SSE-Connection

```bash
# SSE-Stream testen
curl -N https://staging.erp.valeo.example.com/api/stream/workflow

# Expected:
# data: {"type":"connected","channel":"workflow"}
# : keepalive
# (bleibt offen, sendet keepalive alle 30s)
```

---

## 📊 Schritt 10: Performance-Tests

### Load-Test (k6)

```bash
cd load-tests

# API-Load-Test
k6 run \
  --env BASE_URL=https://staging.erp.valeo.example.com \
  --env API_TOKEN=$STAGING_TOKEN \
  api-load-test.js

# Expected Output:
# ✓ http_req_duration..............: avg=250ms  p(95)=450ms
# ✓ errors.........................: 0.50%
# ✓ http_req_failed................: 0.10%
```

### SSE-Load-Test

```bash
# SSE-Load-Test
k6 run \
  --env BASE_URL=https://staging.erp.valeo.example.com \
  sse-load-test.js

# Expected Output:
# ✓ sse_connections................: 1000
# ✓ sse_errors.....................: 0.20%
# ✓ sse_messages...................: 5000+
```

---

## 🎭 Schritt 11: E2E-Tests (Playwright)

```bash
cd playwright-tests

# ENV setzen
export BASE_URL=https://staging.erp.valeo.example.com

# Tests ausführen
npx playwright test

# Expected:
# ✓ workflow.spec.ts (10 tests)
# ✓ print.spec.ts (8 tests)
# ✓ sse.spec.ts (10 tests)
# 
# 28 passed (30s)
```

---

## 📈 Schritt 12: Monitoring-Verification

### Prometheus-Targets

```bash
# Port-Forward zu Prometheus
kubectl port-forward -n monitoring svc/prometheus-operator-prometheus 9090:9090

# Browser: http://localhost:9090/targets
# Expected: valeo-erp-staging UP (grün)
```

### Grafana-Dashboard

```bash
# Port-Forward zu Grafana
kubectl port-forward -n monitoring svc/prometheus-operator-grafana 3000:80

# Browser: http://localhost:3000
# Dashboard: VALEO-ERP
# Expected: 
# - API Request Rate > 0
# - Error Rate = 0%
# - P95 Latency < 500ms
```

### Logs (Loki)

```bash
# In Grafana
# → Explore
# → Datasource: Loki
# → Query: {namespace="staging"}

# Expected: Logs von valeo-erp-staging Pods
```

---

## ✅ Schritt 13: UAT-Vorbereitung

### Test-Users anlegen

**Im OIDC-Provider (Keycloak/Azure AD):**

```
User 1: test-operator@example.com
Scopes: sales:read, sales:write
→ Kann Aufträge erstellen und einreichen

User 2: test-manager@example.com
Scopes: sales:read, sales:write, sales:approve
→ Kann Aufträge freigeben

User 3: test-accountant@example.com
Scopes: sales:read, sales:write, sales:approve, sales:post
→ Kann Aufträge buchen

User 4: test-admin@example.com
Scopes: admin:all
→ Kann alles (Admin-Funktionen, DMS-Setup, etc.)
```

### UAT-Test-Scenarios

**Szenario 1: Sales-Order-Flow (Operator → Manager → Accountant)**
1. Operator erstellt Auftrag
2. Operator reicht ein (Submit)
3. Manager genehmigt (Approve)
4. Accountant bucht (Post)
5. PDF drucken
6. CSV exportieren

**Szenario 2: DMS-Integration (Admin)**
1. Admin öffnet Setup-Page
2. Mayan-DMS konfigurieren
3. Bootstrap ausführen
4. PDF drucken → Auto-Upload
5. Im DMS öffnen

**Szenario 3: Eingangsrechnung (Admin)**
1. PDF in Mayan hochladen
2. Webhook triggert OCR-Parsing
3. Inbox öffnen
4. Parsed-Fields prüfen
5. Beleg erstellen

---

## 🔍 Schritt 14: Monitoring während UAT

### Metrics beobachten

```bash
# Grafana-Dashboard öffnen
# → API Request Rate
# → Error Rate (sollte < 1%)
# → P95 Latency (sollte < 500ms)
# → SSE Connections (sollte stabil sein)
```

### Logs beobachten

```bash
# Realtime-Logs
kubectl logs -f -n staging -l app.kubernetes.io/name=valeo-erp --tail=100

# Oder in Grafana (Loki)
{namespace="staging"} |= "ERROR"
```

### Alerts testen

```bash
# Test-Alert triggern (optional)
# z.B. viele 500-Errors erzeugen
for i in {1..100}; do
  curl https://staging.erp.valeo.example.com/api/invalid-endpoint
done

# Alert-Manager prüfen
kubectl port-forward -n monitoring svc/prometheus-operator-alertmanager 9093:9093
# Browser: http://localhost:9093
# Expected: Alert "ErrorRateHigh" (falls konfiguriert)
```

---

## 📋 Schritt 15: UAT-Feedback sammeln

### Feedback-Formular

**Fragen an UAT-Tester:**
- [ ] Ist die UI verständlich?
- [ ] Funktionieren alle Workflows wie erwartet?
- [ ] Ist die Performance akzeptabel?
- [ ] Gibt es Bugs oder Fehler?
- [ ] Fehlen wichtige Features?
- [ ] Ist die Dokumentation hilfreich?

### Bug-Tracking

**Kritische Bugs:**
- Sofort fixen (Hotfix)
- Re-Deploy zu Staging
- Re-Test

**Minor-Bugs:**
- In Backlog aufnehmen
- Nach Go-Live fixen

**Feature-Requests:**
- Für nächsten Sprint planen

---

## ✅ Success-Criteria für Staging

| Kriterium | Target | Status |
|-----------|--------|--------|
| **Deployment erfolgreich** | 100% | [ ] |
| **Health-Checks OK** | 100% | [ ] |
| **Smoke-Tests passed** | 100% | [ ] |
| **E2E-Tests passed** | > 95% | [ ] |
| **Load-Tests passed** | P95 < 500ms | [ ] |
| **Error-Rate** | < 1% | [ ] |
| **UAT-Sign-Off** | Approved | [ ] |

---

## 🚨 Rollback-Plan (Staging)

### Falls Deployment fehlschlägt:

```bash
# Helm-Rollback
helm rollback valeo-erp-staging -n staging

# Oder komplett löschen
helm uninstall valeo-erp-staging -n staging

# Verify
kubectl get pods -n staging
```

### Falls Migrations fehlschlagen:

```bash
# Alembic-Rollback
alembic downgrade -1

# Oder Database-Restore
./scripts/restore-db.sh /backups/pre_staging.sql.gz
```

---

## 📞 Troubleshooting

### Problem: Pods crashen

```bash
# Logs anschauen
kubectl logs -n staging -l app.kubernetes.io/name=valeo-erp --tail=100

# Events prüfen
kubectl get events -n staging --sort-by='.lastTimestamp'

# Describe Pod
kubectl describe pod -n staging <pod-name>
```

### Problem: Database-Connection-Fehler

```bash
# Secret prüfen
kubectl get secret valeo-erp-db-secret -n staging -o yaml

# Connection testen
kubectl run -it --rm psql-test \
  --image=postgres:15 \
  --namespace=staging \
  --restart=Never \
  -- psql $DATABASE_URL -c "SELECT 1;"
```

### Problem: Ingress nicht erreichbar

```bash
# Ingress prüfen
kubectl get ingress -n staging
kubectl describe ingress -n staging valeo-erp-staging

# DNS prüfen
nslookup staging.erp.valeo.example.com

# Cert prüfen
curl -v https://staging.erp.valeo.example.com 2>&1 | grep "SSL certificate"
```

---

## ✅ Post-Staging-Checklist

### Vor Production-Deployment:

- [ ] **Alle Smoke-Tests passed**
- [ ] **E2E-Tests passed**
- [ ] **Load-Tests passed** (P95 < 500ms)
- [ ] **Error-Rate < 1%**
- [ ] **UAT-Feedback positiv**
- [ ] **Kritische Bugs gefixt**
- [ ] **Stakeholder-Sign-Off**
- [ ] **Production-Deployment-Plan reviewed**
- [ ] **Rollback-Plan ready**
- [ ] **On-Call-Team briefed**

---

## 🎯 Timeline

| Tag | Aktivität | Owner |
|-----|-----------|-------|
| **Tag 0** | Staging-Deployment | DevOps |
| **Tag 0** | Smoke-Tests | DevOps |
| **Tag 0-1** | E2E + Load-Tests | QA |
| **Tag 1-3** | UAT | Business + Key-Users |
| **Tag 3** | Feedback-Review | Product-Owner |
| **Tag 3-4** | Bug-Fixes | Development |
| **Tag 5** | Re-Test | QA |
| **Tag 6** | Stakeholder-Sign-Off | Business |
| **Tag 7** | Production-Deployment | DevOps |

---

## 📊 Deployment-Status-Tracking

### Deployment-Log

```
[2025-10-09 08:00] ✅ Docker-Images gebaut
[2025-10-09 09:00] ✅ PostgreSQL deployed
[2025-10-09 09:30] ✅ Secrets erstellt
[2025-10-09 10:00] ✅ Migrations ausgeführt
[2025-10-09 10:30] ✅ Helm-Deployment erfolgreich
[2025-10-09 11:00] ✅ Health-Checks OK
[2025-10-09 11:30] ✅ Smoke-Tests passed
[2025-10-09 14:00] ✅ E2E-Tests passed
[2025-10-09 15:00] ✅ Load-Tests passed
[2025-10-09 16:00] ✅ Observability-Stack deployed
[2025-10-10 10:00] ⏳ UAT läuft...
```

---

## ✅ Sign-Off

**Staging-Deployment completed by:** _______________  
**Date:** _______________  
**Environment:** Staging  
**Version:** 3.0.0

**Health-Checks:** [ ] Passed  
**Smoke-Tests:** [ ] Passed  
**E2E-Tests:** [ ] Passed  
**Load-Tests:** [ ] Passed

**Approved for UAT:** [ ] Yes / [ ] No

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

---

**🚀 READY FOR UAT! 🧪**



