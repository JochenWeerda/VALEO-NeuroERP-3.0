# VALEO NeuroERP Administrator Guide

## System Administration

### 1. Nummernkreise (Number Ranges)

#### Konfiguration über Environment Variables

```bash
# Sales Orders
SALES_ORDER_PREFIX=SO
SALES_ORDER_START=20250001
SALES_ORDER_DIGITS=8

# Delivery Notes
DELIVERY_PREFIX=DL
DELIVERY_START=20250001
DELIVERY_DIGITS=8

# Invoices
INVOICE_PREFIX=IV
INVOICE_START=20250001
INVOICE_DIGITS=8

# Purchase Orders
PURCHASE_ORDER_PREFIX=PO
PURCHASE_ORDER_START=20250001
PURCHASE_ORDER_DIGITS=8
```

#### Nummernkreis-Verwaltung API

```bash
# Aktuelle Konfiguration abrufen
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.valero.com/api/admin/number-ranges

# Nummernkreis zurücksetzen (VORSICHT!)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "sales", "reset_to": 20250001}' \
  https://erp.valero.com/api/admin/number-ranges/reset
```

#### Nummernkreis-Monitoring

```bash
# Verfügbare Nummern prüfen
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.valero.com/api/admin/number-ranges/status

# Response:
{
  "sales": {
    "current": 20250015,
    "available": 9999985,
    "utilization_percent": 0.0015
  },
  "purchase": {
    "current": 20250008,
    "available": 9999992,
    "utilization_percent": 0.0008
  }
}
```

### 2. Branding und Customization

#### PDF-Branding Konfiguration

```bash
# Logo-Datei (Base64 encoded)
PDF_LOGO_BASE64=iVBORw0KGgoAAAANSUhEUgAA...

# Firmeninformationen
COMPANY_NAME="VALEO GmbH"
COMPANY_STREET="Musterstraße 123"
COMPANY_CITY="80331 München"
COMPANY_COUNTRY="Deutschland"
COMPANY_PHONE="+49 89 123456"
COMPANY_EMAIL="info@valero.com"
COMPANY_WEBSITE="https://www.valero.com"

# Farbschema
PDF_PRIMARY_COLOR="#1f2937"
PDF_SECONDARY_COLOR="#6b7280"
PDF_ACCENT_COLOR="#3b82f6"
```

#### E-Mail Templates

```bash
# SMTP Konfiguration
SMTP_HOST=smtp.valero.com
SMTP_PORT=587
SMTP_USER=neuroerp@valero.com
SMTP_PASSWORD=********
SMTP_TLS=true

# E-Mail Templates
EMAIL_FROM="VALEO NeuroERP <neuroerp@valero.com>"
EMAIL_SIGNATURE="
Mit freundlichen Grüßen
VALEO NeuroERP Team
www.valero.com
"
```

#### UI Customization

```bash
# Theme Konfiguration
THEME_PRIMARY_COLOR="#1f2937"
THEME_SECONDARY_COLOR="#6b7280"
THEME_SUCCESS_COLOR="#10b981"
THEME_WARNING_COLOR="#f59e0b"
THEME_ERROR_COLOR="#ef4444"

# Logo URL
LOGO_URL="/assets/valero-logo.svg"
FAVICON_URL="/assets/valero-favicon.ico"

# Footer Text
FOOTER_TEXT="© 2025 VALEO GmbH - Alle Rechte vorbehalten"
```

### 3. Policy Management

#### Policy-Engine Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alert Input   │───▶│  Policy Engine  │───▶│   Decision      │
│                 │    │                 │    │   Output        │
│ • KPI Metrics   │    │ • Rules Store   │    │                 │
│ • User Context  │    │ • Decision Logic│    │ • Allow/Deny    │
│ • Business Data │    │ • Audit Trail   │    │ • Warnings      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Policy-Regeln definieren

```json
{
  "id": "sales_order_amount_limit",
  "name": "Sales Order Amount Limit",
  "description": "Prüft ob Auftragswert über Limit liegt",
  "priority": 10,
  "conditions": [
    {
      "field": "total",
      "operator": "gt",
      "value": 50000
    },
    {
      "field": "user.role",
      "operator": "neq",
      "value": "manager"
    }
  ],
  "actions": [
    {
      "type": "require_approval",
      "level": "manager"
    },
    {
      "type": "send_notification",
      "recipients": ["controller@valero.com"],
      "message": "Auftrag über 50.000€ erfordert Manager-Freigabe"
    }
  ],
  "enabled": true
}
```

#### Policy-API Verwaltung

```bash
# Alle Policies auflisten
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.valero.com/api/mcp/policy/list

# Neue Policy erstellen
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @policy-rule.json \
  https://erp.valero.com/api/mcp/policy/create

# Policy aktualisieren
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @updated-policy.json \
  https://erp.valero.com/api/mcp/policy/update

# Policy löschen
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "sales_order_amount_limit"}' \
  https://erp.valero.com/api/mcp/policy/delete
```

#### Policy Testing und Simulation

```bash
# Policy gegen Alert testen
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "kpiId": "sales_order_total",
      "value": 75000,
      "user": {"role": "sales", "department": "EMEA"}
    },
    "roles": ["sales"]
  }' \
  https://erp.valero.com/api/mcp/policy/test

# Response:
{
  "ok": true,
  "decision": {
    "type": "require_approval",
    "level": "manager",
    "message": "Auftrag über 50.000€ erfordert Manager-Freigabe"
  }
}
```

#### Policy Audit und Monitoring

```bash
# Policy-Entscheidungen auditieren
curl -H "Authorization: Bearer $TOKEN" \
  "https://erp.valero.com/api/mcp/policy/audit?from=2025-01-01&to=2025-01-31"

# Policy-Performance-Metriken
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.valero.com/api/mcp/policy/metrics

# Response:
{
  "total_decisions": 15420,
  "decisions_by_type": {
    "allow": 14250,
    "deny": 850,
    "require_approval": 320
  },
  "average_response_time_ms": 45.2,
  "error_rate_percent": 0.1
}
```

### 4. Backup und Restore Konfiguration

#### Automatische Backups

```bash
# Backup-Konfiguration
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # Täglich 02:00 UTC
BACKUP_RETENTION_DAYS=30
BACKUP_COMPRESSION=gzip
BACKUP_ENCRYPTION=true

# S3 Storage für Backups
BACKUP_S3_BUCKET=neuroerp-backups-valero
BACKUP_S3_REGION=eu-central-1
BACKUP_S3_ACCESS_KEY=********
BACKUP_S3_SECRET_KEY=********

# Backup-Verifikation
BACKUP_VERIFY_INTEGRITY=true
BACKUP_VERIFY_RESTORABILITY=true
```

#### Backup-Monitoring

```bash
# Backup-Status prüfen
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.valero.com/api/admin/backups/status

# Response:
{
  "last_backup": "2025-01-15T02:00:00Z",
  "status": "success",
  "size_mb": 2450,
  "duration_seconds": 180,
  "next_backup": "2025-01-16T02:00:00Z"
}
```

### 5. Security Konfiguration

#### Role-Based Access Control (RBAC)

```bash
# Rollen-Definitionen
ROLES_CONFIG='{
  "admin": {
    "permissions": ["*"],
    "description": "Vollzugriff auf alle Systemfunktionen"
  },
  "controller": {
    "permissions": [
      "documents:read",
      "documents:approve",
      "export:create",
      "reports:read"
    ],
    "description": "Controller mit Freigabe-Rechten"
  },
  "sales": {
    "permissions": [
      "sales:create",
      "sales:update",
      "sales:submit"
    ],
    "description": "Vertriebsmitarbeiter"
  }
}'
```

#### Audit Logging Konfiguration

```bash
# Audit-Log-Level
AUDIT_LEVEL=detailed  # none, basic, detailed

# Audit-Storage
AUDIT_STORAGE=elasticsearch  # file, database, elasticsearch
AUDIT_ELASTICSEARCH_URL=https://es.valero.com:9200
AUDIT_ELASTICSEARCH_INDEX=neuroerp-audit

# Audit-Retention
AUDIT_RETENTION_DAYS=2555  # ~7 Jahre
AUDIT_COMPRESSION=true
```

### 6. Performance Tuning

#### Database Optimization

```bash
# Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

# Query Optimization
DB_SLOW_QUERY_THRESHOLD_MS=1000
DB_QUERY_CACHE_SIZE=100MB

# Index-Konfiguration
DB_INDEXES='{
  "documents": ["domain", "number", "status", "created_at"],
  "workflows": ["domain", "current_state", "updated_at"],
  "audit": ["timestamp", "user", "action"]
}'
```

#### Cache Konfiguration

```bash
# Redis Cache
REDIS_ENABLED=true
REDIS_URL=redis://redis.valero.com:6379
REDIS_PASSWORD=********

# Cache TTL
CACHE_USER_SESSION_TTL=3600    # 1 Stunde
CACHE_POLICY_DECISIONS_TTL=300 # 5 Minuten
CACHE_DOCUMENT_DATA_TTL=1800   # 30 Minuten
```

### 7. Monitoring und Alerting

#### Prometheus Metrics

```bash
# Application Metrics
METRICS_ENABLED=true
METRICS_PATH=/metrics
METRICS_PORT=9090

# Custom Metrics
WORKFLOW_TRANSITIONS_TOTAL=enabled
POLICY_DECISIONS_TOTAL=enabled
EXPORT_OPERATIONS_TOTAL=enabled
```

#### Alert Rules

```yaml
# Prometheus Alert Rules
groups:
  - name: neuroerp
    rules:
      - alert: NeuroERPDown
        expr: up{job="neuroerp"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "VALEO NeuroERP is down"

      - alert: NeuroERPHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in NeuroERP"

      - alert: NeuroERPWorkflowStale
        expr: rate(workflow_transitions_total[30m]) == 0
        for: 30m
        labels:
          severity: info
        annotations:
          summary: "No workflow transitions in last 30 minutes"
```

### 8. Troubleshooting

#### Häufige Probleme und Lösungen

**Problem**: SSE-Verbindungen funktionieren nicht
```
Lösung:
1. Prüfe Firewall-Einstellungen für Port 443
2. Verifiziere SSL-Zertifikat
3. Prüfe SSE-Hub Logs: kubectl logs -f deployment/neuroerp | grep sse
```

**Problem**: Policy-Engine reagiert langsam
```
Lösung:
1. Prüfe Redis Cache: redis-cli ping
2. Überprüfe Policy-Index: curl /api/mcp/policy/metrics
3. Skaliere Policy-Service: kubectl scale deployment policy-engine --replicas=2
```

**Problem**: Nummernkreis erschöpft
```
Lösung:
1. Prüfe aktuelle Nummer: curl /api/admin/number-ranges/status
2. Erhöhe Range: UPDATE number_ranges SET max_value = max_value + 1000000
3. Benachrichtige Users über neue Range
```

### 9. Maintenance Procedures

#### Monatliche Wartung

```bash
# 1. Log-Rotation
logrotate /etc/logrotate.d/neuroerp

# 2. Database Maintenance
kubectl exec -it deployment/postgres -- vacuumdb --analyze neuroerp

# 3. Cache-Flush (optional)
kubectl exec -it deployment/redis -- redis-cli FLUSHALL

# 4. Backup-Verifikation
kubectl create job backup-verify-$(date +%Y%m%d) --from=cronjob/backup-verify
```

#### Quartalsweise Wartung

```bash
# 1. Security Updates
helm upgrade neuroerp ./charts/neuroerp --set image.tag=latest

# 2. Certificate Rotation
certbot renew --nginx

# 3. Database Reindexing
kubectl exec -it deployment/postgres -- reindexdb neuroerp

# 4. Archive Cleanup
find /data/archives -name "*.pdf" -mtime +2555 -delete
```

#### Jährliche Wartung

```bash
# 1. Full System Audit
# 2. Disaster Recovery Test
# 3. Performance Benchmarking
# 4. Security Assessment
# 5. Documentation Update