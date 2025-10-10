***REMOVED*** VALEO-NeuroERP 3.0 - Staging-Deployment-Guide

**Datum:** 2025-10-09  
**Environment:** Staging  
**Version:** 3.0.0

---

***REMOVED******REMOVED*** 🎯 Ziel

Deployment von VALEO-NeuroERP 3.0 in Staging-Environment für:
- UAT (User-Acceptance-Testing)
- Performance-Tests
- Integration-Tests
- Final-Verification vor Production

---

***REMOVED******REMOVED*** 📋 Pre-Deployment-Checklist

***REMOVED******REMOVED******REMOVED*** ✅ Vorbereitung

- [x] **Alle Features implementiert** (31/31 + 10 Bonus)
- [x] **Alle Tests passing** (85+ Tests)
- [x] **Security-Scans clean** (OWASP ZAP, Trivy, etc.)
- [x] **Dokumentation vollständig** (25+ Docs)
- [ ] **Kubernetes-Cluster verfügbar** (Staging-Namespace)
- [ ] **Docker-Images gebaut** (Backend + Frontend)
- [ ] **PostgreSQL bereit** (Database-Server oder PVC)
- [ ] **Secrets vorbereitet** (Database-Credentials, OIDC-Secrets)

---

***REMOVED******REMOVED*** 🔨 Schritt 1: Docker-Images bauen

***REMOVED******REMOVED******REMOVED*** Backend-Image

```bash
***REMOVED*** Im Root-Verzeichnis
docker build -t valeo-erp-backend:3.0.0-staging -f Dockerfile .

***REMOVED*** Verify
docker images | grep valeo-erp-backend

***REMOVED*** Test lokal
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  valeo-erp-backend:3.0.0-staging

***REMOVED*** Health-Check
curl http://localhost:8000/healthz
```

***REMOVED******REMOVED******REMOVED*** Frontend-Image

```bash
cd packages/frontend-web

***REMOVED*** Build
npm run build

***REMOVED*** Create Dockerfile (falls nicht vorhanden)
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

***REMOVED*** Build Image
docker build -t valeo-erp-frontend:3.0.0-staging -f Dockerfile.frontend .

***REMOVED*** Verify
docker images | grep valeo-erp-frontend
```

***REMOVED******REMOVED******REMOVED*** Images zu Registry pushen

```bash
***REMOVED*** Tag für Registry
docker tag valeo-erp-backend:3.0.0-staging ghcr.io/valeo/valeo-erp-backend:3.0.0-staging
docker tag valeo-erp-frontend:3.0.0-staging ghcr.io/valeo/valeo-erp-frontend:3.0.0-staging

***REMOVED*** Login to Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

***REMOVED*** Push
docker push ghcr.io/valeo/valeo-erp-backend:3.0.0-staging
docker push ghcr.io/valeo/valeo-erp-frontend:3.0.0-staging
```

---

***REMOVED******REMOVED*** 🗄️ Schritt 2: PostgreSQL-Setup

***REMOVED******REMOVED******REMOVED*** Option A: Managed Database (Empfohlen)

```bash
***REMOVED*** Erstelle Managed-PostgreSQL (Cloud-Provider-spezifisch)
***REMOVED*** z.B. AWS RDS, Azure Database, etc.

***REMOVED*** Connection-String notieren
DATABASE_URL=postgresql://valeo:PASSWORD@postgres-staging.example.com:5432/valeo_erp
```

***REMOVED******REMOVED******REMOVED*** Option B: PostgreSQL via Helm

```bash
***REMOVED*** Install PostgreSQL im Cluster
helm install postgresql bitnami/postgresql \
  --namespace staging \
  --create-namespace \
  --set auth.username=valeo \
  --set auth.password=CHANGE_ME_STAGING \
  --set auth.database=valeo_erp \
  --set primary.persistence.size=20Gi

***REMOVED*** Warte bis ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n staging --timeout=300s

***REMOVED*** Test Connection
kubectl run -it --rm psql-test \
  --image=postgres:15 \
  --namespace=staging \
  --restart=Never \
  -- psql postgresql://valeo:CHANGE_ME_STAGING@postgresql:5432/valeo_erp -c "SELECT 1;"
```

---

***REMOVED******REMOVED*** 🔐 Schritt 3: Secrets & ConfigMaps erstellen

***REMOVED******REMOVED******REMOVED*** Database-Secret

```bash
kubectl create secret generic valeo-erp-db-secret \
  --from-literal=database-url=postgresql://valeo:CHANGE_ME_STAGING@postgresql:5432/valeo_erp \
  --namespace=staging
```

***REMOVED******REMOVED******REMOVED*** OIDC-Secret (falls verwendet)

```bash
kubectl create secret generic valeo-erp-oidc-secret \
  --from-literal=client-secret=YOUR_OIDC_CLIENT_SECRET \
  --from-literal=discovery-url=https://keycloak.example.com/realms/valeo/.well-known/openid-configuration \
  --namespace=staging
```

***REMOVED******REMOVED******REMOVED*** DMS-Secret (optional)

```bash
kubectl create secret generic valeo-erp-dms-secret \
  --from-literal=dms-token=YOUR_MAYAN_TOKEN \
  --namespace=staging
```

***REMOVED******REMOVED******REMOVED*** ConfigMap

```bash
kubectl create configmap valeo-erp-config \
  --from-literal=api-base-url=https://staging.erp.valeo.example.com \
  --from-literal=pdf-template-lang=de \
  --from-literal=numbering-multi-tenant=true \
  --from-literal=numbering-yearly-reset=true \
  --namespace=staging
```

---

***REMOVED******REMOVED*** 📦 Schritt 4: Database-Migrations

***REMOVED******REMOVED******REMOVED*** Migrations lokal ausführen (Empfohlen)

```bash
***REMOVED*** ENV setzen
export DATABASE_URL=postgresql://valeo:CHANGE_ME_STAGING@postgres-staging.example.com:5432/valeo_erp

***REMOVED*** Alembic-Migrations ausführen
alembic upgrade head

***REMOVED*** Verify
alembic current
***REMOVED*** Expected: (head)

***REMOVED*** Check Tables
psql $DATABASE_URL -c "\dt"
***REMOVED*** Expected: documents_header, documents_line, workflow_status, workflow_audit, archive_index, number_series
```

***REMOVED******REMOVED******REMOVED*** Oder via Kubernetes-Job

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

***REMOVED*** Watch Job
kubectl logs -f job/valeo-erp-migrations -n staging
```

---

***REMOVED******REMOVED*** 🚀 Schritt 5: VALEO-ERP deployen

***REMOVED******REMOVED******REMOVED*** Helm-Values für Staging

**Datei:** `staging-values.yaml`

```yaml
***REMOVED*** Image Configuration
image:
  repository: ghcr.io/valeo/valeo-erp-backend
  tag: 3.0.0-staging
  pullPolicy: Always

***REMOVED*** Replicas (weniger als Production)
replicaCount: 2

***REMOVED*** Resources (weniger als Production)
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

***REMOVED*** Ingress
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

***REMOVED*** Environment
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
    value: "true"  ***REMOVED*** Staging = mehr Logs
  - name: LOG_LEVEL
    value: "DEBUG"

***REMOVED*** PostgreSQL (wenn via Subchart)
postgresql:
  enabled: false  ***REMOVED*** Wir nutzen externe DB

***REMOVED*** Backup (aktiviert für Staging-Tests)
backup:
  enabled: true
  schedule: "0 3 * * *"  ***REMOVED*** Täglich um 03:00
  retentionDays: 7  ***REMOVED*** Nur 7 Tage in Staging
```

***REMOVED******REMOVED******REMOVED*** Helm-Deployment

```bash
***REMOVED*** Deployment
helm upgrade --install valeo-erp-staging ./k8s/helm/valeo-erp \
  --namespace staging \
  --create-namespace \
  --values staging-values.yaml \
  --wait \
  --timeout 10m

***REMOVED*** Verify Deployment
kubectl get pods -n staging
***REMOVED*** Expected: 2 Pods in Running state

kubectl get ingress -n staging
***REMOVED*** Expected: staging.erp.valeo.example.com

***REMOVED*** Check Logs
kubectl logs -f -n staging -l app.kubernetes.io/name=valeo-erp --tail=100
```

---

***REMOVED******REMOVED*** ✅ Schritt 6: Health-Checks

***REMOVED******REMOVED******REMOVED*** Liveness-Probe

```bash
curl https://staging.erp.valeo.example.com/healthz

***REMOVED*** Expected Response:
{
  "status": "healthy",
  "service": "VALEO-NeuroERP API",
  "version": "3.0.0",
  "timestamp": 1728469200.123
}
```

***REMOVED******REMOVED******REMOVED*** Readiness-Probe

```bash
curl https://staging.erp.valeo.example.com/readyz

***REMOVED*** Expected Response:
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

***REMOVED******REMOVED******REMOVED*** Metrics-Endpoint

```bash
curl https://staging.erp.valeo.example.com/metrics | grep valeo

***REMOVED*** Expected:
***REMOVED*** workflow_transitions_total{domain="sales",action="submit",status="pending"} 0.0
***REMOVED*** sse_connections_active{channel="workflow"} 0.0
***REMOVED*** ...
```

---

***REMOVED******REMOVED*** 🧪 Schritt 7: Smoke-Tests

***REMOVED******REMOVED******REMOVED*** 1. API-Endpoints testen

```bash
***REMOVED*** Health
curl https://staging.erp.valeo.example.com/healthz
***REMOVED*** Expected: 200 OK

***REMOVED*** OpenAPI-Docs
curl https://staging.erp.valeo.example.com/docs
***REMOVED*** Expected: 200 OK (Swagger-UI)

***REMOVED*** Workflow-Status (ohne Auth)
curl https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001
***REMOVED*** Expected: 200 OK {"ok": true, "state": "draft"}

***REMOVED*** Verify (Public-Endpoint)
curl https://staging.erp.valeo.example.com/verify/sales/SO-00001
***REMOVED*** Expected: 200 OK
```

***REMOVED******REMOVED******REMOVED*** 2. Frontend testen

```bash
***REMOVED*** Frontend-URL
open https://staging.erp.valeo.example.com

***REMOVED*** Expected:
***REMOVED*** → Redirect zu /login (wenn nicht authenticated)
***REMOVED*** → Login-Page mit "Mit SSO anmelden" Button
***REMOVED*** → OIDC-Redirect funktioniert
```

***REMOVED******REMOVED******REMOVED*** 3. Database-Connection

```bash
kubectl run -it --rm psql-client \
  --image=postgres:15 \
  --namespace=staging \
  --restart=Never \
  -- psql $DATABASE_URL

***REMOVED*** In psql:
\dt
***REMOVED*** Expected: 6 Tables (documents_header, documents_line, workflow_status, etc.)

SELECT COUNT(*) FROM number_series;
***REMOVED*** Expected: >= 0
```

---

***REMOVED******REMOVED*** 🔄 Schritt 8: Observability-Stack deployen

***REMOVED******REMOVED******REMOVED*** Prometheus-Operator (Empfohlen)

```bash
***REMOVED*** Install Prometheus-Stack
helm install prometheus-operator prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=admin

***REMOVED*** Verify
kubectl get pods -n monitoring
***REMOVED*** Expected: prometheus-operator, prometheus, alertmanager, grafana pods running

***REMOVED*** Grafana-URL
kubectl port-forward -n monitoring svc/prometheus-operator-grafana 3000:80

***REMOVED*** Browser: http://localhost:3000
***REMOVED*** Login: admin / admin
```

***REMOVED******REMOVED******REMOVED*** Loki-Stack (Optional)

```bash
***REMOVED*** Install Loki
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set prometheus.enabled=false \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi

***REMOVED*** Verify
kubectl get pods -n monitoring -l app=loki
```

***REMOVED******REMOVED******REMOVED*** Grafana-Dashboard importieren

```bash
***REMOVED*** Dashboard in Grafana importieren
***REMOVED*** 1. Grafana öffnen: http://localhost:3000
***REMOVED*** 2. + → Import
***REMOVED*** 3. Upload JSON: monitoring/grafana/dashboards/valeo-erp.json
***REMOVED*** 4. Datasource: Prometheus
***REMOVED*** 5. Import
```

---

***REMOVED******REMOVED*** 🧪 Schritt 9: Functional-Tests

***REMOVED******REMOVED******REMOVED*** Test-Scenario 1: Workflow-Flow

```bash
***REMOVED*** 1. Login (OIDC oder Demo-Mode)
***REMOVED*** 2. Create Sales-Order
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

***REMOVED*** Response: {"ok": true, "id": "...", "number": "SO-00001"}

***REMOVED*** 3. Submit for Approval
curl -X POST https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001/transition \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "submit", "total": 500, "lines": [{"qty": 10, "price": 50}]}'

***REMOVED*** Response: {"ok": true, "state": "pending"}

***REMOVED*** 4. Get Status
curl https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001
***REMOVED*** Response: {"ok": true, "state": "pending"}

***REMOVED*** 5. Get Audit-Trail
curl https://staging.erp.valeo.example.com/api/workflow/sales/SO-00001/audit
***REMOVED*** Response: {"ok": true, "items": [{"ts": ..., "from": "draft", "to": "pending", "action": "submit"}]}
```

***REMOVED******REMOVED******REMOVED*** Test-Scenario 2: PDF-Druck

```bash
***REMOVED*** Print Document
curl https://staging.erp.valeo.example.com/api/documents/sales_order/SO-00001/print \
  -H "Authorization: Bearer $TOKEN" \
  -o SO-00001.pdf

***REMOVED*** Verify PDF
file SO-00001.pdf
***REMOVED*** Expected: PDF document

ls -lh SO-00001.pdf
***REMOVED*** Expected: Size > 10 KB
```

***REMOVED******REMOVED******REMOVED*** Test-Scenario 3: Export

```bash
***REMOVED*** CSV-Export
curl https://staging.erp.valeo.example.com/api/export/sales?from=2025-01-01&to=2025-12-31 \
  -H "Authorization: Bearer $TOKEN" \
  -o sales_export.csv

***REMOVED*** Verify CSV
head sales_export.csv
***REMOVED*** Expected: CSV-Header + Data
```

***REMOVED******REMOVED******REMOVED*** Test-Scenario 4: SSE-Connection

```bash
***REMOVED*** SSE-Stream testen
curl -N https://staging.erp.valeo.example.com/api/stream/workflow

***REMOVED*** Expected:
***REMOVED*** data: {"type":"connected","channel":"workflow"}
***REMOVED*** : keepalive
***REMOVED*** (bleibt offen, sendet keepalive alle 30s)
```

---

***REMOVED******REMOVED*** 📊 Schritt 10: Performance-Tests

***REMOVED******REMOVED******REMOVED*** Load-Test (k6)

```bash
cd load-tests

***REMOVED*** API-Load-Test
k6 run \
  --env BASE_URL=https://staging.erp.valeo.example.com \
  --env API_TOKEN=$STAGING_TOKEN \
  api-load-test.js

***REMOVED*** Expected Output:
***REMOVED*** ✓ http_req_duration..............: avg=250ms  p(95)=450ms
***REMOVED*** ✓ errors.........................: 0.50%
***REMOVED*** ✓ http_req_failed................: 0.10%
```

***REMOVED******REMOVED******REMOVED*** SSE-Load-Test

```bash
***REMOVED*** SSE-Load-Test
k6 run \
  --env BASE_URL=https://staging.erp.valeo.example.com \
  sse-load-test.js

***REMOVED*** Expected Output:
***REMOVED*** ✓ sse_connections................: 1000
***REMOVED*** ✓ sse_errors.....................: 0.20%
***REMOVED*** ✓ sse_messages...................: 5000+
```

---

***REMOVED******REMOVED*** 🎭 Schritt 11: E2E-Tests (Playwright)

```bash
cd playwright-tests

***REMOVED*** ENV setzen
export BASE_URL=https://staging.erp.valeo.example.com

***REMOVED*** Tests ausführen
npx playwright test

***REMOVED*** Expected:
***REMOVED*** ✓ workflow.spec.ts (10 tests)
***REMOVED*** ✓ print.spec.ts (8 tests)
***REMOVED*** ✓ sse.spec.ts (10 tests)
***REMOVED*** 
***REMOVED*** 28 passed (30s)
```

---

***REMOVED******REMOVED*** 📈 Schritt 12: Monitoring-Verification

***REMOVED******REMOVED******REMOVED*** Prometheus-Targets

```bash
***REMOVED*** Port-Forward zu Prometheus
kubectl port-forward -n monitoring svc/prometheus-operator-prometheus 9090:9090

***REMOVED*** Browser: http://localhost:9090/targets
***REMOVED*** Expected: valeo-erp-staging UP (grün)
```

***REMOVED******REMOVED******REMOVED*** Grafana-Dashboard

```bash
***REMOVED*** Port-Forward zu Grafana
kubectl port-forward -n monitoring svc/prometheus-operator-grafana 3000:80

***REMOVED*** Browser: http://localhost:3000
***REMOVED*** Dashboard: VALEO-ERP
***REMOVED*** Expected: 
***REMOVED*** - API Request Rate > 0
***REMOVED*** - Error Rate = 0%
***REMOVED*** - P95 Latency < 500ms
```

***REMOVED******REMOVED******REMOVED*** Logs (Loki)

```bash
***REMOVED*** In Grafana
***REMOVED*** → Explore
***REMOVED*** → Datasource: Loki
***REMOVED*** → Query: {namespace="staging"}

***REMOVED*** Expected: Logs von valeo-erp-staging Pods
```

---

***REMOVED******REMOVED*** ✅ Schritt 13: UAT-Vorbereitung

***REMOVED******REMOVED******REMOVED*** Test-Users anlegen

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

***REMOVED******REMOVED******REMOVED*** UAT-Test-Scenarios

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

***REMOVED******REMOVED*** 🔍 Schritt 14: Monitoring während UAT

***REMOVED******REMOVED******REMOVED*** Metrics beobachten

```bash
***REMOVED*** Grafana-Dashboard öffnen
***REMOVED*** → API Request Rate
***REMOVED*** → Error Rate (sollte < 1%)
***REMOVED*** → P95 Latency (sollte < 500ms)
***REMOVED*** → SSE Connections (sollte stabil sein)
```

***REMOVED******REMOVED******REMOVED*** Logs beobachten

```bash
***REMOVED*** Realtime-Logs
kubectl logs -f -n staging -l app.kubernetes.io/name=valeo-erp --tail=100

***REMOVED*** Oder in Grafana (Loki)
{namespace="staging"} |= "ERROR"
```

***REMOVED******REMOVED******REMOVED*** Alerts testen

```bash
***REMOVED*** Test-Alert triggern (optional)
***REMOVED*** z.B. viele 500-Errors erzeugen
for i in {1..100}; do
  curl https://staging.erp.valeo.example.com/api/invalid-endpoint
done

***REMOVED*** Alert-Manager prüfen
kubectl port-forward -n monitoring svc/prometheus-operator-alertmanager 9093:9093
***REMOVED*** Browser: http://localhost:9093
***REMOVED*** Expected: Alert "ErrorRateHigh" (falls konfiguriert)
```

---

***REMOVED******REMOVED*** 📋 Schritt 15: UAT-Feedback sammeln

***REMOVED******REMOVED******REMOVED*** Feedback-Formular

**Fragen an UAT-Tester:**
- [ ] Ist die UI verständlich?
- [ ] Funktionieren alle Workflows wie erwartet?
- [ ] Ist die Performance akzeptabel?
- [ ] Gibt es Bugs oder Fehler?
- [ ] Fehlen wichtige Features?
- [ ] Ist die Dokumentation hilfreich?

***REMOVED******REMOVED******REMOVED*** Bug-Tracking

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

***REMOVED******REMOVED*** ✅ Success-Criteria für Staging

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

***REMOVED******REMOVED*** 🚨 Rollback-Plan (Staging)

***REMOVED******REMOVED******REMOVED*** Falls Deployment fehlschlägt:

```bash
***REMOVED*** Helm-Rollback
helm rollback valeo-erp-staging -n staging

***REMOVED*** Oder komplett löschen
helm uninstall valeo-erp-staging -n staging

***REMOVED*** Verify
kubectl get pods -n staging
```

***REMOVED******REMOVED******REMOVED*** Falls Migrations fehlschlagen:

```bash
***REMOVED*** Alembic-Rollback
alembic downgrade -1

***REMOVED*** Oder Database-Restore
./scripts/restore-db.sh /backups/pre_staging.sql.gz
```

---

***REMOVED******REMOVED*** 📞 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: Pods crashen

```bash
***REMOVED*** Logs anschauen
kubectl logs -n staging -l app.kubernetes.io/name=valeo-erp --tail=100

***REMOVED*** Events prüfen
kubectl get events -n staging --sort-by='.lastTimestamp'

***REMOVED*** Describe Pod
kubectl describe pod -n staging <pod-name>
```

***REMOVED******REMOVED******REMOVED*** Problem: Database-Connection-Fehler

```bash
***REMOVED*** Secret prüfen
kubectl get secret valeo-erp-db-secret -n staging -o yaml

***REMOVED*** Connection testen
kubectl run -it --rm psql-test \
  --image=postgres:15 \
  --namespace=staging \
  --restart=Never \
  -- psql $DATABASE_URL -c "SELECT 1;"
```

***REMOVED******REMOVED******REMOVED*** Problem: Ingress nicht erreichbar

```bash
***REMOVED*** Ingress prüfen
kubectl get ingress -n staging
kubectl describe ingress -n staging valeo-erp-staging

***REMOVED*** DNS prüfen
nslookup staging.erp.valeo.example.com

***REMOVED*** Cert prüfen
curl -v https://staging.erp.valeo.example.com 2>&1 | grep "SSL certificate"
```

---

***REMOVED******REMOVED*** ✅ Post-Staging-Checklist

***REMOVED******REMOVED******REMOVED*** Vor Production-Deployment:

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

***REMOVED******REMOVED*** 🎯 Timeline

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

***REMOVED******REMOVED*** 📊 Deployment-Status-Tracking

***REMOVED******REMOVED******REMOVED*** Deployment-Log

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

***REMOVED******REMOVED*** ✅ Sign-Off

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

