# Alert Handling Runbook

## Überblick

Dieses Runbook beschreibt die Behandlung von Alerts für VALEO-NeuroERP.

## Alert-Kategorien

### 1. High Error Rate (> 5%)

**Alert:** `ErrorRateHigh`

**Symptom:** API-Error-Rate über 5% in den letzten 5 Minuten

**Ursachen:**
- Database-Connection-Fehler
- Upstream-Service-Ausfall
- Bug in neuem Deployment

**Diagnose:**
```bash
# Check error logs
kubectl logs -n production -l app=valeo-erp --tail=100 | grep ERROR

# Check database connectivity
kubectl exec -n production deploy/valeo-erp -- python -c "from app.core.database_pg import engine; engine.connect()"

# Check metrics
curl https://erp.valeo.example.com/metrics | grep api_requests_total
```

**Mitigation:**
1. Prüfe `/readyz` endpoint
2. Prüfe PostgreSQL-Verbindung
3. Bei Bug: Rollback auf vorherige Version
4. Bei DB-Problem: Prüfe Credentials, Connection-Pool

**Escalation:** Nach 15 Minuten → Team Lead

---

### 2. High Latency (P95 > 500ms)

**Alert:** `LatencyHigh`

**Symptom:** P95-Latenz über 500ms

**Ursachen:**
- Slow Database Queries
- Resource-Limits erreicht
- High Load

**Diagnose:**
```bash
# Check resource usage
kubectl top pods -n production

# Check database slow queries
psql -h $DB_HOST -U $DB_USER -d valeo_erp \
  -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check HPA status
kubectl get hpa -n production
```

**Mitigation:**
1. Scale up replicas: `kubectl scale deployment valeo-erp --replicas=5 -n production`
2. Prüfe Slow Queries und optimiere Indices
3. Erhöhe Resource-Limits falls nötig

**Escalation:** Nach 30 Minuten → Database Team

---

### 3. SSE Disconnections (> 10)

**Alert:** `SSEDisconnectsHigh`

**Symptom:** Mehr als 10 SSE-Disconnects in 5 Minuten

**Ursachen:**
- Pod-Restarts
- Network-Issues
- Load-Balancer-Timeout

**Diagnose:**
```bash
# Check pod restarts
kubectl get pods -n production -l app=valeo-erp

# Check SSE metrics
curl https://erp.valeo.example.com/metrics | grep sse_connections_active

# Check ingress logs
kubectl logs -n ingress-nginx deploy/ingress-nginx-controller --tail=100
```

**Mitigation:**
1. Prüfe Pod-Health
2. Prüfe Ingress-Konfiguration (Timeouts)
3. Prüfe Network-Policies

**Escalation:** Nach 10 Minuten → Platform Team

---

### 4. Database Connection Failures

**Alert:** `DatabaseDown`

**Symptom:** `/readyz` gibt 503 zurück

**Ursachen:**
- PostgreSQL down
- Connection-Pool exhausted
- Network-Partition

**Diagnose:**
```bash
# Check PostgreSQL pod
kubectl get pods -n production -l app=postgresql

# Check PostgreSQL logs
kubectl logs -n production -l app=postgresql --tail=100

# Test connection
psql -h $DB_HOST -U $DB_USER -d valeo_erp -c "SELECT 1;"
```

**Mitigation:**
1. Prüfe PostgreSQL-Pod-Status
2. Restart PostgreSQL falls nötig
3. Prüfe Credentials in Secret
4. Prüfe Connection-Pool-Settings

**Escalation:** IMMEDIATE → Database Team + Platform Team

---

## Alert-Konfiguration (Prometheus)

```yaml
groups:
  - name: valeo-erp-alerts
    interval: 30s
    rules:
      - alert: ErrorRateHigh
        expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      - alert: LatencyHigh
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"
      
      - alert: SSEDisconnectsHigh
        expr: increase(sse_connections_active[5m]) < -10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High SSE disconnect rate"
      
      - alert: DatabaseDown
        expr: up{job="valeo-erp"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
```

## On-Call-Rotation

- **Primary:** Siehe PagerDuty-Schedule
- **Secondary:** Team Lead
- **Escalation:** CTO (nach 1 Stunde)

## Kontakte

- **PagerDuty:** https://valeo.pagerduty.com
- **Slack:** #valeo-erp-alerts
- **Email:** oncall@valeo-erp.com

