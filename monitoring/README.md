# VALEO-NeuroERP Observability Stack

**Prometheus + Grafana + Loki + AlertManager**

---

## 🚀 Quick-Start

### 1. Observability-Stack starten

```bash
cd monitoring

# Docker-Compose starten
docker compose -f docker-compose.observability.yml up -d
```

**Enthält:**
- **Prometheus** (Port 9090) - Metrics-Collection
- **Grafana** (Port 3000) - Visualization
- **Loki** (Port 3100) - Log-Aggregation
- **Promtail** - Log-Shipping
- **AlertManager** (Port 9093) - Alert-Routing

### 2. Services öffnen

**Grafana:**
```
URL: http://localhost:3000
Login: admin / admin
```

**Prometheus:**
```
URL: http://localhost:9090
```

**AlertManager:**
```
URL: http://localhost:9093
```

---

## 📊 Dashboards

### Vorinstallierte Dashboards

1. **VALEO-ERP Overview**
   - API Request Rate
   - Error Rate
   - P95 Latency
   - Workflow Transitions
   - SSE Connections
   - PDF Generation Duration

**Import:**
```bash
# Dashboard ist bereits in grafana/dashboards/valeo-erp.json
# Wird automatisch beim Start geladen
```

### Custom-Dashboards erstellen

1. Grafana öffnen (http://localhost:3000)
2. Dashboard → New Dashboard
3. Add Panel
4. Query: `rate(api_requests_total[5m])`
5. Save Dashboard

---

## 🔔 Alerts

### Vorkonfigurierte Alerts

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| ErrorRateHigh | > 5% | Critical | PagerDuty + Email |
| LatencyHigh | P95 > 500ms | Warning | Slack |
| SSEDisconnectsHigh | > 10/5min | Warning | Slack |
| DatabaseDown | Connection fail | Critical | PagerDuty + Email |
| AuthFailuresHigh | > 5/sec | Critical | Security-Team |
| MemoryUsageHigh | > 90% | Warning | Slack |

### Alert-Konfiguration

**Datei:** `prometheus/alerts.yml`

```yaml
- alert: ErrorRateHigh
  expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High error rate detected"
```

### AlertManager-Konfiguration

**Datei:** `alertmanager/config.yml`

**Receivers:**
- default → Email
- oncall-critical → PagerDuty + Email
- team-warnings → Slack
- security-team → Email + Slack

**Konfiguration:**
```yaml
# ENV-Variablen setzen
export SMTP_PASSWORD=...
export PAGERDUTY_SERVICE_KEY=...
export SLACK_WEBHOOK_URL=...

# AlertManager neustarten
docker compose -f docker-compose.observability.yml restart alertmanager
```

---

## 📝 Logs (Loki)

### Log-Queries in Grafana

1. Grafana → Explore
2. Datasource: Loki
3. Query:

**Alle Errors:**
```logql
{namespace="production"} |= "ERROR"
```

**Workflow-Transitions:**
```logql
{namespace="production"} |= "Workflow transition"
```

**Auth-Failures:**
```logql
{namespace="production"} |= "401" |= "login"
```

**Grouped by Pod:**
```logql
sum by (pod) (rate({namespace="production"}[5m]))
```

### Log-Retention

- **Default:** 30 Tage
- **Konfiguration:** `loki/loki-config.yaml`
- **Ändern:** `retention_period: 720h`

---

## 🔧 Configuration

### Prometheus-Targets

**Datei:** `prometheus/prometheus.yml`

**Vorhandene Targets:**
- valeo-erp:8000/metrics
- prometheus:9090
- alertmanager:9093
- grafana:3000

**Neue Targets hinzufügen:**
```yaml
- job_name: 'mayan-dms'
  static_configs:
    - targets: ['host.docker.internal:8010']
```

### Grafana-Datasources

**Automatisch konfiguriert:**
- Prometheus (http://prometheus:9090)
- Loki (http://loki:3100)

**Manuell hinzufügen:**
1. Grafana → Configuration → Datasources
2. Add Datasource → Prometheus/Loki
3. URL eingeben → Save & Test

---

## 📈 Metrics

### VALEO-ERP Custom-Metrics

**Verfügbar:**
```
# Workflow
workflow_transitions_total{domain, action, status}

# Documents
document_print_duration_seconds{domain}

# SSE
sse_connections_active{channel}

# API
api_requests_total{method, endpoint, status}
api_request_duration_seconds{method, endpoint}
```

### Prometheus-Queries (Beispiele)

**Request Rate:**
```promql
rate(api_requests_total[5m])
```

**Error Rate:**
```promql
rate(api_requests_total{status=~"5.."}[5m])
```

**P95 Latency:**
```promql
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))
```

**SSE Connections:**
```promql
sse_connections_active
```

**Workflow Transitions by Action:**
```promql
sum by (action) (rate(workflow_transitions_total[5m]))
```

---

## 🧪 Testing

### 1. Prometheus erreichbar?

```bash
curl http://localhost:9090/api/v1/targets
# Expected: {"status":"success", "data":{"activeTargets":[...]}}
```

### 2. Grafana erreichbar?

```bash
curl http://localhost:3000/api/health
# Expected: {"database":"ok","version":"..."}
```

### 3. Loki erreichbar?

```bash
curl http://localhost:3100/ready
# Expected: ready
```

### 4. Metrics werden gesammelt?

```bash
curl http://localhost:9090/api/v1/query?query=up
# Expected: {"status":"success","data":{"result":[...]}}
```

### 5. Logs werden gesammelt?

```bash
curl -G http://localhost:3100/loki/api/v1/query \
  --data-urlencode 'query={job="docker"}' \
  --data-urlencode 'limit=10'
# Expected: {"status":"success","data":{"result":[...]}}
```

---

## 📊 Monitoring-Best-Practices

### 1. Dashboard-Organisation

**Erstelle Dashboards für:**
- ✅ API-Overview (Request-Rate, Errors, Latency)
- ✅ Workflow-Metrics (Transitions, Status-Distribution)
- ✅ SSE-Connections (Active, Disconnects, Reconnects)
- ✅ System-Health (CPU, Memory, Disk)
- ✅ Security (Auth-Failures, Rate-Limiting)

### 2. Alert-Routing

**Critical Alerts:**
- ErrorRateHigh → PagerDuty (24/7)
- DatabaseDown → PagerDuty (24/7)
- AuthFailuresHigh → Security-Team

**Warning Alerts:**
- LatencyHigh → Slack (#alerts)
- MemoryUsageHigh → Slack (#alerts)

### 3. Log-Correlation

**Verwende Correlation-IDs:**
```python
# In FastAPI-Middleware
request_id = str(uuid.uuid4())
logger.info(f"Request started", extra={"request_id": request_id})
```

**In Loki-Query:**
```logql
{namespace="production"} |= "request_id=abc123"
```

---

## 🆘 Troubleshooting

### Problem: Prometheus kann VALEO-ERP nicht erreichen

**Lösung:**
```bash
# Check /metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### Problem: Keine Logs in Loki

**Lösung:**
```bash
# Check Promtail
docker compose -f docker-compose.observability.yml logs promtail

# Check Loki
curl http://localhost:3100/ready
```

### Problem: Alerts funktionieren nicht

**Lösung:**
```bash
# Check AlertManager
curl http://localhost:9093/api/v1/status

# Test Alert senden
curl -X POST http://localhost:9093/api/v1/alerts \
  -d '[{"labels":{"alertname":"TestAlert","severity":"warning"}}]'
```

---

## 📞 Production-Deployment

### Kubernetes (via Helm)

```bash
# Install Prometheus-Operator
helm install prometheus-operator prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Install Loki-Stack
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=true
```

### Values.yaml anpassen

```yaml
# k8s/helm/valeo-erp/values.yaml
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

---

## 🎯 Next Steps

1. ✅ **Stack starten:** `docker compose up -d`
2. ✅ **Grafana öffnen:** http://localhost:3000
3. ✅ **Dashboard importieren:** valeo-erp.json
4. ✅ **Alerts konfigurieren:** alertmanager/config.yml
5. ✅ **Test-Alert senden**
6. ✅ **Logs prüfen:** Grafana → Explore → Loki

---

**🎉 Observability-Stack Ready! 📊🔔**

