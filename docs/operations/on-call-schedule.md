# On-Call Schedule & Incident Response

## 🚨 On-Call-Rotation

### Primary On-Call (24/7)
- **Week 1:** DevOps Lead
- **Week 2:** Backend Lead
- **Week 3:** SRE Engineer 1
- **Week 4:** SRE Engineer 2

### Secondary On-Call (Escalation)
- **Always:** CTO / Engineering Manager

### Business Hours Support (Mo-Fr 8-18 Uhr)
- **CRM Issues:** CRM Team Lead
- **Finance Issues:** Finance Team Lead
- **Inventory Issues:** Inventory Team Lead

---

## 📞 Escalation-Policy

### Level 1 (0-15 Min)
1. Alert wird an Primary On-Call gesendet (PagerDuty)
2. Primary acknowledged Alert innerhalb 5 Min
3. Primary beginnt mit Investigation

### Level 2 (15-30 Min)
1. Wenn nicht acknowledged → Secondary On-Call wird alarmiert
2. Beide arbeiten gemeinsam an Resolution

### Level 3 (30+ Min)
1. Wenn nicht resolved → CTO/Engineering Manager wird informiert
2. War-Room wird einberufen
3. Status-Updates alle 15 Min

---

## 📋 Runbooks

### Runbook 1: High Error Rate (>1%)
**Alert:** `APIErrorRateSLOCritical`

**Schritte:**
1. Check Logs: `kubectl logs -n valeo-erp deployment/valeo-app --tail=100`
2. Check Metrics: Grafana Dashboard "API Overview"
3. Identify Error-Source:
   - Database Connection? → Check PostgreSQL
   - External Service? → Check integrations
   - Code Bug? → Rollback zu last-known-good
4. Mitigate:
   - Scale up Pods (wenn Resource-Issue)
   - Rollback Deployment (wenn neuer Release)
   - Disable Feature-Flag (wenn Feature-Bug)
5. Post-Incident: Create Incident-Report

**Contact:** Backend Team

---

### Runbook 2: Pod OOM-Killed
**Alert:** `PodOOMKilled`

**Schritte:**
1. Check Memory-Usage: `kubectl top pod -n valeo-erp`
2. Identify Memory-Hog:
   - Check Logs für Memory-Leaks
   - Analyze Heap-Dumps (wenn Java/Node.js)
3. Immediate-Fix:
   - Increase Memory-Limit: `kubectl edit deployment valeo-app`
   - Restart Pod: `kubectl rollout restart deployment/valeo-app`
4. Long-term-Fix:
   - Optimize Code
   - Add Memory-Caching-Strategy
   - Implement Pagination

**Contact:** SRE Team

---

### Runbook 3: Database Connection-Pool-Exhaustion
**Alert:** `ConnectionPoolExhaustion`

**Schritte:**
1. Check Pool-Status: `/api/v1/metrics/business`
2. Identify Slow-Queries:
   ```sql
   SELECT * FROM pg_stat_statements
   WHERE mean_exec_time > 1000
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```
3. Mitigate:
   - Increase Pool-Size (temp)
   - Kill Long-Running-Queries
4. Fix:
   - Optimize Slow-Queries
   - Add Indexes
   - Implement Query-Caching

**Contact:** Database Team

---

### Runbook 4: Compliance Violation Rate High
**Alert:** `ComplianceViolationRateHigh`

**Schritte:**
1. Check Compliance-Dashboard: `/admin/compliance`
2. Identify Violation-Source:
   - Check `/api/v1/audit/logs?action=compliance_check`
3. Immediate-Action:
   - Notify Compliance-Officer
   - Block affected Transactions (wenn critical)
4. Long-term:
   - Update Compliance-Rules
   - Train Users
   - Fix Data-Issues

**Contact:** Compliance Team

---

## 🔔 Alert-Severity-Guide

| Severity | Response-Time | Escalation | Example |
|----------|---------------|------------|---------|
| **Critical** | 5 Min | Immediate PagerDuty | API down, Data-Loss, Security-Breach |
| **Warning** | 1 Hour | Slack notification | High Latency, Resource-Pressure |
| **Info** | Next-Business-Day | Email only | Successful Deployments, Backups |

---

## 📞 Contact-Information

### Primary Contacts
- **On-Call Hotline:** +49-XXX-XXXXXXX
- **Slack:** #incidents
- **Email:** oncall@valeo-erp.com

### Team-Specific
- **CRM Team:** crm-team@valeo-erp.com
- **Finance Team:** finance-team@valeo-erp.com
- **SRE Team:** sre@valeo-erp.com
- **Compliance:** compliance@valeo-erp.com

---

## 🛠️ Tools

### Monitoring
- **Grafana:** https://monitoring.valeo-erp.com
- **Prometheus:** https://prometheus.valeo-erp.com
- **AlertManager:** https://alerts.valeo-erp.com

### Logging
- **Loki:** Grafana → Explore → Loki
- **Kubectl:** `kubectl logs -n valeo-erp <pod-name>`

### Tracing
- **Jaeger:** https://tracing.valeo-erp.com (when implemented)

---

## 📝 Post-Incident-Review

Nach jedem P1/P2-Incident:
1. **Incident-Report** erstellen (Template in `/docs/templates/incident-report.md`)
2. **Root-Cause-Analysis** durchführen
3. **Action-Items** definieren & tracken
4. **Team-Meeting** (within 2 days)
5. **Runbook** updaten (lessons learned)

